from rest_framework import serializers
from .models import ChatSession, ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ('id', 'sender', 'text', 'created_at')

class ChatSessionSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    class Meta:
        model = ChatSession
        fields = ('id', 'title', 'created_at', 'last_message')
    def get_last_message(self, obj):
        last = obj.messages.order_by('-created_at').first()
        return last.text if last else ""