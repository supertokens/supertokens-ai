import openai
import tiktoken
from dotenv import load_dotenv
import os
import time
import random
from openai.embeddings_utils import distances_from_embeddings
load_dotenv()

tokenizer = tiktoken.get_encoding("cl100k_base")
openai.api_key = os.environ.get('OPEN_AI_KEY')

allow_gpt_4 = os.environ.get('USE_GPT_4', 'false').lower() == 'true'

def to_token(text):
    return tokenizer.encode(text)

def chat_completion(messages, use_gpt4=False):
    use_gpt4 = use_gpt4 and allow_gpt_4
    while True:
        try:
            response = openai.ChatCompletion.create(
                    messages=messages,
                    temperature=0,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None,
                    model="gpt-4" if use_gpt4 else "gpt-3.5-turbo",
                )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            if "That model is currently overloaded with other requests" in str(e):
                # sleep for a random amount of time
                time.sleep(random.random() * 3)
                continue
            raise e

def get_embedding(text):
    return openai.Embedding.create(
        engine='text-embedding-ada-002',
        input=to_token(text)
    )['data'][0]['embedding']

def get_distance_from_embeddings(emb1, emb2array):
    return distances_from_embeddings(emb1, emb2array, distance_metric='cosine')