# SuperTokens AI question / answer bot

This project allows a user to ask SuperTokens related questions to the bot. It also allows the user to update the bot's knowledge base by crawling the SuperTokens documentation and discord communication.

## Setup project

```bash
pip install -r requirements.txt
python split_or_union_data_files.py
```

## Asking questions
```bash
python main.py
```

Once you type out a question, press Ctrl-D or Ctrl-Z (windows) in a new line to submit it.

## Updating knowledge base

### Setup env vars:
Open the .env file and set:
- `OPEN_AI_KEY`: Your OpenAI API key
- `DOCUMENTATION_PATH`: The full path to the `v2` folder location of the SuperTokens documentation on your local machine

### Updating docs knowledge base
```bash
python main.py --update
```

Once it prompts you to ask a question, you can exit the program and run:

```bash
python split_or_union_data_files.py
```

### Updating discord knowledge base
```bash
python fetch_discord.py
python create_discord_embeddings.py
python split_or_union_data_files.py
```

# Debugging prompts
If you want to see the full prompt that is set to the OpenAI model, you can ask questions like:
```bash
Enter a new question (or type exit) and press Ctrl-D or Ctrl-Z (windows) in a new line to ask:
DEBUG Does supertokens support m2m auth?
```

The `DEBUG` keyword will print the full prompt that is sent to the OpenAI model.

# Example questions it does not do well at even though the answers are in the docs:
- Hi, how to add new OAuth methods to supertokens ? like Steam or Epic Games ? -> gives a lot of information related to being an oauth provider, which is unrelated to the question (but is confused with oauth client vs provider).
- https://discord.com/channels/603466164219281420/644849840475602944/1092010413949997127 -> the issue here is that even though the thread contains the answer, chatGPT doesn't give the answer, instead it continues to talk about the last message in the thread which has little to do with the original question.
- What Server from those 3 are in the best location for germany -> this gives info about the context like "according to the context, the conversation between rp and <user>.. but it's not clear which is the best".

# Improvements idea:
- When creating the context, do it based on the recipe that the user is using. So only search and add the context based on the user's recipes
- Instead of adding context, fine tune a new model instead.
- Add real time learning: After every answer, the bot can ask for positive or negative feedback. If positive, the bot can save the question and answer as new embeddings in the knowledge base. If negative feedback, the bot can ask for the correct answer and save that as new embeddings.
- When showing the answer, also show the link to the documentation page where the answer is found.
- Add intercom chat and github issues as a source of knowledge as well.
- If an existing discord thread is updated after it has already been indexed, then the next time we update the knowledge base, it doesn't pick it up from there.
- Add documentation links to answers