from django.db import models

class ChatSession(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title or f"Chat {self.pk}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=10)  # 'user' or 'assistant'
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)