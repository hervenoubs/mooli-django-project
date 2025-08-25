# ai_chatbot/tasks.py

from celery import shared_task
import boto3
import json
import os
import asyncio
from asgiref.sync import async_to_sync
from django.conf import settings
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes, ConversationReference, ChannelAccount
import logging

logger = logging.getLogger(__name__)

boto3_session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("AWS_REGION_NAME"),
)
bedrock_runtime = boto3_session.client('bedrock-runtime')

@shared_task(bind=True)
def process_message(self, request_data):
    """
    Celery task to process incoming messages, generate a response, and send it back.
    This task now handles both Slack and Teams payloads.
    """
    try:
        platform = request_data.get('platform', 'teams')
        
        if platform == 'slack':
            message_text = request_data["event"]["text"]
            channel_id = request_data["event"]["channel"]
            logger.info(f"Task received: process_message for channel {channel_id}, platform {platform}")

        elif platform == 'teams':
            message_text = request_data.get('text', '')
            conversation_id = request_data.get('conversation', {}).get('id')
            logger.info(f"Task received: process_message for channel {conversation_id}, platform {platform}")
        
        system_prompt = "You are a helpful assistant. Respond to this user's message:"
        prompt = f"{system_prompt} {message_text}"
        
        body = json.dumps({
            "messages": [
                {"role": "user", "content": [{"text": prompt, "type": "text"}]}
            ],
            "anthropic_version": "bedrock-2023-05-31",
            "temperature": 0.1,
            "max_tokens": 512,
        })

        logger.debug("Invoking Bedrock model...")
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=settings.BEDROCK_MODEL_ID,
            accept="application/json",
            contentType="application/json",
        )
        logger.debug("Bedrock model invocation successful.")

        response_body = json.loads(response.get("body").read())
        response_text = response_body["content"][0]["text"]
        
        logger.info(f"Generated response: {response_text}")

        if platform == 'slack':
            from slack_bolt import App
            app = App(token=settings.SLACK_BOT_TOKEN)
            try:
                app.client.chat_postMessage(channel=channel_id, text=response_text)
                logger.info("Message successfully sent to Slack.")
            except Exception as e:
                logger.error(f"Failed to send Slack message: {e}", exc_info=True)
                raise

        elif platform == 'teams':
            # Create a simple activity with the necessary data
            activity = Activity.deserialize(request_data)
            
            # Use the activity to get the conversation reference
            teams_reference_object = TurnContext.get_conversation_reference(activity)
            
            async_to_sync(send_teams_message)(teams_reference_object, response_text)

    except Exception as e:
        logger.error(f"An error occurred in process_message: {e}", exc_info=True)

@async_to_sync
async def send_teams_message(teams_reference: ConversationReference, response_text: str):
    try:
        app_id = os.environ.get("TEAMS_APP_ID")
        app_password = os.environ.get("TEAMS_APP_PASSWORD")

        adapter = BotFrameworkAdapter(
            BotFrameworkAdapterSettings(app_id=app_id, app_password=app_password)
        )

        async def send_response(turn_context: TurnContext):
            await turn_context.send_activity(
                Activity(
                    type=ActivityTypes.message,
                    text=response_text
                )
            )

        # The previous logic was an if/else block that both had 'await' calls. 
        # The return from those calls is what caused the NoneType error
        # Let's simplify this by providing the bot_id to continue_conversation
        # as it will be needed for both the emulator and production environments
        # when performing proactive messaging
        
        # Ensure we have a bot_id to send with the proactive message
        if not app_id:
            raise ValueError("TEAMS_APP_ID is not set in environment variables.")

        await adapter.continue_conversation(
            teams_reference,
            send_response,
            bot_id=app_id
        )

    except Exception as e:
        logger.error(f"An error occurred in send_teams_message: {e}")
        # Log the full traceback for debugging
        import traceback
        traceback.print_exc()