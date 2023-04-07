from termcolor import colored
# this is there at the start, above all the other imports cause if we put it 
# below, for fist time users, it will take a long time before this message is shown.
print(colored("Loading knowledge base. This will take a few seconds...", "blue"))

import openai
import re
import os
import tiktoken
from dotenv import load_dotenv
import pandas as pd
from openai.embeddings_utils import distances_from_embeddings
import numpy as np
import sys
load_dotenv()

root_dir = os.environ.get('DOCUMENTATION_PATH') or  ""
not_allowed = [root_dir + '/auth-react', root_dir + '/auth-react_versioned_docs', root_dir + '/auth-react_versioned_sidebars', root_dir + '/build', root_dir + '/change_me', root_dir + '/community', root_dir + '/node_modules', root_dir + '/nodejs', root_dir + '/nodejs_versioned_docs', root_dir + '/nodejs_versioned_sidebars', root_dir + '/website', root_dir + '/website_versioned_docs', root_dir + '/website_versioned_sidebars']
only_allow = [root_dir + '/mfa', root_dir + '/session', root_dir + '/emailpassword', root_dir + '/passwordless', root_dir + '/thirdparty']
consider_only_allow = False
# max_tokens_per_chunk = 500

# Load the cl100k_base tokenizer which is designed to work with the ada-002 model
tokenizer = tiktoken.get_encoding("cl100k_base")

chunks = [500, 1024, 2048]
df = {}
for max_tokens_per_chunk in chunks:
    embeddings_location = 'processed/' + str(max_tokens_per_chunk) + '-limit.csv'
    df[max_tokens_per_chunk] = pd.DataFrame(columns=['text', 'embeddings'])
    if os.path.exists(embeddings_location):
        df[max_tokens_per_chunk] = pd.read_csv(embeddings_location)

chunks_ignored = 0

# Function to split the text into chunks of a maximum number of tokens
def split_into_many(text, max_tokens):
    if (len(tokenizer.encode(text)) < max_tokens):
        return [text]
    global chunks_ignored

    # Split the text into sentences - some sentences end with a ". " and some with just a "." followed by a new line.
    sentences = re.split(r'\. |\.\n', text)

    # Get the number of tokens for each sentence
    n_tokens = [len(tokenizer.encode(sentence + ". ")) for sentence in sentences]
    
    chunks = []
    tokens_so_far = 0
    chunk = []

    # Loop through the sentences and tokens joined together in a tuple
    for sentence, token in zip(sentences, n_tokens):

        # If the number of tokens so far plus the number of tokens in the current sentence is greater 
        # than the max number of tokens, then add the chunk to the list of chunks and reset
        # the chunk and tokens so far
        if tokens_so_far + token > max_tokens and len(chunk) > 0:
            chunks.append(" ".join(chunk))
            chunk = []
            tokens_so_far = 0

        # If the number of tokens in the current sentence is greater than the max number of 
        # tokens, go to the next sentence
        if token > max_tokens:
            chunks_ignored += 1 # for analysis only
            continue

        # Otherwise, add the sentence to the chunk and add the number of tokens to the total
        chunk.append(sentence + ". ")
        tokens_so_far += token + 1

    return chunks

def find_df_for_text_from_existing_embeddings(text):
    for chunk in chunks:
        if chunk in existing_embeddings:
            for i in range(len(existing_embeddings[chunk])):
                if existing_embeddings[chunk].loc[i, 'text'] == text:
                    return existing_embeddings[chunk].loc[i]
    return None

def find_df_for_text_from_df(text):
    for chunk in chunks:
        for i in range(len(df[chunk])):
            if df[chunk].loc[i, 'text'] == text:
                return df[chunk].loc[i]
    return None


def convert_mdx_to_chunks(root_dir, chunk_size):
    mdx_content = []
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.mdx'):
                filepath = os.path.join(subdir, file)
                
                continue_to_next_loop = False
                for i in not_allowed:
                    if i in filepath:
                        continue_to_next_loop = True
                if continue_to_next_loop:
                    continue

                continue_to_next_loop = True
                for i in only_allow:
                    if i in filepath:
                        continue_to_next_loop = False
                if continue_to_next_loop and consider_only_allow:
                    continue
                
                with open(filepath, 'r') as f:
                    contents = f.read()
                    if (len(tokenizer.encode(contents)) > chunk_size):
                        h2chunks = re.split(r'(?<=^##\s)', contents, flags=re.MULTILINE)
                        for chunk in h2chunks:
                            finalChunk_without_tags = re.sub(r'<[^>]+>', '', chunk)
                            finalChunk_without_tags = finalChunk_without_tags.replace("##", "")
                            finalChunk_without_tags = finalChunk_without_tags.replace(":::", "")
                            chunk_within_token_limit = split_into_many(finalChunk_without_tags, chunk_size)
                            for i in chunk_within_token_limit:
                                mdx_content.append(i)
                    else:
                        mdx_content.append(contents)
    return mdx_content
                    

# Set up OpenAI API credentials
openai.api_key = os.environ.get('OPEN_AI_KEY')

# Function to split the text into chunks of a maximum number of tokens
def to_token(text):
    return tokenizer.encode(text)

def decode_tokens(token_ids):
    # Call GPT tokenizer to decode token IDs
    text_tokens = tokenizer.decode(token_ids)
    
    # Return list of text tokens
    return text_tokens.split()

def get_embeddings(chunk_size):
    mdx_content = convert_mdx_to_chunks(root_dir, chunk_size)

    # convert the mdx_content list into a list tokens
    mdx_content_tokens = []
    for i in mdx_content:
        mdx_content_tokens.append(to_token(i))

    new_df = pd.DataFrame(columns=['text', 'embeddings'])
    curr_index = 0
    for i in range(len(mdx_content_tokens)):
        existing_df = find_df_for_text_from_existing_embeddings(mdx_content[i])
        if existing_df is not None:
            continue
        existing_df = find_df_for_text_from_df(mdx_content[i])
        if existing_df is not None:
            new_df.loc[curr_index, 'text'] = existing_df['text']
            new_df.loc[curr_index, 'embeddings'] = existing_df['embeddings']
            curr_index+=1
            continue
        print("=========================")
        print("Calculating embed for " + str(i) + " out of " + str(len(mdx_content_tokens)) + " for chunk size:" + str(chunk_size))
        print()
        embeddings = openai.Embedding.create(
            engine='text-embedding-ada-002',
            input=mdx_content_tokens[i]
        )['data'][0]['embedding']

        new_df.loc[curr_index, 'text'] = mdx_content[i]
        new_df.loc[curr_index, 'embeddings'] = embeddings
        curr_index+=1

    new_df.to_csv('processed/' + str(chunk_size) + '-limit.csv', index=False)
    return new_df

already_seen_context_for_question = {}

def is_context_relevant_according_to_gpt(context, question):
    prompt = f"You are an expert at SuperTokens and authentication. Is the provided context answering the question below? Answer only in \"yes\" or \"no\", and not a word more.\n\nQuestion: \"\"\"{question}\"\"\"\n\nContext: \"\"\"{context}\"\"\"\n\nAnswer (yes/no):"
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
            messages=messages,
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            model="gpt-3.5-turbo",
        )
    response = response["choices"][0]["message"]["content"].strip()
    return response.lower() != "no" and response.lower() != "no."

def get_top_embeddings_up_to_limit(question, prev_answer, right_track, context_limit=4, token_limit=2500):
    if question not in already_seen_context_for_question:
        already_seen_context_for_question[question] = []
    question_embeddings = openai.Embedding.create(
        engine='text-embedding-ada-002',
        input=to_token(question)
    )['data'][0]['embedding']
    new_df['distances'] = distances_from_embeddings(question_embeddings, new_df['embeddings'].values, distance_metric='cosine')

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

                if (curr_token_count + len(tokenizer.encode(row['text']))) > token_limit:
                    continue
                curr_token_count += len(tokenizer.encode(row['text']))
                context.append(row['text'])
        return context
    else:
        prev_answer_embeddings = openai.Embedding.create(
            engine='text-embedding-ada-002',
            input=to_token(prev_answer)
        )['data'][0]['embedding']
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
                
                if distances_from_embeddings(prev_answer_embeddings, [row['embeddings']], distance_metric='cosine')[0] - row['distances'] < 0:
                    # this means that the current row is further away from the previous answer, so we skip this one.
                    number_skipped_because_of_answer_distance += 1
                    continue

                if (curr_token_count + len(tokenizer.encode(row['text']))) > token_limit:
                    continue
                curr_token_count += len(tokenizer.encode(row['text']))
                context.append(row['text'])
        return context

existing_embeddings = {}

if len(sys.argv) > 1 and sys.argv[1] == "--update":
    for chunk in chunks:
        existing_embeddings[chunk] = get_embeddings(chunk)   
else:
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

def get_multi_line_input():
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)
    
    inp = "\n".join(contents)
    if inp == "exit":
        quit()
    return inp

while(True):
    already_seen_context_for_question = {}
    # Ask the user for a question from the console
    print(colored("Enter a new question (or type \"exit\") and press Ctrl-D or Ctrl-Z (windows) in a new line to ask: ", "cyan"))
    question = get_multi_line_input()

    print()
    print()
    print(colored("Thinking...", "cyan"))
    print()
    
    debug = os.environ.get('DEBUG') is not None 
    if question.startswith("DEBUG "):
        question = question.replace("DEBUG ", "")
        debug = True

    more_context = ""

    right_track = True
    prev_answer = ""
    number_of_bad_grade_iterations = 0
    while(True):
        context = get_top_embeddings_up_to_limit(question, prev_answer, right_track)

        if len(context) == 0 or number_of_bad_grade_iterations > 5:
            print("Answer: ")
            print(colored("I don't know. Please reach out to the SuperTokens team on Discord: https://supertokens.com/discord", "green"))
            break

        prompt = f"You are a friendly developer who is an expert at SuperTokens and authentication. Answer the question based on the context below, and if the question can't be answered with a high degree of certainty, based on the context, say \"I don't know\". Each context starts with the title \"New Context:\" and is in a new chat. You can ignore a context if it's not relevant to the question, and if there is no context that is relevant, say \"I don't know\". Do not mention the context directly in your answer. Do not provide code snippets unless it's mentioned in the context already, or if the question specifically asks for code snippets."

        messages = [{"role": "user", "content": prompt}]
        for i in range(len(context)):
            messages.append({"role": "user", "content": "New Context:\n" + context[i]})
        messages.append({"role": "user", "content": "Question:\n" + question})
        messages.append({"role": "user", "content": "Answer:"})
        if debug:
            for m in messages:
                print()
                print()
                print(colored("=====================================", "red"))
                print(colored(m["content"], "yellow"))
                print()
                print()

        # Create a completions using the question and context
        response = openai.ChatCompletion.create(
            messages=messages,
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            model="gpt-3.5-turbo",
        )
        prev_answer = response["choices"][0]["message"]["content"].strip()


        # now we ask chatgpt to tell us if the question is actually answered (without the context)
        prompt = f"You are a strict teacher and an expert at SuperTokens and authentication. You are grading someone's answer to a question. Give a score out of 10, where 10 indicates that the answer is helpful and resolved the question, whereas 0 indicates that the answer is completely wrong or irrelevant to the question. Answer with just a number and not a word more.\n\nQuestion:\n\"\"\"{question}\"\"\"\n\nAnswer:\"\"\"\n{prev_answer}\"\"\"\n\nScore: "

        messages = [{"role": "user", "content": prompt}]

        response = openai.ChatCompletion.create(
            messages=messages,
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            model="gpt-3.5-turbo",
        )
        try:
            score = float(response["choices"][0]["message"]["content"].strip())
        except ValueError:
            score = -1
        if debug:
            print()
            print()
            print(colored("============ANSWER SCORE===============", "red"))
            print(colored(score, "yellow"))
            print()
            print(colored(prev_answer, "yellow"))
            print()
            print()
        
        # it's very lenient at giving scores.. so if it's <= 7, we will try and get more context
        if score != -1 and score <= 7:
            right_track = False
            number_of_bad_grade_iterations += 1
            print()
            print(colored("Thinking some more...", "cyan"))
            print()
            continue


        print("Answer: ")
        print(colored(prev_answer, "green"))
        print()
        print(colored("WARNING: Code snippets / answer suggested by the bot may be wrong. For additional help, please ask on our Discord server: https://supertokens.com/discord", "red"))
        print()

        print(colored("Your reply (type \"new\" for a new question, or \"exit\"): ", "cyan"))
        more_context = get_multi_line_input()
        if more_context == "new":
            print()
            break


        print()
        print(colored("Thinking...", "cyan"))
        print()

        messages = []
        messages.append({"role": "user", "content": question})
        messages.append({"role": "system", "content": prev_answer})
        messages.append({"role": "user", "content": more_context})
        messages.append({"role": "user", "content": "Rephrase my question (pretending you are me) based on the conversation above, retaining any code snippets provided by me, and do not loose out on any information.\n\nBased on my reply to your answer, do you think you are on the right track to answering the question?. If you think that you are on the right track, say \"yes\", else say \"no\".\n\nExample output format is:\n\"\"\"Rephrased question: ....\n\nRight track: yes\"\"\"\n\nRephrased question:"})
        response = openai.ChatCompletion.create(
            messages=messages,
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            model="gpt-3.5-turbo",
        )
        if debug:
            print()
            print()
            print(colored("============REPHRASED QUESTION===========", "red"))
            print(colored(response["choices"][0]["message"]["content"].strip(), "yellow"))
            print()
            print()
        new_resp = response["choices"][0]["message"]["content"].strip()
        if "\nRight track:" in new_resp:
            question = new_resp.split("\nRight track:")[0].strip()
            right_track = new_resp.split("\nRight track:")[1].strip().lower() == "yes" or new_resp.split("\nRight track:")[1].strip().lower() == "yes."
        else:
            right_track = True
            question = response["choices"][0]["message"]["content"].strip()
    