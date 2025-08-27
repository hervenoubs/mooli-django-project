# ai_chatbot/scripts/ingestion_script.py

def run():
    
    import boto3
    import os
    from io import BytesIO
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_community.embeddings.bedrock import BedrockEmbeddings
    from langchain_community.vectorstores import FAISS
    # Change the import here to BedrockChat
    from langchain_community.chat_models import BedrockChat
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.chains import RetrievalQA
    from django.conf import settings
    import logging

    # Define the logger here, inside the run() function
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    # Now you can access settings directly
    llm_model_id = settings.BEDROCK_MODEL_ID
    embedding_model_id = "amazon.titan-embed-text-v1"

    # Define the Bedrock client once
    bedrock_runtime = boto3.client('bedrock-runtime',
        region_name=settings.AWS_REGION_NAME
    )

    def ingest_from_s3(bucket_name, file_key):
        """
        Downloads a file from S3, loads it, and splits it into chunks.
        """
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
        """
        Creates a FAISS index from document chunks and saves it locally.
        """
        if not documents:
            logger.error("No documents to process. Aborting index creation.")
            return None
            
        logger.info("Creating embeddings and building FAISS index...")
        embeddings = BedrockEmbeddings(client=bedrock_runtime, model_id=embedding_model_id)
        vector_store = FAISS.from_documents(documents, embeddings)
        vector_store.save_local(index_name)
        logger.info(f"FAISS index saved to '{index_name}' directory.")
        return vector_store

    def perform_qa_with_rag(vector_store, query):
        """
        Performs a Q&A using the RAG pipeline.
        """
        if not vector_store:
            logger.error("No vector store provided for Q&A.")
            return "An error occurred. The knowledge base is not available."
            
        logger.info(f"Processing query: '{query}'")
        # Change this line to use BedrockChat
        llm = BedrockChat(client=bedrock_runtime, model_id=llm_model_id)
        
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 3})
        )
        
        response = qa.run(query)
        return response

    # --- Execution Logic ---
    S3_BUCKET_NAME = settings.S3_BUCKET_NAME
    S3_FILE_KEY = "uploads/PythonAI.pdf"
    
    documents = ingest_from_s3(S3_BUCKET_NAME, S3_FILE_KEY)
    if documents:
        vector_store = create_faiss_index(documents)
        
        if vector_store:
            # --- Demonstrate Q&A ---
            query = "What are the key technical proficiencies assessed in this test?"
            answer = perform_qa_with_rag(vector_store, query)
            print("\n--- Question and Answer Demonstration ---")
            print(f"Question: {query}")
            print(f"Answer: {answer}")
            print("---------------------------------------")
            
            # --- Demonstrate summarization ---
            summary_query = "Summarize the key objectives of this test."
            summary_answer = perform_qa_with_rag(vector_store, summary_query)
            print("\n--- Summarization Demonstration ---")
            print(f"Question: {summary_query}")
            print(f"Summary: {summary_answer}")
            print("---------------------------------------")