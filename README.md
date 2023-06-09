# SuperTokens AI question / answer bot

This project allows a user to ask SuperTokens related questions to the bot. It also allows the user to update the bot's knowledge base by crawling the SuperTokens documentation and discord communication.

## Setup project

### Step 1: Setup env var
Copy `.env.example` and rename it to `.env`. Open the .env file and set:
- `OPEN_AI_KEY`: Your OpenAI API key

### Step 2: Install dependencies and setup knowledge base
```bash
pip install -r requirements.txt
python init.py
```

## Asking questions
```bash
python src/main.py
```

Once you type out a question, press Ctrl-D or Ctrl-Z (windows) in a new line to submit it.

## Updating knowledge base

### Setup env vars:
Open the .env file and set:
- `OPEN_AI_KEY`: Your OpenAI API key
- `DOCUMENTATION_PATH`: The full path to the `v2` folder location of the SuperTokens documentation on your local machine

### Updating docs knowledge base
```bash
python update_docs.py
```

### Updating discord knowledge base
```bash
python update_discord.py
```

# Debugging prompts
Add `DEBUG=true` in the `.env` file

# Adding to test cases
We pick up test cases from our discord channel. To add a thread as a new test case, post the message with the text: `st-bot-test-case`, and all messages up until this one will be added to the test embeddings file.

# Example questions it does not do well at even though the answers are in the docs:
- Code snippets provided are sometimes quite wrong. For example, when querying how to fetch user's profile from google, it replies with the correct answer, but when setting the metadata, it uses `supertokens.setUserMetadata` which doesn't exist.
- When should i use supertokens' metadata recipe vs storing the metadata in my own db?
- Hi how can i get the session id after login ? -> results in it calling createNewSession, and then when prompted after by "No. I mean when the user is logged in, and they make a request from the frontend with a session. How do i get the session id from that request?" -> it returns calling getSession, but with auth-react SDK
- is there any API for healthchecks in supertokens core? -> instead of returning i don't know, it returns with /health
- How can I send a refresh token to the server when I receive a 401 error with the message "try refresh token"? Can you provide some code snippets to help me understand how to do this? -> this gives a full code snippet instead of saying that our frontend interceptors do the refreshing.
- how to do optional protection of route on the frontend?
- I want to log the user out when their subscription is ended. Is there any way I can set custom expiry to cookies and sessions for each user based on their subscription? The default time will be 7 days but users with less than 7 days remaining on their subscription will have the session & cookies expiry date the same as their subscription end date (works with gpt4).
- After signup by EmailPassword when I call POST /auth/signinup/code and passing phonenumber I get Please provide exactly one of email or phoneNumber
- Hi Guys, we have two react apps abc.example.com and xyz.example.com. And these are talking to a single server express app iou.example.com. Our issue is when we login into abc.example.com it automatically changes the cookie value for xyz, and shows it also as logged in. We have also tried adding sessionScope value to an exact domain, but the session is still being shared. 
Is there any way we can restrict this sharing? -> this eventually starts suggesting to use `cookieName` config in session.init, which does not exist
- which version of java does supertokens support -> it gets the right answer, but the hallucination agent thinks it's hallucinating..

# Improvements idea:
- When creating docs chunks, add overlapping between chunks
- Instead of summarizing the question each time, only summarize it when we reach the token limit of the new question + context
- Instead of adding context, fine tune a new model.
- Add real time learning: After every answer, the bot can ask for positive or negative feedback. If positive, the bot can save the question and answer as new embeddings in the knowledge base. If negative feedback, the bot can ask for the correct answer and save that as new embeddings.
- When showing the answer, also show the link to the documentation page where the answer is found.
- Add intercom chat and github issues as a source of knowledge as well.
- If an existing discord thread is updated after it has already been indexed, then the next time we update the knowledge base, it doesn't pick it up from there.
- Add documentation links to answers.
- When it's suggesting code snippets, run it through the docs type checking and keep iterating on it until the type errors are fixed.
- We can create a testing suit which has several questions and answers (source of truth), and then test out different forms of embedding docs by making it generate answers for those questions and then compare the answers with the source of truth. Comparison can be done getting the embeddings of the truthy and generated answers and checking how far away they are.
- Dynamically generate context size based on max_token and length of question (max_token + prompt = max context size).
- Ask the user for which recipe, sdks, custom or pre built UI they are using, and add those to the context for each question to the bot.
- When going through the docs and making it into chunks, break each page into several pages such that each version of the page is specifically for a language / framework. And then save those embeddings for that lang / framework. Then ask the user which lang / sdks / frameworks / recipe they use and only use the relevant docs embeddings.
- Save the question / answer + on right track feedback into it's own file, and then when a question is asked, fetch the answer + feedback that is closest to the question from the file and use those to filter out bad context right from the very start.
- When links are provided in the context, fetch the page and add the text to the context (by summarizing the context along with the contents of the link to create a new context).
- When reasking question, add the previous question and the previous answer as well.
- Do we really need so many chunks of docs (referring to using 500, 1024 and 2048 sizes chunks)
- Build a correction data set. Users who use the bot in debug mode can give the bot correction points based on the answer. The correction points are saved along with the question, answer and correction point (being the context), and then post getting an answer, we can fetch relevant correction points and then run the answer through all of them to make the answers better (some of these can be applied to all answers maybe? Have a way to add that dynamically). Here is an example template for the same:
    ```
    Your job is to correct or rephrase the answer below based on the correct criteria. If the correction criteria doesn't apply to the answer, do NOT change the answer in any way whatsoever, and write back the answer as is.

    =====ANSWER=====
    Yes, the default cookie-based authentication should work properly on all browsers, including Safari, as long as the cookie domain is set to the base domain (mysite.com) and not a subdomain (e.g. api.mysite.com). This will allow the cookie to be shared across all subdomains of mysite.com.

    =====CORRECTION CRITERIA=====
    Whenever referring to cookieDomain and talking about sub domains, if specifying a value for the cookieDomain, make the cookieDomain start with a ".". For example, if saying that the cookieDomain is "example.com", instead say that it is ".example.com". This is because if cookies are to be shared across sub domains, they need to start with a leading "."

    Rephrased answer:
    ```
    OR
    ```
    Your job is to correct or rephrase the answer below based on the correct criteria. If the correction criteria doesn't apply to the answer, do NOT change the answer in any way whatsoever, and write back the answer as is.

    =====ANSWER=====
    According to the conversation,the default cookie-based authentication should work properly on all browsers, including Safari, as long as the cookie domain is set to the base domain (mysite.com) and not a subdomain (e.g. api.mysite.com). This will allow the cookie to be shared across all subdomains of mysite.com.

    =====CORRECTION CRITERIA=====
    Never mention things like according to the conversation, or according to the context. Do not refer to the context in your answer.

    Rephrased answer:
    ```