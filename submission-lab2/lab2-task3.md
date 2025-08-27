**Lab 2 - Task 3: Adding an Agentic Task**  
  
  
**1. Objective**  
  
The goal of this task is to enhance the AI chatbot by implementing an
**intelligent agent** capable of performing multi-step, tool-based
tasks. Unlike the previous RAG pipeline, which followed a rigid
sequence, this agent can dynamically choose the best **tool** to fulfill
a user\'s request. This provides a more flexible and robust
conversational experience. The two primary tasks the agent must handle
are:

1.  **Answering questions** based on the ingested `PythonAI.pdf`
    document (using the RAG pipeline as a tool).

2.  **Handling new file uploads** by triggering a background processing
    task.  
      
      
    **2. Implementation Details**  
      
    The solution is implemented by leveraging **LangChain\'s agentic
    framework** and integrating it with a **Celery task queue** within
    your Django project. This ensures long-running operations like
    document ingestion don\'t block the main web server, providing a
    responsive user experience.  
    The implementation is broken down into four logical parts:  
    **Part 1: Defining the Agent\'s Tools**

- **Purpose**: To make the agent aware of the specific actions it can
  perform.

- **Code Location**: `ai_chatbot/agent_tools.py`

- **Key Components**:

  - `DocumentQA`: A **LangChain Tool** that wraps your existing
    `perform_qa_with_rag` function. The agent will use this tool when it
    determines a user\'s request is a question about the pre-processed
    document. The tool\'s `description` is crucial as it tells the LLM
    when to use it.

  - `FileUploader`: A new tool that handles the file upload logic.
    Instead of performing the file ingestion directly, this tool\'s
    function triggers a **Celery task**, which runs in the background.
    It returns the Celery **`Task` object** so its status can be
    tracked.  
    **Part 2: Initializing the Agent Logic**

<!-- -->

- **Purpose**: To create the central decision-making engine of the
  chatbot.

- **Code Location**: `ai_chatbot/agent_tools.py`

- **Key Components**:

  - **Agent Prompt**: A custom `PromptTemplate` that guides the LLM on
    how to behave. It defines the agent\'s persona and explains the
    purpose of each available tool. This prompt is essential for the
    agent\'s reasoning process (the \"Thought,\" \"Action,\" and \"Final
    Answer\" sequence).

  - **Agent Creation**: The `create_react_agent` function combines the
    LLM, the defined tools, and the custom prompt to build the agent.
    The ReAct (Reasoning and Acting) framework allows the agent to
    reason about the best course of action before performing it.

  - **Agent Executor**: The `AgentExecutor` is the final object that
    runs the agent and its tools. It handles the entire reasoning loop,
    invoking the correct tool based on the user\'s input. The
    `verbose=True` flag is invaluable for debugging, as it prints the
    agent\'s internal thought process to the terminal.

  - `run_agent_task` function: A simple wrapper function that serves as
    a public API for the agent. It takes a user\'s message and, if
    applicable, a file path. When a file is uploaded, it directly
    returns the Celery `Task` object.  
    **Part 3: Django and Celery Integration**

<!-- -->

- **Purpose**: To connect the web interface to the backend agent and
  offload heavy tasks.

- **Code Location**: `ai_chatbot/views.py` and `ai_chatbot/tasks.py`

- **Key Components**:

  - **`process_chat_message` View**: This view receives a user\'s text
    input from the web page via an AJAX POST request. It then passes the
    message directly to the `run_agent_task` function and returns the
    agent\'s response as a JSON object.

  - **`process_file_upload` View**: This view handles file uploads.
    Instead of processing the file immediately, it saves it to a
    temporary location. It then calls `run_agent_task`, which returns a
    **Celery `Task` object**. The view then returns the `task_id` in a
    JSON response so the client can track its status.

  - **Celery Task**: A `@shared_task` decorated function in
    `ai_chatbot/tasks.py` is responsible for performing the actual file
    ingestion and index creation. This happens asynchronously,
    independent of the user\'s web session.  
    **Part 4: Asynchronous Feedback via Polling**

<!-- -->

- **Purpose**: To inform the user when the background task is complete.

- **Code Location**: `web_chat.html` and `ai_chatbot/views.py`

- **Key Components**:

  - **`get_task_status` View**: A new Django view that takes a `task_id`
    and checks the status of the corresponding Celery task using
    `celery.result.AsyncResult`. It returns a JSON response with the
    current status (e.g., `PENDING`, `SUCCESS`, `FAILURE`).

  - **Client-side Polling**: The JavaScript code in `web_chat.html` now
    only starts a polling loop (`setInterval`) after a file upload. This
    loop periodically sends an AJAX request to the `get_task_status`
    view. When the status changes to `SUCCESS` or `FAILURE`, the loop is
    cleared, and the final message is displayed to the user.  
      
      
    **3. Expected Outcomes**  

<!-- -->

- When a user asks a question about the PDF document, the agent will
  recognize the intent and use the `DocumentQA` tool to provide a
  correct answer.

- When a user uploads a new PDF file, the agent will use the
  `FileUploader` tool and provide an immediate confirmation message.
  After a short delay, a second message will appear confirming the
  successful completion of the background processing task.

## Screenshots
https://drive.google.com/file/d/13ZndLCHsjhmnfbEZvT8DqEQpnxJ64uRD/view?usp=sharing 

## Code Repo
- Repository: 
- Branch: lab2-task3
