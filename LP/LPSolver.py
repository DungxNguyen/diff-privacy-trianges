import gurobipy as grb

# Load a model

print("Loading a model")

model = grb.read("/apps/software/vendor/grbrobi/8.0.1/examples/data/afiro.mps")

model.optimize()

model.printAttr('X')

print("Creating a new model")

m = grb.Model()

# Variables
x = m.addVar(vtype=grb.GRB.BINARY, name = "x")
y = m.addVar(vtype=grb.GRB.BINARY, name = "y")
z = m.addVar(vtype=grb.GRB.BINARY, name = "z")


# Objectives
m.setObjective(x + y + 2 * z, grb.GRB.MAXIMIZE)

# Constraints
c1 = m.addConstr(2 * x + y + 3 * z <= 4)
c2 = m.addConstr(x + y >= 1)


# Solve
m.optimize()

# Print attributes
m.printAttr("x")
