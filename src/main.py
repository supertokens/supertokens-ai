from termcolor import colored
# this is there at the start, above all the other imports cause if we put it 
# below, for fist time users, it will take a long time before this message is shown.
print(colored("Loading knowledge base. This will take a few seconds...", "blue"))
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from llm import chat_completion, get_embedding, to_token, distances_from_embeddings
from question_answer_agent import get_answer
from grading_agent import get_if_on_right_track_based_on_grade
from utils import get_multi_line_input
from human_feedback_agent import get_rephrased_question, get_human_feedback_sentiment
load_dotenv()


chunks = [500, 1024, 2048]
df = {}
for max_tokens_per_chunk in chunks:
    embeddings_location = 'processed/' + str(max_tokens_per_chunk) + '-limit.csv'
    df[max_tokens_per_chunk] = pd.DataFrame(columns=['text', 'embeddings'])
    if os.path.exists(embeddings_location):
        df[max_tokens_per_chunk] = pd.read_csv(embeddings_location)

already_seen_context_for_question = {}

def is_context_relevant_according_to_gpt(context, question):
    prompt = f"You are an expert at SuperTokens and authentication. Is the provided context answering the question below? Answer only in \"yes\" or \"no\", and not a word more.\n\nQuestion: \"\"\"{question}\"\"\"\n\nContext: \"\"\"{context}\"\"\"\n\nAnswer (yes/no):"
    messages = [{"role": "user", "content": prompt}]
    response = chat_completion(messages)
    return response.lower() != "no" and response.lower() != "no."

def get_top_embeddings_up_to_limit(question, prev_answer, right_track, context_limit=4, token_limit=2500):
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
        return context

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

while(True):
    already_seen_context_for_question = {}
    # Ask the user for a question from the console
    print()
    print(colored("Enter a new question (or type \"exit\") and press Ctrl-D or Ctrl-Z (windows) in a new line to ask: ", "cyan"))
    question = get_multi_line_input()

    print()
    print(colored("Thinking...", "cyan"))
    
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

        if debug:
            for c in context:
                print()
                print(colored("=========NEW CONTEXT BELOW=========", "red"))
                print(colored(c, "yellow"))

        # we ask the question / answer agent to give us an answer
        prev_answer = get_answer(question, context)

        # now we grade the answer is based on that we know if we
        # are on the right track or not. The automated grading agent will do this.
        right_track = get_if_on_right_track_based_on_grade(question, prev_answer)

        if not right_track:
            # this will cause a revision in the context being used, or if no other relevant context is found, we will tell the bot to say i don't know.
            number_of_bad_grade_iterations += 1
            continue

        # we now print the answer since the grading agent thinks that it's good.
        print("Answer: ")
        print(colored(prev_answer, "green"))
        print()
        print(colored("WARNING: Answer suggested by the bot may be wrong (especially code snippets). For additional help, please ask on our Discord server: https://supertokens.com/discord", "red"))
        print()

        # now we ask for human feedback / further question on the answer.
        print(colored("Your reply (type \"new\" for a new question, or \"exit\"): ", "cyan"))
        human_feedback = get_multi_line_input()
        if human_feedback == "new":
            break

        print()
        print(colored("Thinking...", "cyan"))

        right_track = get_human_feedback_sentiment(question, prev_answer, human_feedback)

        question = get_rephrased_question(question, prev_answer, human_feedback)
    