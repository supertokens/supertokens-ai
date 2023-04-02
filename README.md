This project allows a user to ask SuperTokens related questions to the bot. It also allows the user to update the bot's knowledge base by crawling the SuperTokens documentation and discord communication.

# How to run

## Install dependencies

```bash
pip install -r requirements.txt
```

## Setup env vars:
Open the .env file and set:
- `OPEN_AI_KEY`: Your OpenAI API key
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

# Debugging prompts
If you want to see the full prompt that is set to the OpenAI model, you can ask questions like:
```bash
Enter a question (or type exit): DEBUG what is apiGatewayPath in appInfo?
```

The `DEBUG` keyword will print the full prompt that is sent to the OpenAI model.

# Example questions it does not do well at even though the answers are in the docs:
- What is the db schema for mysql?
- Hi, how to add new OAuth methods to supertokens ? like Steam or Epic Games ?

# Improvements idea:
- When creating the context, do it based on the recipe that the user is using. So only search and add the context based on the user's recipes
- Instead of adding context, fine tune a new model instead.
- Add real time learning: After every answer, the bot can ask for positive or negative feedback. If positive, the bot can save the question and answer as new embeddings in the knowledge base. If negative feedback, the bot can ask for the correct answer and save that as new embeddings.
- When showing the answer, also show the link to the documentation page where the answer is found.
- Allow for multiline input.