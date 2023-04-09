import os
from termcolor import colored
from dotenv import load_dotenv
from llm import chat_completion
load_dotenv()

debug = os.environ.get('DEBUG') is not None 

def get_if_on_right_track_based_on_grade(question, answer):
    prompt = f"You are a strict teacher and an expert at SuperTokens and authentication. You are grading someone's answer to a question. Give a score out of 10, where 10 indicates that the answer is helpful and resolved the question, whereas 0 indicates that the answer is completely wrong or irrelevant to the question. Answer with just a number and not a word more.\n\nQuestion:\n\"\"\"{question}\"\"\"\n\nAnswer:\"\"\"\n{answer}\"\"\"\n\nScore: "

    messages = [{"role": "user", "content": prompt}]
    try:
        score = float(chat_completion(messages))
    except ValueError:
        score = -1
    
    if debug:
        print()
        print(colored("============ANSWER SCORE===============", "red"))
        print(colored(score, "yellow"))

    # it's very lenient at giving scores.. so if it's <= 7, we will try and get more context
    if score != -1 and score <= 7:
        return False
    return True
        

