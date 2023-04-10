import os
from termcolor import colored
from dotenv import load_dotenv
from llm import chat_completion
import json
load_dotenv()

debug = os.environ.get('DEBUG', "false") == "true"

def get_rephrased_question(question, answer, human_feedback):
    messages = []
    messages.append({"role": "user", "content": "QUESTION:\n" + question + "\n\nAnswer: "})
    messages.append({"role": "system", "content": answer})
    messages.append({"role": "user", "content": "FEEDBACK:\n" + human_feedback})
    messages.append({"role": "user", "content": "Rephrase my question above based on my feedback above, so that the next time i ask the question, without providing the above question or answer, i get a better answer. Do not miss out any any code snippets or any information from my question or feedback.\n\nRephrased question: "})

    resp = chat_completion(messages)

    if debug:
        print()
        print(colored("============REPHRASED QUESTION FROM HUMAN FEEDBACK AGENT===========", "red"))
        print(colored(resp, "yellow"))
    
    return resp

