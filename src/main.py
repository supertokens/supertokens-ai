from termcolor import colored
# this is there at the start, above all the other imports cause if we put it 
# below, for fist time users, it will take a long time before this message is shown.
print(colored("Loading knowledge base. This will take a few seconds...", "blue"))
import os
from dotenv import load_dotenv
from context_agent import get_context, clear_already_seen_context_for_question
from question_answer_agent import get_answer
from grading_agent import get_if_on_right_track_based_on_grade
from human_feedback_agent import get_rephrased_question
from utils import get_multi_line_input
load_dotenv()

while(True):
    clear_already_seen_context_for_question()
    
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
        context = get_context(question, prev_answer, right_track)

        if len(context) == 0 or number_of_bad_grade_iterations > 5:
            print("Answer: ")
            print(colored("I don't know. Please reach out to the SuperTokens team on Discord: https://supertokens.com/discord", "green"))
            break

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

        question = get_rephrased_question(question, prev_answer, human_feedback)
    