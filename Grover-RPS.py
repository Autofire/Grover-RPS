#!/usr/bin/env python
# coding: utf-8

"""
Some of this code is based on the code found in this tutorial page:
https://qiskit.org/textbook/ch-applications/satisfiability-grover.html

However, much has changed since starting from there.
"""

import numpy as np
from qiskit import BasicAer, execute, IBMQ
from qiskit.providers.ibmq import least_busy
#from qiskit.visualization import plot_histogram
from qiskit.aqua import QuantumInstance
from qiskit.aqua.algorithms import Grover
from qiskit.aqua.components.oracles import LogicalExpressionOracle
from qiskit.compiler import transpile
from qiskit.tools.monitor import job_monitor
import random

#get_ipython().run_line_magic('config', "InlineBackend.figure_format = 'svg' # Makes the images look nice")
#get_ipython().run_line_magic('matplotlib', 'inline')


""" This assumes that the counts are already sorted and as a list """
def counts_to_probabilities(counts):
    total_counts = sum(counts)
    probabilities = list(map(lambda x: (x/total_counts), counts))
    
    # To make it easier to figure out what result we get, we'll combine
    # values so we can see what's the result
    for i in range(len(probabilities) - 1):
        probabilities[i+1] += probabilities[i]
    
    return probabilities


""" Assumes that the list of probabilities are already combined """
def random_selection(probabilities, debug=False):
    randomVal = random.random()

    # Logic pulled from https://www.geeksforgeeks.org/python-get-the-index-of-first-element-greater-than-k/
    resultingAction = next(x for x, val in enumerate(probabilities) if val > randomVal)
    
    if(debug):
        print(f'{randomVal} yields {resultingAction}')
    
    return resultingAction



""" Starting here... first we'll give the opening message """
print("Grover is an AI who's decisions are based on the result of running the Grover algorithm.")
print("He tends to cheat more on bad days, when there's more noise in the quantum computer...")
print()


""" Get the data from the quantum computer """
expression = 'a & b'
oracle = LogicalExpressionOracle(expression, optimization = True)
grover = Grover(oracle)
grover_compiled = grover.construct_circuit(measurement=True)


# Load our saved IBMQ accounts and get the backend
print("Loading account...")
provider = IBMQ.load_account()

provider = IBMQ.get_provider(hub='ibm-q')
device = provider.get_backend('ibmq_ourense')
#device = least_busy(provider.backends(simulator=False))
print("Selected device: ", device)

job = execute(grover_compiled, backend=device, shots=1024)
job_monitor(job, interval = 2)



""" Now we can process the for our RNG stuff """

print("Computing probabilities...")

counts = job.result().get_counts()

# I know this is sloppy but it works
ordered_counts = [
    counts.get('00', 0),
    counts.get('01', 0),
    counts.get('10', 0),
    counts.get('11', 0)
]

ai_probabilities = counts_to_probabilities(ordered_counts)

# We use the 3 invalid probabilities for determining the throw
ordered_counts_without_valid = ordered_counts
ordered_counts_without_valid.pop()
ai_action_probabilities = counts_to_probabilities(ordered_counts_without_valid)



""" Now we can finally start the game! """

print()
print("Thanks for waiting! Grover's ready to play!")

game_over = False
num_to_throw = {
    0: 'rock',
    1: 'paper',
    2: 'scissors'
}

points_to_win = 5
player_points = 0
grover_points = 0

debug_rng = False

while(not game_over):
    
    player_action = ""
    while(player_action == ""):
        player_action = input("Rock, paper, or scissors? ")[0]
        if(not (player_action in ['r', 'p', 's', 'e'])):
            player_action = ""

    if(player_action == 'e'):
        print("You give up...")
        game_over = True
        
    else:
        print()

        ai_action_type = random_selection(ai_probabilities, debug=debug_rng)

        if(ai_action_type == 0):
            print("Grover pulls a gun! *BANG*")
            print("You appear to have died...")
            print()
            print("Incidentally, that means Grover wins.")
            game_over = True
        elif(ai_action_type == 1):
            print("Grover laughs histerically!")
            print("(You seem to have lost this round...)")
            grover_points += 1
        elif(ai_action_type == 2):
            print("Grover forgot the score... oh, he remembered it again!")
            print("(You seem to have lost a point...)")
            player_points -= 1
        elif(ai_action_type == 3):
            ai_action_name = num_to_throw.get(
                random_selection(ai_action_probabilities, debug=debug_rng)
            )
            print(f"Grover throws {ai_action_name}!")
            ai_action = ai_action_name[0]

            if(ai_action == player_action):
                print("It's a draw!")
            elif((ai_action == 'r' and player_action == 'p') or
                 (ai_action == 'p' and player_action == 's') or
                 (ai_action == 's' and player_action == 'r')):
                print("You win the round!")
                player_points += 1
            else:
                print("Grover wins the round!")
                grover_points += 1


    if(not game_over):
        print()
        if(player_points >= points_to_win):
            print(f"You have {player_points} points, so you win the game!")
            print("Grover congratulates you on your hard-fought victory.")
            game_over = True
        elif(grover_points >= points_to_win):
            print(f"Grover has {grover_points} points, so he wins the game.")
            print("Grover smiles with glee!")
            game_over = True
        else:
            print(f"You have {player_points} points, and Grover has {grover_points}")
        
        print()

# End while(not game_over)


print()
print("Results of the quantum computation:")

# re-get this stuff
ordered_counts = [
    counts.get('00', 0),
    counts.get('01', 0),
    counts.get('10', 0),
    counts.get('11', 0)
]

print(f'Counts: {counts}')

total_counts = sum(ordered_counts)
raw_ai_probabilities = list(map(lambda x: (x/total_counts), ordered_counts))
print(f'AI probabilities:       {raw_ai_probabilities} (Gun/Laugh/Forget/Normal)')

ordered_counts.pop()

total_counts = sum(ordered_counts)
raw_ai_throw_probabilities = list(map(lambda x: (x/total_counts), ordered_counts))
print(f'AI throw probabilities: {raw_ai_throw_probabilities} (Rock/Paper/Scissors)')

print()
