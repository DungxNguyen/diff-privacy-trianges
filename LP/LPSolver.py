import gurobipy as gu

# Load a model

print("Loading a model")

model = gu.read("/apps/software/vendor/gurobi/8.0.1/examples/data/afiro.mps")

model.optimize()

model.printAttr('X')

print("Creating a new model")

m = gu.Model()

# Variables
x = m.addVar(vtype=gu.GRB.BINARY, name = "x")
y = m.addVar(vtype=gu.GRB.BINARY, name = "y")
z = m.addVar(vtype=gu.GRB.BINARY, name = "z")


# Objectives
m.setObjective(x + y + 2 * z, gu.GRB.MAXIMIZE)

# Constraints
c1 = m.addConstr(2 * x + y + 3 * z <= 4)
c2 = m.addConstr(x + y >= 1)


# Solve
m.optimize()

# Print attributes
m.printAttr("x")
