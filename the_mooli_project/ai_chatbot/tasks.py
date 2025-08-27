from celery import shared_task
import boto3
import json
import os
import asyncio
from django.conf import settings
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes, ConversationReference
from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.llms.bedrock import Bedrock
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.readers.file import PDFReader
import faiss
import logging
import tempfile
import re

from io import BytesIO
# Import my existing functions from agent_tools.py
from ai_chatbot.agent_tools import ingest_from_s3, create_faiss_index
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

boto3_session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("AWS_REGION_NAME", "us-east-1"),
)
bedrock_runtime = boto3_session.client('bedrock-runtime')

@shared_task(bind=True)
def process_message(self, request_data):
    """
    Celery task to process messages, generate a response using RAG with FAISS, and send it back.
    Handles Slack and Teams payloads with specific S3 file indexing.
    """
    try:
        platform = request_data.get('platform', 'teams')
        channel_id = None
        conversation_id = None
        message_text = ""
        
        logger.info(f"Request data received: {json.dumps(request_data, indent=2)}")
        
        if platform == 'slack':
            message_text = request_data.get("event", {}).get("text", "")
            channel_id = request_data.get("event", {}).get("channel", "unknown")
            logger.info(f"Task received: process_message for channel {channel_id}, platform {platform}, message: {message_text}")
        elif platform == 'teams':
            message_text = request_data.get('text', '')
            conversation_id = request_data.get('conversation', {}).get('id', 'unknown')
            logger.info(f"Task received: process_message for channel {conversation_id}, platform {platform}, message: {message_text}")
        
        # Skip empty messages
        if not message_text.strip():
            response_text = "Please provide a valid message."
            send_response(platform, request_data, channel_id, conversation_id, response_text)
            return
        
        # Extract file name and query type
        file_match = re.search(r'PythonAI\.pdf|pythonai\.pdf', message_text, re.IGNORECASE)
        summarize_match = re.search(r'summarize', message_text, re.IGNORECASE)
        file_key = "uploads/PythonAI.pdf" if file_match else None
        
        if not file_key:
            response_text = "Please include 'PythonAI.pdf' in your message (e.g., 'Query PythonAI.pdf about X')."
            send_response(platform, request_data, channel_id, conversation_id, response_text)
            return
        
        # Initialize Bedrock LLM and Embedding
        llm = Bedrock(
            model="anthropic.claude-3-sonnet-20240229-v1:0",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name="us-east-1"
        )
        embed_model = BedrockEmbedding(
            model="amazon.titan-embed-text-v1",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name="us-east-1"
        )
        
        # Set ServiceContext to ensure Bedrock
        service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)
        
        # Initialize FAISS vector store
        faiss_index = faiss.IndexFlatL2(1536)
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        
        # Use boto3 directly to download the file instead of S3Reader
        s3_client = boto3_session.client('s3')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            try:
                # Download the file from S3
                s3_client.download_fileobj(settings.S3_BUCKET_NAME, file_key, tmp_file)
                tmp_file.flush()
                
                # Use PDFReader to load the document
                pdf_reader = PDFReader()
                documents = pdf_reader.load_data(tmp_file.name)
                
                if not documents:
                    response_text = f"File {file_key} is empty or could not be read."
                    send_response(platform, request_data, channel_id, conversation_id, response_text)
                    return
                    
                # Index documents with FAISS
                index = VectorStoreIndex.from_documents(
                    documents, 
                    vector_store=vector_store, 
                    embed_model=embed_model, 
                    service_context=service_context
                )
                
                if summarize_match:
                    query_engine = index.as_query_engine(response_mode="compact")
                    response = query_engine.query("Provide a concise summary of the document.")
                    response_text = f"Summary of PythonAI.pdf:\n{str(response)}"
                else:
                    query_engine = index.as_query_engine()
                    response = query_engine.query(message_text)
                    response_text = str(response)
                    
            except Exception as e:
                logger.error(f"Error processing file from S3: {e}", exc_info=True)
                response_text = f"Error processing file {file_key}: {str(e)}"
                send_response(platform, request_data, channel_id, conversation_id, response_text)
                return
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass
        
        logger.info(f"Generated response: {response_text}")
        send_response(platform, request_data, channel_id, conversation_id, response_text)

    except Exception as e:
        logger.error(f"Error in process_message: {e}", exc_info=True)
        response_text = f"Sorry, an error occurred: {str(e)}"
        send_response(platform, request_data, channel_id, conversation_id, response_text)

def send_response(platform, request_data, channel_id, conversation_id, response_text):
    if platform == 'slack' and channel_id and channel_id != "unknown":
        try:
            from slack_bolt import App
            app = App(token=settings.SLACK_BOT_TOKEN)
            app.client.chat_postMessage(channel=channel_id, text=response_text)
            logger.info("Message sent to Slack.")
        except Exception as e:
            logger.error(f"Error sending Slack response: {e}", exc_info=True)
    elif platform == 'teams':
        try:
            activity = Activity.deserialize(request_data)
            teams_reference = TurnContext.get_conversation_reference(activity)
            if teams_reference is None or not hasattr(teams_reference, 'conversation') or not teams_reference.conversation:
                logger.error(f"Invalid teams_reference: {teams_reference}")
                return
            asyncio.run(send_teams_message(teams_reference, response_text))
        except Exception as e:
            logger.error(f"Error processing Teams activity: {e}", exc_info=True)

async def send_teams_message(teams_reference: ConversationReference, response_text: str):
    try:
        app_id = os.environ.get("TEAMS_APP_ID")
        app_password = os.environ.get("TEAMS_APP_PASSWORD")
        if not app_id or not app_password:
            raise ValueError("TEAMS_APP_ID or TEAMS_APP_PASSWORD not set.")
        
        adapter = BotFrameworkAdapter(
            BotFrameworkAdapterSettings(app_id=app_id, app_password=app_password)
        )

        async def send_response(turn_context: TurnContext):
            if turn_context is None:
                logger.error("TurnContext is None")
                return
            await turn_context.send_activity(
                Activity(
                    type=ActivityTypes.message,
                    text=response_text
                )
            )

        await adapter.continue_conversation(
            teams_reference,
            send_response,
            bot_id=app_id
        )
        logger.info("Message sent to Teams.")
    except Exception as e:
        logger.error(f"Error in send_teams_message: {e}", exc_info=True)
        raise

def ingest_from_temp_file(file_path):
    """
    Loads a PDF from a temporary file path, splits it, and returns document chunks.
    This is an adaptation of your original ingest_from_s3 function.
    """
    try:
        logger.info(f"Loading {file_path} for ingestion...")
        
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        docs = text_splitter.split_documents(documents)
        logger.info(f"Split document into {len(docs)} chunks.")
        
        # Optionally, you can now upload this to S3 for permanent storage if needed
        s3_client = boto3.client('s3')
        s3_file_key = f"uploads/{os.path.basename(file_path)}"
        s3_client.upload_file(file_path, settings.S3_BUCKET_NAME, s3_file_key)
        logger.info(f"File uploaded to S3 at: {s3_file_key}")
        
        return docs
    except Exception as e:
        logger.error(f"Error ingesting file from temp path: {e}")
        return []

@shared_task(bind=True)
def process_uploaded_file(self, file_path):
    """
    Celery task to handle the ingestion of an uploaded file in the background.
    """
    try:
        filename = os.path.basename(file_path)
        logger.info(f"Starting Celery task to process file: {filename} at path: {file_path}")
        
        # 1. Ingest the document from the temporary file path
        documents = ingest_from_temp_file(file_path)

        if not documents:
            logger.error(f"No documents were created from the uploaded file: {filename}.")
            return "Failed to process file."

        # 2. Create the FAISS index from the new documents
        vector_store = create_faiss_index(documents)

        if vector_store:
            logger.info(f"File {filename} successfully processed and FAISS index created.")
            # Clean up the temporary file after processing is complete
            os.remove(file_path)
            return f"File {filename} successfully processed and indexed."
        else:
            logger.error("FAISS index creation failed.")
            return "Failed to create knowledge base from file."

    except Exception as e:
        logger.error(f"An unexpected error occurred during file processing: {filename}: {e}")
        return f"Failed to process file {filename}."