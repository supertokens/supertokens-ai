import openai
import re
import os
import tiktoken
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

# Load the cl100k_base tokenizer which is designed to work with the ada-002 model
tokenizer = tiktoken.get_encoding("cl100k_base")

if os.path.exists('processed/scraped.csv'):
    df = pd.read_csv('processed/scraped.csv')
else:
    df = pd.DataFrame(columns=['text', 'embeddings'])

root_dir = '/Users/rishabhpoddar/Desktop/supertokens/main-website/docs/v2'

not_allowed = [root_dir + '/auth-react', root_dir + '/auth-react_versioned_docs', root_dir + '/auth-react_versioned_sidebars', root_dir + '/build', root_dir + '/change_me', root_dir + '/community', root_dir + '/node_modules', root_dir + '/nodejs', root_dir + '/nodejs_versioned_docs', root_dir + '/nodejs_versioned_sidebars', root_dir + '/website', root_dir + '/website_versioned_docs', root_dir + '/website_versioned_sidebars']

only_allow = [root_dir + '/mfa']
consider_only_allow = True

max_tokens = 500

chunks_ignored = 0

# Function to split the text into chunks of a maximum number of tokens
def split_into_many(text, max_tokens = max_tokens):
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

def find_df_for_text(text):
    for i in range(len(df)):
        if df.loc[i, 'text'] == text:
            return df.loc[i]
    return None


def convert_mdx_to_chunks(root_dir):
    mdx_content = []
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.mdx'):
                filepath = os.path.join(subdir, file)
                continue_to_next_loop = False
                for i in not_allowed:
                    if i in filepath:
                        continue_to_next_loop = True
                for i in only_allow:
                    if i not in filepath and consider_only_allow:
                        continue_to_next_loop = True
                if continue_to_next_loop:
                    continue
                with open(filepath, 'r') as f:
                    contents = f.read()
                    if (len(tokenizer.encode(contents)) > max_tokens):
                        h2chunks = re.split(r'(?<=^##\s)', contents, flags=re.MULTILINE)
                        for chunk in h2chunks:
                            finalChunk_without_tags = re.sub(r'<[^>]+>', '', chunk)
                            finalChunk_without_tags = finalChunk_without_tags.replace("##", "")
                            finalChunk_without_tags = finalChunk_without_tags.replace(":::", "")
                            chunk_within_token_limit = split_into_many(finalChunk_without_tags)
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

mdx_content = convert_mdx_to_chunks(root_dir)

# convert the mdx_content list into a list tokens
mdx_content_tokens = []
for i in mdx_content:
    mdx_content_tokens.append(to_token(i))

new_df = pd.DataFrame(columns=['text', 'embeddings'])
for i in range(2):
    print("=========================")
    existing_df = find_df_for_text(mdx_content[i])
    if existing_df is not None:
        new_df.loc[i, 'text'] = existing_df['text']
        new_df.loc[i, 'embeddings'] = existing_df['embeddings']
        print("Embedding already exists for " + str(i) + " out of " + str(len(mdx_content_tokens)))
        print()
        continue
    print("Calculating embed for " + str(i) + " out of " + str(len(mdx_content_tokens)))
    print(mdx_content[i])
    print()
    embeddings = openai.Embedding.create(
        engine='text-embedding-ada-002',
        input=mdx_content_tokens[i]
    )['data'][0]['embedding']

    new_df.loc[i, 'text'] = mdx_content[i]
    new_df.loc[i, 'embeddings'] = embeddings

new_df.to_csv('processed/scraped.csv', index=False)











# # Define a function which returns the maximum number of words across all strings in mdx_content
# def max_words(mdx_content):
#     max_words = 0
#     for i in mdx_content:
#         count = len(i.split(" "))
#         if count > max_words:
#             max_words = count
#     return max_words

# def average_words(mdx_content):
#     counts = []
#     for i in mdx_content:
#         count = len(i.split(" "))
#         counts.append(count)
#     return sum(counts)/len(counts)

# # a function to calculate the median number of words across all strings in mdx_content
# def median_words(mdx_content):
#     counts = []
#     for i in mdx_content:
#         count = len(i.split(" "))
#         counts.append(count)
#     counts.sort()
#     if len(counts) % 2 == 0:
#         return (counts[len(counts)//2] + counts[len(counts)//2 - 1])/2
#     else:
#         return counts[len(counts)//2]


# def max_tokens(mdx_content):
#     max_words = 0
#     for i in mdx_content:
#         count = len(i)
#         if count > max_words:
#             max_words = count
#     return max_words

# def average_tokens(mdx_content):
#     counts = []
#     for i in mdx_content:
#         count = len(i)
#         counts.append(count)
#     return sum(counts)/len(counts)

# # a function to calculate the median number of words across all strings in mdx_content
# def median_tokens(mdx_content):
#     counts = []
#     for i in mdx_content:
#         count = len(i)
#         counts.append(count)
#     counts.sort()
#     if len(counts) % 2 == 0:
#         return (counts[len(counts)//2] + counts[len(counts)//2 - 1])/2
#     else:
#         return counts[len(counts)//2]

# print(max_words(mdx_content))
# print(average_words(mdx_content))
# print(median_words(mdx_content))

# print("")
# print(max_tokens(mdx_content_tokens))
# print(average_tokens(mdx_content_tokens))
# print(median_tokens(mdx_content_tokens))

# print("")
# print(len(mdx_content))

# print(chunks_ignored)