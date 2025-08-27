from django.urls import path
from .views import slack_events, teams_webhook, root_handler, web_chat, process_chat_message, process_file_upload, get_task_status

urlpatterns = [
    path('', root_handler),  # so POST / doesn’t 403
    path('slack/events/', slack_events, name='slack_events'),
    path('teams/webhook/', teams_webhook, name='teams_webhook'),
    path('chat/', web_chat, name='web_chat'),
    path('api/chat/', process_chat_message, name='process_chat_message'),
    path('api/upload/', process_file_upload, name='process_file_upload'),
    path('api/task-status/', get_task_status, name='get_task_status'),
]