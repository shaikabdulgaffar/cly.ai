from django.urls import path
from .views import (
    ChatSessionListCreateView,
    ChatSessionMessagesView,
    ChatMessageCreateView,
)

urlpatterns = [
    path('sessions/', ChatSessionListCreateView.as_view()),
    path('sessions/<int:session_id>/messages/', ChatSessionMessagesView.as_view()),
    path('chat/', ChatMessageCreateView.as_view()),
]