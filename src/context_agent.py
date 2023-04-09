import os
from termcolor import colored
from dotenv import load_dotenv
from llm import chat_completion, get_embedding, to_token, distances_from_embeddings
import pandas as pd
import numpy as np
load_dotenv()

chunks = [500, 1024, 2048]
df = {}
for max_tokens_per_chunk in chunks:
    embeddings_location = 'processed/' + str(max_tokens_per_chunk) + '-limit.csv'
    df[max_tokens_per_chunk] = pd.DataFrame(columns=['text', 'embeddings'])
    if os.path.exists(embeddings_location):
        df[max_tokens_per_chunk] = pd.read_csv(embeddings_location)


existing_embeddings = df

for chunk in chunks:
    existing_embeddings[chunk]['embeddings'] = existing_embeddings[chunk]['embeddings'].apply(lambda x: eval(str(x))).apply(np.array)

new_df = pd.DataFrame(columns=['text', 'embeddings'])
for chunk in chunks:
    new_df = pd.concat([new_df, existing_embeddings[chunk]], ignore_index=True)

existing_embeddings = {} # free up memory

# now we load up discord embeddings
discord_df = pd.read_csv('processed/discord_threads.csv')
discord_df['embeddings'] = discord_df['embeddings'].apply(lambda x: eval(str(x))).apply(np.array)

new_df = pd.concat([new_df, discord_df], ignore_index=True)
discord_df = {} # free up memory

debug = os.environ.get('DEBUG') is not None 

already_seen_context_for_question = {}

def get_context(question, prev_answer, right_track, context_limit=4, token_limit=2500):
    if question not in already_seen_context_for_question:
        already_seen_context_for_question[question] = []
    question_embeddings = get_embedding(question)
    new_df['distances'] = distances_from_embeddings(question_embeddings, new_df['embeddings'].values)

    number_skipped_because_of_bad_context = 0
    if right_track:
        context = []
        curr_token_count = 0
        for i, row in new_df.sort_values('distances', ascending=True).iterrows():
            if len(context) >= context_limit or number_skipped_because_of_bad_context >= context_limit:
                break
            if row['text'] not in already_seen_context_for_question[question]:
                already_seen_context_for_question[question].append(row['text'])
                if not is_context_relevant_according_to_gpt(row['text'], question):
                    number_skipped_because_of_bad_context += 1
                    continue

                if (curr_token_count + len(to_token(row['text']))) > token_limit:
                    continue
                curr_token_count += len(to_token(row['text']))
                context.append(row['text'])
        
        if debug:
            for c in context:
                print()
                print(colored("=========NEW CONTEXT BELOW=========", "red"))
                print(colored(c, "yellow"))

        return context
    else:
        prev_answer_embeddings = get_embedding(prev_answer)
        context = []
        curr_token_count = 0
        number_skipped_because_of_answer_distance = 0
        for i, row in new_df.sort_values('distances', ascending=True).iterrows():
            if len(context) >= context_limit or number_skipped_because_of_answer_distance >= context_limit or number_skipped_because_of_bad_context >= context_limit:
                break
            if row['text'] not in already_seen_context_for_question[question]:
                already_seen_context_for_question[question].append(row['text'])
                
                if not is_context_relevant_according_to_gpt(row['text'], question):
                    number_skipped_because_of_bad_context += 1
                    continue
                
                if distances_from_embeddings(prev_answer_embeddings, [row['embeddings']])[0] - row['distances'] < 0:
                    # this means that the current row is further away from the previous answer, so we skip this one.
                    number_skipped_because_of_answer_distance += 1
                    continue

                if (curr_token_count + len(to_token(row['text']))) > token_limit:
                    continue
                curr_token_count += len(to_token(row['text']))
                context.append(row['text'])
        
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