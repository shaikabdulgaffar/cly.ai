from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from .utils import (
    get_youtube_subtitle_transcript, summarize_with_gemini,
    get_lyrics_and_details, chat_with_gemini
)
import os
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

# Uses environment variables, loaded by settings.py via dotenv
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GENIUS_TOKEN = os.environ.get('GENIUS_TOKEN')

# List/Create chat sessions for sidebar
class ChatSessionListCreateView(generics.ListCreateAPIView):
    queryset = ChatSession.objects.all().order_by('-created_at')
    serializer_class = ChatSessionSerializer

# List messages for a session
class ChatSessionMessagesView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    def get_queryset(self):
        session_id = self.kwargs['session_id']
        return ChatMessage.objects.filter(session_id=session_id).order_by('created_at')

# Send a chat message (and get bot reply)
@method_decorator(csrf_exempt, name='dispatch')
class ChatMessageCreateView(APIView):
    def post(self, request):
        print("POST /api/chat/ called")
        data = request.data
        message = data.get('message')
        history = data.get('history', [])  # <-- Get history from request
        session_id = data.get('session_id')
        user_id = data.get('user_id', 'anonymous')

        # Build context for Gemini
        if history:
            context = ""
            for turn in history:
                if turn['role'] == 'user':
                    context += f"User: {turn['content']}\n"
                elif turn['role'] == 'assistant':
                    context += f"Assistant: {turn['content']}\n"
            prompt = context + f"User: {message}\nAssistant:"
        else:
            prompt = message

        # Command: summarize
        if message.lower().startswith('summarize:'):
            video_url = message.split(':', 1)[1].strip()
            transcript, error = get_youtube_subtitle_transcript(video_url, lang='en')
            if error:
                bot_response = f"Error: {error}"
            else:
                bot_response = summarize_with_gemini(transcript, GEMINI_API_KEY)
        # Command: lyrics
        elif message.lower().startswith('lyrics:'):
            song_title = message.split(':', 1)[1].strip()
            lyrics, song_info, error = get_lyrics_and_details(song_title, GENIUS_TOKEN, GEMINI_API_KEY)
            if error:
                bot_response = f"Error: {error}"
            else:
                bot_response = lyrics  # Only Gemini output, no "More:" link
        # Normal chat
        else:
            bot_response = chat_with_gemini(prompt, GEMINI_API_KEY)

        # Session logic
        if session_id:
            try:
                session = ChatSession.objects.get(pk=session_id)
            except ChatSession.DoesNotExist:
                return Response({"error": "Session not found"}, status=404)
        else:
            session = ChatSession.objects.create(title=message[:40])

        # Save user message
        ChatMessage.objects.create(session=session, sender='user', text=message)
        # Save bot response
        ChatMessage.objects.create(session=session, sender='assistant', text=bot_response)

        return Response({
            "reply": bot_response,
            "session_id": session.id,
        })

# (Optional: Remove or comment out old chatbot_api view)
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# import json
# from .models import ChatHistory
# @csrf_exempt
# def chatbot_api(request):
#     ...