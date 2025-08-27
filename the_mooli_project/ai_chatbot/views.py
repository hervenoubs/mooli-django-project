import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import json
import os
from .tasks import process_message
from .agent_tools import run_agent_task
from celery.result import AsyncResult

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

# Teams Setup
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

# Web agentic chat Setup
def web_chat(request):
    """Render the main chat page."""
    return render(request, 'web_chat.html')

@csrf_exempt
@require_POST
def process_chat_message(request):
    """Handle chat messages by passing them to the agent."""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'message': 'Please enter a valid message.'}, status=400)
            
        bot_response = run_agent_task(user_message)
        
        return JsonResponse({'message': bot_response})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

@csrf_exempt
@require_POST
def process_file_upload(request):
    """Handle file uploads."""
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'message': 'No file was uploaded.'}, status=400)
    
    # Save the file to a temporary location for the agent to process
    temp_dir = 'temp_uploads'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
            
    # Trigger the agent's file processing logic
    # This now returns the Celery task object
    task = run_agent_task("process file upload", file_path=file_path)
    
    # Get the task ID from the object
    task_id = task.id
    
    return JsonResponse({
        'message': f"File {uploaded_file.name} uploaded successfully. Processing will begin shortly.",
        'task_id': task_id
    })

def get_task_status(request):
    task_id = request.GET.get('task_id')
    if not task_id:
        return JsonResponse({'status': 'invalid_id'}, status=400)
    
    task_result = AsyncResult(task_id)
    
    # Celery task states: PENDING, STARTED, SUCCESS, FAILURE, RETRY
    if task_result.state == 'SUCCESS':
        return JsonResponse({'status': 'SUCCESS', 'result': task_result.result})
    elif task_result.state == 'FAILURE':
        return JsonResponse({'status': 'FAILURE', 'result': str(task_result.result)})
    else:
        return JsonResponse({'status': task_result.state})