import logging
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from .tasks import process_message

# Slack specific imports
from slack_bolt import App
from slack_bolt.adapter.django import SlackRequestHandler

logger = logging.getLogger(__name__)

@csrf_exempt
def root_handler(request):
    if request.method == "POST":
        return JsonResponse({"status": "ignored"}, status=200)
    return JsonResponse({"message": "OK"}, status=200)

# Slack Setup
slack_app = App(
    token=settings.SLACK_BOT_TOKEN,
    signing_secret=settings.SLACK_SIGNING_SECRET
)
slack_handler = SlackRequestHandler(slack_app)

@csrf_exempt
def slack_events(request):
    """
    Handles Slack events. The SlackRequestHandler manages the CSRF exemption
    and event dispatching automatically, including the URL verification challenge.
    """
    return slack_handler.handle(request)

@slack_app.event("message")
def handle_message(event, say):
    """
    Handles incoming Slack messages.
    """
    if "bot_id" in event or event.get("subtype") == "bot_message":
        return 
    say(":wave: Got it! Working on that now...")
    process_message.delay({"event": event, "platform": "slack"})


@csrf_exempt
def teams_webhook(request):
    """
    Handles incoming Teams webhook messages.
    """
    try:
        if request.method == "POST":
            request_data = json.loads(request.body)
            
            # Pass the entire, raw payload to the Celery task.
            # The task will handle parsing it and getting the conversation reference.
            process_message.delay(request_data)
            
            logger.info("Task successfully queued. Returning 200 OK.")
            return JsonResponse({"status": "ok"}, status=200)

        return JsonResponse({"error": "Method not allowed"}, status=405)

    except Exception as e:
        logger.error(f"An error occurred in the Teams webhook view: {e}", exc_info=True)
        return JsonResponse({"error": "An internal error occurred"}, status=500)