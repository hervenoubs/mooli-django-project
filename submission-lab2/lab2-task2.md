**Lab 2 - Task 2: Building a RAG Pipeline**  
  
  
**1. Objective**  
  
The primary objective of this task is to create an automated ingestion
script that forms the foundation of a Retrieval-Augmented Generation
(RAG) system. This system will ingest a PDF document from an AWS S3
bucket, process its content, and create a searchable knowledge base. The
script will then demonstrate a question-and-answer functionality based
on the ingested data.  
The key components of this pipeline are:

- **Amazon S3**: For scalable storage of the source document (e.g.,
  `PythonAI.pdf`).

- **LangChain**: The framework used to orchestrate the pipeline.

- **AWS Bedrock**: The service providing access to the large language
  model (LLM) and embedding model.

- **FAISS**: A library for efficient vector similarity search, which
  will serve as our knowledge base.  
    
  **2. Prerequisites**  

<!-- -->

- A configured Django project (`the_mooli_project`).

- An active Python virtual environment with all required packages
  installed (e.g., `boto3`, `langchain-community`, `pydantic`,
  `faiss-cpu`, `django-extensions`).

- AWS credentials configured either as environment variables or via the
  AWS CLI.

- An S3 bucket with the PDF file uploaded.

- Access to the Bedrock models (`amazon.titan-embed-text-v1` and
  `anthropic.claude-3-sonnet-20240229-v1:0`) in your AWS account.  
    
  **3. Implementation**  
    
  The script is implemented as a Django management command using the
  `django-extensions` package. The `ingestion_script.py` file is located
  in the `ai_chatbot/scripts/` directory to allow it to be executed
  within the Django environment.  
  The core logic is contained within a `run()` function, which is
  automatically executed by the `runscript` command.  
  **`ai_chatbot/scripts/ingestion_script.py` Breakdown:**

1.  **Environment Setup**: The script imports necessary libraries and
    sets up a logger. It leverages Django\'s `settings` to access
    sensitive information like AWS credentials and model IDs, ensuring
    no hardcoded values.

2.  **`ingest_from_s3` Function**:

    - Connects to AWS S3 using `boto3`.

    - Downloads the PDF file from the specified bucket and key.

    - Uses `PyPDFLoader` from LangChain to read the PDF content.

    - Splits the document into manageable text chunks using
      `RecursiveCharacterTextSplitter`. This is a crucial step for the
      RAG process, as it breaks the document into small, semantically
      meaningful pieces.

<!-- -->

1.  **`create_faiss_index` Function**:

    - Initializes the `BedrockEmbeddings` model
      (`amazon.titan-embed-text-v1`).

    - Generates a **vector embedding** for each text chunk. This process
      converts text into a numerical representation that captures its
      meaning.

    - Builds a **FAISS vector store** from these embeddings. This data
      structure enables fast similarity searches.

    - Saves the resulting `index.faiss` (the vector data) and
      `index.pkl` (the metadata) files locally for later use.

<!-- -->

1.  **`perform_qa_with_rag` Function**:

    - Initializes the LLM using the `BedrockChat` class with the Claude
      3 Sonnet model ID. This class is essential as it is compatible
      with the chat-based API of the Claude v3 family of models, which
      caused a `ValidationError` when the older `Bedrock` class was
      used.

    - Creates a `RetrievalQA` chain that uses the FAISS vector store as
      a retriever. This chain automatically performs the RAG process:
      finding relevant document chunks and using them as context for the
      LLM\'s response.

    - The function runs a sample query and prints the answer to
      demonstrate the system\'s functionality.  
        
      **4. Execution**  
        
      The script is executed from the Django project\'s root
      directory:  
      Bash  
        
      `python3 manage.py runscript ingestion_script`  
      This command ensures the script runs in the correct Django
      environment, resolving any module path issues.  
        
      **5. Outcomes**  
        
      Upon successful execution, the script will:

- Download the PDF from S3.

- Create a local `faiss_index` directory containing `index.faiss` and
  `index.pkl` files.

- Output the answer to the predefined questions, demonstrating the RAG
  pipeline.  
  The task successfully demonstrates the complete workflow of building a
  RAG system from data ingestion to providing a conversational response
  using AWS Bedrock and LangChain.

## Screenshots
- Screenshot: 

## Code Repo
- Repository: 
- Branch: lab2-task2
