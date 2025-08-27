import boto3
import os
from io import BytesIO
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from langchain_community.chat_models import BedrockChat
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain.agents import Tool, create_react_agent, AgentExecutor
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Define the Bedrock client once for all functions in this module
bedrock_runtime = boto3.client('bedrock-runtime',
    region_name=settings.AWS_REGION_NAME
)

def ingest_from_s3(bucket_name, file_key):
    # This is your existing function from Task 2
    s3_client = boto3.client('s3')
    try:
        logger.info(f"Downloading {file_key} from S3 bucket {bucket_name}...")
        file_stream = BytesIO()
        s3_client.download_fileobj(bucket_name, file_key, file_stream)
        file_stream.seek(0)
        
        temp_file_path = f"/tmp/{os.path.basename(file_key)}"
        with open(temp_file_path, "wb") as f:
            f.write(file_stream.read())
        
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        docs = text_splitter.split_documents(documents)
        logger.info(f"Split document into {len(docs)} chunks.")
        
        os.remove(temp_file_path)
        
        return docs
    except Exception as e:
        logger.error(f"Error ingesting file from S3: {e}")
        return []


def create_faiss_index(documents, index_name="faiss_index"):
    # This is your existing function from Task 2
    # No changes are needed here
    # ... (paste the full code for this function)
    if not documents:
        logger.error("No documents to process. Aborting index creation.")
        return None
        
    logger.info("Creating embeddings and building FAISS index...")
    embeddings = BedrockEmbeddings(client=bedrock_runtime, model_id="amazon.titan-embed-text-v1")
    vector_store = FAISS.from_documents(documents, embeddings)
    vector_store.save_local(index_name)
    logger.info(f"FAISS index saved to '{index_name}' directory.")
    return vector_store


def perform_qa_with_rag(query):
    """
    Performs a Q&A using the RAG pipeline.
    This function is slightly modified to take only the query as input,
    as required by the Tool class. It will load the index itself.
    """
    index_name = "faiss_index"
    if not os.path.exists(index_name):
        # If the index doesn't exist, try to build it first.
        S3_BUCKET_NAME = settings.S3_BUCKET_NAME
        S3_FILE_KEY = "uploads/PythonAI.pdf"
        documents = ingest_from_s3(S3_BUCKET_NAME, S3_FILE_KEY)
        vector_store = create_faiss_index(documents, index_name)
    else:
        # Load the existing index
        embeddings = BedrockEmbeddings(client=bedrock_runtime, model_id="amazon.titan-embed-text-v1")
        vector_store = FAISS.load_local(index_name, embeddings, allow_dangerous_deserialization=True)
        
    if not vector_store:
        logger.error("No vector store provided for Q&A.")
        return "An error occurred. The knowledge base is not available."
        
    logger.info(f"Processing query with RAG: '{query}'")
    llm = BedrockChat(client=bedrock_runtime, model_id=settings.BEDROCK_MODEL_ID)
    
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3})
    )
    
    response = qa.run(query)
    return response

def process_file_upload(file_path):
    """
    A tool to handle file uploads.
    It will trigger a background task to process the file.
    """
    from .tasks import process_uploaded_file
    
    # Pass only the file_path to the Celery task.
    task = process_uploaded_file.delay(file_path)
    
    # Return the Celery task object
    return task

# Now, we define the tools the agent will use
agent_tools = [
    Tool(
        name="DocumentQA",
        func=perform_qa_with_rag,
        description="""Useful for answering questions or summarizing content from the pre-processed
        'PythonAI.pdf' document. Input should be a specific question or a command like
        'summarize the document'. Always use this tool for any questions about the
        content of the document."""
    ),
    Tool(
        name="FileUploader",
        func=process_file_upload,
        description="""Useful for handling a user's request to upload or process a new file.
        Input should be the file's path. Use this tool only when the user explicitly mentions
        uploading or processing a new document."""
    )
]

# The agent creation logic

# Define the LLM for the agent
llm = BedrockChat(client=bedrock_runtime, model_id=settings.BEDROCK_MODEL_ID)

# Define a custom prompt for the agent to guide its behavior.
# This prompt tells the agent what its purpose is and what tools it has.
prompt_template = PromptTemplate.from_template("""
You are a helpful and intelligent chatbot named Mooli. Your purpose is to assist users with two main tasks:
1. Answering questions about the 'PythonAI.pdf' document.
2. Handling new PDF file uploads for future processing.

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer.
Thought: you should always think about what to do.
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action, MUST be a string.
Observation: the result of the action.
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer.
Final Answer: the final answer to the original input question.

Begin!

Question: {input}
Thought:{agent_scratchpad}
""")

# Create the agent executor. This is the main runnable object.
agent = create_react_agent(
    tools=agent_tools, # The list of tools from Part 1
    llm=llm,
    prompt=prompt_template,
)

# The AgentExecutor is responsible for running the agent with the provided tools.
agent_executor = AgentExecutor(
    agent=agent, 
    tools=agent_tools, 
    verbose=True, 
    handle_parsing_errors=True
)

def run_agent_task(user_input, file_path=None):
    """
    The main function to run the agent.
    It takes user input and an optional file path.
    """
    logger.info(f"Received request: '{user_input}' with file_path: '{file_path}'")

    # If a file is uploaded, we will force the agent to use the FileUploader tool
    if file_path:
        # Now this call returns the Celery task object
        return process_file_upload(file_path)
    
    # Otherwise, let the agent reason and decide which tool to use
    try:
        response = agent_executor.invoke({"input": user_input})
        return response.get('output', "I am unable to process that request at this time.")
    except Exception as e:
        logger.error(f"Error in agent execution: {e}")
        return "I apologize, but an error occurred while processing your request."
