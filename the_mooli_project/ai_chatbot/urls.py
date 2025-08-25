from django.urls import path
from .views import slack_events, teams_webhook, root_handler

urlpatterns = [
    path('', root_handler),  # so POST / doesn’t 403
    path('slack/events/', slack_events, name='slack_events'),
    path('teams/webhook/', teams_webhook, name='teams_webhook'),
]