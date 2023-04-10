import os
from termcolor import colored
from dotenv import load_dotenv
from llm import chat_completion
load_dotenv()

debug = os.environ.get('DEBUG') is not None 

def get_answer(question, context):
    prompt = f"You are a friendly developer who is an expert at SuperTokens and authentication. Answer the question based on the context below, and if the question can't be answered with a high degree of certainty, based on the context, say \"I don't know\". Each context starts with the title \"New Context:\" and is in a new chat. You can ignore a context if it's not relevant to the question, and if there is no context that is relevant, say \"I don't know\". Do not mention the context directly in your answer. Do not provide code snippets unless it's mentioned in the context already, or if the question specifically asks for code snippets."

    messages = [{"role": "user", "content": prompt}]
    for i in range(len(context)):
        messages.append({"role": "user", "content": "New Context:\n" + context[i]})
    messages.append({"role": "user", "content": "Question:\n" + question})
    messages.append({"role": "user", "content": "Answer:"})
    answer = chat_completion(messages, True)

    if debug:
        print()
        print(colored("=========ANSWER FROM Q/A AGENT=========", "red"))
        print(colored(answer, "yellow"))

    return answer

