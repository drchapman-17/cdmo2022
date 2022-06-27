from pulp import *

prob = LpProblem("Brewery Problem", LpMaximize)

A = LpVariable("Ale", 0, None, LpInteger)
B = LpVariable("Beer", 0, None, LpInteger)

prob += 13*A + 23*B, "Profit"
prob += 5*A + 15*B <= 480, "Corn"
prob += 4*A + 4*B <= 160, "Hop"
prob += 35*A + 20*B <= 1190, "Malt"

# We can specify the solver to use as a parameter of solve
prob.solve()


