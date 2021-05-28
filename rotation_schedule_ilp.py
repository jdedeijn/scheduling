"""Solves the following scheduling problem.

There are 10 teams and 8 games. We want to create a schedule such that:
(i)   Each team gets to play every game
(ii)  No multiple matches are scheduled at the same time for some game
(iii) Every matchup between teams occurs at most once

Approach:
1. We created a roulation scheme beforehand (summarized in matches.csv),
with 8 rounds of 5 matches satisfying constraint (iii) above.
2. This script solves an ILP model to assign a game to each match in the
roulation scheme, satisfying also constraints (i) and (ii).
"""

import os
from collections import defaultdict
from itertools import product

import numpy as np
from ortools.linear_solver import pywraplp

# Load schedule of matches
match_team = np.zeros((5, 8, 10))
path = os.path.join(os.path.dirname(__file__), "data", "matches.txt")
matches = np.loadtxt(path, delimiter="\t").astype(int)
for i, j, t in matches:
    match_team[i, j, t-1] = 1  # team t plays in match i in round j

# Create solver
solver = pywraplp.Solver.CreateSolver("SCIP")

# Define variables
x = defaultdict(lambda: defaultdict(dict))
for i, j, k in product(range(5), range(8), range(8)):
    x[i][j][k] = solver.IntVar(0, 1, f"x[{i}][{j}][{k}]")

# Define constraints: each game is played at most once per round
for j, k in product(range(8), range(8)):
    solver.Add(sum(x[i][j][k] for i in range(5)) <= 1)

# Define constraints: each match in each round gets assigned exactly one game
for i, j in product(range(5), range(8)):
    solver.Add(sum(x[i][j][k] for k in range(8)) == 1)

# Define constraints: each team plays every game exactly once
for k, t in product(range(8), range(10)):
    constraint_expr = [x[i][j][k] for i, j in product(range(5), range(8))
                       if match_team[i, j, t] == 1]
    solver.Add(sum(constraint_expr) == 1)

# Solve
status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    for i, j, k in product(range(5), range(8), range(8)):
        if x[i][j][k].solution_value() == 1:
            print(f"Match {i+1} in round {j+1} does game {k+1}")
else:
    print('The problem does not have an optimal solution.')