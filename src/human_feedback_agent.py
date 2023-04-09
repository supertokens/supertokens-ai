import os
from termcolor import colored
from dotenv import load_dotenv
from llm import chat_completion
import json
load_dotenv()

debug = os.environ.get('DEBUG') is not None

def get_human_feedback_sentiment(question, answer, human_feedback):
    messages = []
    messages.append({"role": "user", "content": f"You are sentiment analysis bot. Based on the conversation below, do you think that \"Person 1\" is happy with the answer?\n\n=====\n\nPerson 1:\n{question}\n\nPerson 2:\n{answer}\n\nPerson 1:\n{human_feedback}\n\n====\n\nYou should only respond in JSON format as described below, and not a single word more.\n\nRESPONSE FORMAT:\n{{\n    \"is_person_1_happy\": boolean\n}}\n\nEnsure the response can be parsed by Python json.loads"})

    resp = chat_completion(messages)

    if debug:
        print()
        print(colored("============SENTIMENT FROM HUMAN FEEDBACK AGENT===========", "red"))
        print(colored(resp, "yellow"))
    
    try:
        json_parsed = json.loads(resp)
        return json_parsed["is_person_1_happy"]
    except Exception:
        return True



def get_rephrased_question(question, answer, human_feedback):
    messages = []
    messages.append({"role": "user", "content": "QUESTION:\n" + question + "\n\nAnswer: "})
    messages.append({"role": "system", "content": answer})
    messages.append({"role": "user", "content": "FEEDBACK:\n" + human_feedback})
    messages.append({"role": "user", "content": "Rephrase my question above based on my feedback above, so that the next time i ask the question, i get a better answer. Do not miss out any any code snippets or any information from my question or feedback.\n\nRephrased question: "})

    resp = chat_completion(messages)

    if debug:
        print()
        print(colored("============REPHRASED QUESTION FROM HUMAN FEEDBACK AGENT===========", "red"))
        print(colored(resp, "yellow"))
    
    return resp

