import os
from termcolor import colored
from dotenv import load_dotenv
from llm import chat_completion, get_embedding, to_token, distances_from_embeddings
import pandas as pd
import numpy as np
load_dotenv()

CHUNKS = [500, 1024, 2048]

def load_docs_embeddings():
    docs_embeddings = {}
    for max_tokens_per_chunk in CHUNKS:
        embeddings_location = f'processed/{max_tokens_per_chunk}-limit.csv'
        docs_embeddings[max_tokens_per_chunk] = pd.read_csv(embeddings_location)

    for chunk in CHUNKS:
        docs_embeddings[chunk]['embeddings'] = docs_embeddings[chunk]['embeddings'].apply(lambda x: eval(str(x))).apply(np.array)

    return docs_embeddings

def load_discord_embeddings():
    discord_df = pd.read_csv('processed/discord_threads.csv')
    discord_df['embeddings'] = discord_df['embeddings'].apply(lambda x: eval(str(x))).apply(np.array)
    return discord_df

def load_all_embeddings():
    docs_embeddings = load_docs_embeddings()
    discord_embeddings = load_discord_embeddings()

    embeddings_df = pd.DataFrame(columns=['text', 'embeddings'])

    for chunk in CHUNKS:
        embeddings_df = pd.concat([embeddings_df, docs_embeddings[chunk]], ignore_index=True)

    embeddings_df = pd.concat([embeddings_df, discord_embeddings], ignore_index=True)

    return embeddings_df

embeddings_df = load_all_embeddings()
debug = os.environ.get('DEBUG') is not None 
already_seen_context_for_question = {}

def get_context(question, prev_answer, right_track, context_limit=4, token_limit=2500):
    if question not in already_seen_context_for_question:
        already_seen_context_for_question[question] = []
    question_embeddings = get_embedding(question)
    embeddings_df['distances'] = distances_from_embeddings(question_embeddings, embeddings_df['embeddings'].values)

    number_skipped_because_of_bad_context = 0
    number_skipped_because_of_answer_distance = 0
    context = []
    curr_token_count = 0
    for i, row in embeddings_df.sort_values('distances', ascending=True).iterrows():
        if len(context) >= context_limit or number_skipped_because_of_bad_context >= context_limit or number_skipped_because_of_answer_distance >= context_limit:
            break
        if row['text'] not in already_seen_context_for_question[question]:
            already_seen_context_for_question[question].append(row['text'])
            
            if not is_context_relevant_according_to_gpt(row['text'], question):
                number_skipped_because_of_bad_context += 1
                continue

            token_count = len(to_token(row['text']))

            if right_track or distances_from_embeddings(get_embedding(prev_answer), [row['embeddings']])[0] - row['distances'] >= 0:
                if (curr_token_count + token_count) > token_limit:
                    continue
                curr_token_count += token_count
                context.append(row['text'])
            else:
                number_skipped_because_of_answer_distance += 1
        
    if debug:
        for c in context:
            print()
            print(colored("=========NEW CONTEXT BELOW=========", "red"))
            print(colored(c, "yellow"))

    return context
        

def is_context_relevant_according_to_gpt(context, question):
    prompt = f"You are an expert at SuperTokens and authentication. Is the provided context answering the question below? Answer only in \"yes\" or \"no\", and not a word more.\n\nQuestion: \"\"\"{question}\"\"\"\n\nContext: \"\"\"{context}\"\"\"\n\nAnswer (yes/no):"
    messages = [{"role": "user", "content": prompt}]
    response = chat_completion(messages)
    return response.lower() != "no" and response.lower() != "no."

def clear_already_seen_context_for_question():
    global already_seen_context_for_question
    already_seen_context_for_question = {}