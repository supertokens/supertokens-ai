import openai
import tiktoken
from dotenv import load_dotenv
import os
from openai.embeddings_utils import distances_from_embeddings
load_dotenv()

tokenizer = tiktoken.get_encoding("cl100k_base")
openai.api_key = os.environ.get('OPEN_AI_KEY')

def to_token(text):
    return tokenizer.encode(text)

def chat_completion(messages):
    response = openai.ChatCompletion.create(
            messages=messages,
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            model="gpt-3.5-turbo",
        )
    return response["choices"][0]["message"]["content"].strip()

def get_embedding(text):
    return openai.Embedding.create(
        engine='text-embedding-ada-002',
        input=to_token(text)
    )['data'][0]['embedding']

def get_distance_from_embeddings(emb1, emb2array):
    return distances_from_embeddings(emb1, emb2array, distance_metric='cosine')