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

## Testing methodology:

The idea is to test per prompt. A prompt has the following types:
- Fixed Template: This is the hardcoded part prompt given to the llm.
- Variables:
    - Derived variables: These are variables that are non user input, but are derived based on the user input.
    - User input variables: This is the user input string.
- Response:
    - Free form: Response that is free form language.
    - Fixed structure: Responses that are input to other program code flow. It can be a json, or a "yes" or "no" etc.. essentially these are not user facing response.
    - Composite: This is a response that is a combination of free form and fixed structure. For example, a json that has a free form string in it which is displayed to the user, and a boolean value used to continue the code flow.
- Model used

### Changes in the prompt:

From the above, whilst in development, any of the above can change:
- Fixed template change: 
    - In this case, we will take all the previously seen user and derived input and run it through the new prompt and evaluate the response.
- Derived variable change:
    - In this case, we will take all the previously seen user input and prompt and run it through the new derived variables and evaluate the response.
    - Derived variable names must have a fixed key in the template.
    - Derived variable changes mean that the new derived variables must be fetched from somewhere, so we need to allow the user to provide a function that will return the new derived variables for a given user input.
- User input change:
    - Since these are user inputs, we don't really need to test changes in them.
- Model used:
    - In this case, we will take all the previous prompts, user input, derived variables and run it through the new model and evaluate the response.

### Evaluation of the response:
In general, we can define response evaluators some args returns a boolean saying passed or not.

- String response:
    - The input will be two strings.
    - We can use LLM to ask if the responses are similar in meaning, and if not, we return an error.
    - Or we can do string comparison.
- Fixed structure response:
    - The input will be two strings and a structure type (containing the type structure and the validators for each of the fields.).
    - We can ask the user to define a structure type for this:
        - boolean
        - number
        - string
        - JSON with these fields and their data types
    - Strings will be evaluated based on string response
- Custom response validators:
    - These can be used for example to know if the resulting code is valid or not from a types point of view. The user will have to define this on their own.

The key point is that these are all just functions that can be used defined or pre built.

Once the evaluator has run, we will check if the test case is a positive or not for that particular (part of the) response, and if the test case is positive, then we must make sure that the response is "similar" to the test case response, else we must make sure that the response is "not similar" to the test case.

Example definition of response structure:
```
jsonChecker({
    type: "json",
    fields: {
        "name": {
            type: "string",
            validator: (actual, expected) => {
                return actual === expected
            }
        },
        "age": {
            type: "number",
            validator: (actual, expected) => {
                return value === expected
            }
        },
        "description": {
            type: "string",
            validator: llmSimilarityChecker
        }
    }
})(actual, expected)
```
- In this case, the `llmSimilarityChecker` is a pre defined checker which prompts an LLM to check if the actual and expected are similar or not.

### Collection of testing data:
When each time an LLM is used, we can save the input template, variables etc and also save the response. All this will be then saved in a db. The user can then later on go through that and mark the output as valid or not for each of the use cases.

It's important to note that each part of a response must be marked as good or bad (based on the response structure).

This requires the user to define the response structure for each prompt which tallies with the response structure given to the response validator as well.

The data is stored against the current template.

### Storage of testing data:

For each prompt, we must store:
- The template
    - The keys in the template (variable place holders) must be in a special format in the template so tat we can identify their positions.
- The derived variables:
    - Key of the variable
    - Value of the variable
- The user input
- model used
- Response:
    - The structure of the response
    - The full response text
    - For each part (in the structure) of the response, the particular value of that part
    - For each part, if it's marked as good or bad by the user.

### Running tests:
Each time the user changes the code, they will also have to make changes to the prompt definitions for tests. When the tests are run, we check what part of the prompt has changed since the last change and we run the test against that.

### Invalidating / updating older test cases:
Each part of the prompt can change, and that has effects on what tests are run:
- The template changes:
    - In this case, we will run the test against the last prompt change data and see the output.
    - The output of this test will be saved against the current prompt as the new data set for this prompt. The new data set will be also auto marked as good or bad based on the previous test results and if it passed the current test or not.
- The derived variables change:
    - This will not cause a new prompt version. Instead, it will just overwrite the existing derived variables for each test case once all tests pass.
- The user input change:
    - No action needed here
- The model used change:
    - This is similar to the case of a new prompt version
- Response structure change:
    - The user will have to define a function to change the older response format to the newer one, and rerun the tests
    - On test run, the new response will overwrite the older one once all tests pass

### Defining a prompt:
Something like this:

```
{
    id: "template1",
    template: "Please answer this question based on the context:\nContext:{context}\n\nQuestion:\n{question}\n\nAnswer:",
    derivedVariables: [{
        key: "context",
        getValue: (userInputMap: { [key: string]: string }) => {
            return ...
        }
    }],
    userInputVariables: ["question"],
    responseStructure:{
        type: "string",
        validator: llmSimilarityChecker
    },
    model: "gpt-4"
}
```