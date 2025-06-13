from django.contrib import admin
from .models import ChatSession, ChatMessage

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender', 'text', 'created_at')
    search_fields = ('text', 'sender')
    ordering = ('-created_at',)