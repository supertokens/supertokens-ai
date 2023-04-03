import pandas as pd
import os
import json
import openai
from dotenv import load_dotenv
import tiktoken
load_dotenv()

test_case_string = "st-bot-test-case"

max_token_limit = 2048

tokenizer = tiktoken.get_encoding("cl100k_base")

openai.api_key = os.environ.get('OPEN_AI_KEY')

df = pd.DataFrame(columns=['text', 'embeddings', 'id'])
if os.path.exists('processed/discord_threads.csv'):
    df = pd.read_csv('processed/discord_threads.csv')


test_df = pd.DataFrame(columns=['question', 'answer', 'embeddings'])
if os.path.exists('processed/test_cases.csv'):
    test_df = pd.read_csv('processed/test_cases.csv')

with open("processed/discord_threads.json", "r") as f:
    threads = json.loads(f.read())

new_df = pd.DataFrame(columns=['text', 'embeddings', 'id'])

def find_df_for_id_from_df(id):
    for i in range(len(df)):
        if df.loc[i, 'id'] == id:
            return df.loc[i]
    return None

count = -1
for curr_thread in threads:
    count += 1
    existing_df = find_df_for_id_from_df(curr_thread['id'])
    if existing_df is not None:
        new_df.loc[count, 'text'] = existing_df['text']
        new_df.loc[count, 'embeddings'] = existing_df['embeddings']
        new_df.loc[count, 'id'] = existing_df['id']
        continue
    
    message = ""
    is_test_case = False
    for curr_message in curr_thread['messages']:
        if test_case_string in curr_message['body']:
            is_test_case = True
            break
        message += curr_message["author"]["username"] + ": " + curr_message['body'] + "~C_END~\n\n"
    

    tokens = tokenizer.encode(message)
    if (len(tokens) > max_token_limit):
        # we skip this thread cause it's too long..
        continue

    print("Fetching embeddings for thread: " + str(count) + " / " + str(len(threads)))
    embeddings = openai.Embedding.create(
        engine='text-embedding-ada-002',
        input=tokens
    )['data'][0]['embedding']

    new_df.loc[count, 'text'] = message
    new_df.loc[count, 'embeddings'] = embeddings
    new_df.loc[count, 'id'] = curr_thread['id']

    if is_test_case:
        question = curr_thread['messages'][0]["body"]
        answer = ""
        for i in range(len(curr_thread['messages'])):
            if i == 0:
                continue
            if test_case_string in curr_thread['messages'][i]['body']:
                break
            answer += curr_thread['messages'][i]['body'] + "\n"
        
        tokens = tokenizer.encode(answer)

        print("Fetching embeddings for test case.")
        embeddings = openai.Embedding.create(
            engine='text-embedding-ada-002',
            input=tokens
        )['data'][0]['embedding']
        curr_index = len(test_df)
        test_df.loc[curr_index, 'question'] = question
        test_df.loc[curr_index, 'answer'] = answer
        test_df.loc[curr_index, 'embeddings'] = embeddings

new_df.to_csv('processed/discord_threads.csv', index=False)
test_df.to_csv('processed/test_cases.csv', index=False)