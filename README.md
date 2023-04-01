This project allows a user to ask SuperTokens related questions to the bot. It also allows the user to update the bot's knowledge base by crawling the SuperTokens documentation and discord communication.

# How to run

## Install dependencies

```bash
pip install -r requirements.txt
```

## Setup env vars:
Open the .env file and set:
- `OPEN_AI_KEY`: Your OpenAI API key
- `DISCORD_TOKEN`: A discord bot token which can be used to scrape the SuperTokens discord server.
- `DOCUMENTATION_PATH`: The full path to the `v2` folder location of the SuperTokens documentation on your local machine

## Run in read only mode
This will not attempt to update the knowledge base. It will only answer questions based on the knowledge base.

```bash
python main.py
```

## Run in read and write mode
This will attempt to update the knowledge base. It will answer questions based on the knowledge base and also update the knowledge base.

```bash
python main.py --update
```

# Example questions it does not do well at even though the answers are in the docs:
- What is the db schema for mysql?
- Is there any to log out the user if user is idle for 10 mins without?