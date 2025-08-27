# Lab 2 Task 1: OpenAI + AWS Bedrock Chatbot

## Setup Instructions
1. Install dependencies: See requirements.txt (django, celery[redis], boto3, llama-index-llms-bedrock, slack-bolt, botbuilder-core, aiohttp).
2. Configure AWS Bedrock (us-east-1, Anthropic Claude 3 Sonnet enabled).
3. Set up Slack app (Event Subscriptions: message.channels, Bot Token Scopes: chat:write, files:read, users:read).
4. Configure Azure Bot (Teams channel, Messaging endpoint: <tunnel-url>/ai_chatbot/teams/webhook/).
5. Run Redis (`redis-server`), Celery (`celery -A the_mooli_project worker --loglevel=info`), Django (`python manage.py runserver`), and Cloudflare Tunnel (`cloudflared tunnel --url http://localhost:8000`).
6. URLs: /ai_chatbot/slack/events/ for Slack, /ai_chatbot/teams/webhook/ for Teams.

## Implementation Notes
- Used Django with Celery for async Bedrock processing.
- Slack integration via slack-bolt, Teams via botbuilder-core (per Adam Johnson blog).
- Fixed 'access_token' error by regenerating TEAMS_APP_PASSWORD and 'bot_id' error by changing testing environment and using bot framework emulator
- CSRF 403 on / ignored (unrelated probe).
- Tested successfully in Slack (DMs to @MooliChatbot) and Teams (Bot Framework Emulator).

## Screenshot
- https://drive.google.com/file/d/1r4nOlRHOis74Ic7VS3QWa276jzZp4cBK/view?usp=sharing 

## Code Repo
- Repository: 
- Branch: lab2-task1
