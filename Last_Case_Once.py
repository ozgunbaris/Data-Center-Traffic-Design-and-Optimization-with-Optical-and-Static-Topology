#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 11:06:43 2021

@author: ozgunbaris
"""

# Solve a multi-commodity flow problem.  Two products ('Static' and 'Optic')
# are produced in 2 cities ('1' and '2') and must be sent to
# warehouses in 3 cities ('3', '4', and '5') to
# satisfy demand ('inflow[h,i]').
#
# Flows on the transportation network must respect arc capacity constraints
# ('capacity[i,j]'). The objective is to minimize the sum of the arc
# transportation costs ('cost[i,j]').

import gurobipy as gp
from gurobipy import GRB

#from Pseudo_Random_Generator import *

from random import random, randrange


N = int(input("Enter the number of nodes:"))


#Connected Graph Generator
connected = []

a = str(randrange(N))
b = str(randrange(N))

while (a == b):
    a = str(randrange(N))
    b = str(randrange(N))
    
connected.append((a,b))
connected.append((b,a))

nodes_not_added = []

for i in range(N):
    nodes_not_added.append(str(i))



nodes_not_added.pop(nodes_not_added.index(str(int(a))))
nodes_not_added.pop(nodes_not_added.index(str(int(b))))

while(len(connected) < 2 * (N-1)):
    random1 = randrange(len(nodes_not_added))
    random2 = randrange(2)
    random3 = randrange(len(connected))
    
    if( nodes_not_added[random1] != connected[random3][random2]) and ( ( connected[random3][random2], nodes_not_added[random1] ) not in connected) and (( nodes_not_added[random1], connected[random3][random2] ) not in connected):
        connected.append(( str(connected[random3][random2]), str(nodes_not_added[random1]) ))
        connected.append(( str(nodes_not_added[random1]), str(connected[random3][random2]) ))
    
    nodes_not_added.pop(random1)
    print(nodes_not_added)
    
print(connected)

#Static Topology Generator
empty = connected.copy()

for i in range(N):
    for j in range(N):
        if i != j and i < j and ((str(i),str(j)) not in empty): #If topology is undirected alter this line! 
            r_number = random()
            
            if r_number > 0.6:
                empty.append((str(i),str(j)))
                empty.append((str(j),str(i))) #If topology is undirected alter this line!
             
                
s_arcs = empty.copy()       
   
#print("Static Topology is the following:", s_arcs)
print("Number of static arcs:", (len(s_arcs)/2))

#Optic Topology Generator

empty_o = []

for i in range(N):
    for j in range(N):
        if i != j and i < j: # If topology is not undirected alter this line!
            r_number = random()
            
            if r_number > 0.6:
                empty_o.append((str(i),str(j)))
                empty_o.append((str(j),str(i))) # If topology is not undirected alter this line!
             
                
o_arcs = empty_o       
   
#print("\nOptic Topology is the following:", o_arcs)            
print("Number of optic arcs:", (len(o_arcs)/2))

#Demand Generator

empty_dict= {}

for i in range(N):
    for j in range(N):
        if i != j:
            r_number = random()
    
            if r_number > 0.3:
                empty_dict[(str(i),str(j))] = 10
            else:
                empty_dict[(str(i),str(j))] = 0   
                
inflow = empty_dict       
   
#print("\nDemand Matrix is the following:", inflow)


nodes = []
               
for i in range(N):
    nodes.append(str(i))
    
print("\nNode list is the following:", nodes)

# Base data
topology = ['Static', 'Optic']

# Cost for triplets commodity-source-destination
cost = {
    ('Static'): 5,
    ('Optic'): 1,
   }


# Create optimization model
m = gp.Model('netflow')

# Create variables
optic_flow = m.addVars( o_arcs, nodes, name="optic_flow", vtype=gp.GRB.INTEGER)
static_flow = m.addVars( s_arcs, nodes,  name="static_flow", vtype=gp.GRB.INTEGER)
matching = m.addVars(o_arcs, name="matching", vtype=gp.GRB.BINARY)

#Objective Function
objective = (cost['Optic'] * gp.quicksum(optic_flow[i,j,s] for i, j in o_arcs for s in nodes) + 
            cost['Static'] * gp.quicksum(static_flow[i,j,s] for i, j in s_arcs for s in nodes))

m.setObjective(objective, GRB.MINIMIZE)

# Arc-capacity constraints
m.addConstrs(
    (optic_flow.sum(i, '*', s) + static_flow.sum(i, '*', s) - 
     optic_flow.sum( '*',i, s) - static_flow.sum( '*', i, s) == inflow[s,i]  
     for i in nodes for s in nodes if  (s!=i )), "balance1")

m.addConstrs(
    (optic_flow.sum(s, '*', s) + static_flow.sum(s, '*', s) - 
     optic_flow.sum( '*',s, s) - static_flow.sum( '*', s, s) == - (gp.quicksum(inflow[s,j] for j in nodes if s!=j)) 
     for  s in nodes ), "balance2")

#m Constraints

m.addConstrs(
    matching.sum('*',j) <= 1 for j in nodes
    )

m.addConstrs(
    matching.sum(j,'*') <= 1 for j in nodes
    )
m.addConstrs(
     (matching[i,j] == matching[j,i] for i,j in o_arcs)
     )

m.addConstrs(
    gp.quicksum(optic_flow[i,j,s] for s in nodes) <= 9999 * matching[i,j] for i, j in o_arcs
    )

"""

for s in nodes:
    for i in nodes:
        for j in nodes:
            if (i,j) in o_arcs:
                gp.quicksum(optic_flow[i,j,s] <= 9999 * matching[i,j])
            else:
                gp.quicksum(optic_flow[i,j,s] ==0)
"""   
                       
# Equivalent version using Python looping
# for i, j in arcs:
#   m.addConstr(sum(flow[h, i, j] for h in topology) <= capacity[i, j],
#               "cap[%s, %s]" % (i, j))


# Alternate version:
# m.addConstrs(
#   (gp.quicksum(flow[h, i, j] for i, j in arcs.select('*', j)) + inflow[h, j] ==
#     gp.quicksum(flow[h, j, k] for j, k in arcs.select(j, '*'))
#     for h in topology for j in nodes), "node")

# Compute optimal solution
m.optimize()
"""
# Print solution
if m.status == GRB.OPTIMAL:
    solution_optic = m.getAttr('x', optic_flow)
    for s in nodes:
        print('\nOptimal flows in optical topologyfor %s:' % s)
        for i, j in o_arcs:
            if solution_optic[ i, j, s] > 0:
                print('%s -> %s: %g' % (i, j, solution_optic[i, j, s]))

if m.status == GRB.OPTIMAL:
    solution_static = m.getAttr('x', static_flow)
    for s in nodes:
        print('\nOptimal flows in static topology for %s:' % s)
        for i, j in s_arcs:
            if solution_static[ i, j, s] > 0:
                print('%s -> %s: %g' % (i, j, solution_static[i, j, s]))

if m.status == GRB.OPTIMAL:
    solution_matching = m.getAttr('x', matching)
    print('\nMatchings:\n')
    for i, j in o_arcs:
        if solution_matching[ i, j] > 0:
            print('%s -> %s: %g' % (i, j, solution_matching[i, j]))
 """           
print(f"Total cost is {round(m.objVal)}.\n\n") 

print("OLD MODEL")

#THEIR MODEL

# Create optimization model
m = gp.Model('netflow')


# 1) Decision variables
path_lengths = m.addVars(inflow.keys(), lb=0.0, vtype=gp.GRB.INTEGER)
matching = m.addVars(o_arcs, vtype=gp.GRB.BINARY)
x = m.addVars(inflow.keys(), inflow.keys(), vtype=gp.GRB.BINARY)
y = m.addVars(inflow.keys(), inflow.keys(), vtype=gp.GRB.BINARY)

# 2) Create constraints
# I-a: only one match via outgoing re-config link per switch[R] for node i
m.addConstrs(
    matching.sum(i,'*') <= 1  for i in nodes
    )
# I-b: only one match via incoming re-config link per switch[R] for node i
m.addConstrs(
    matching.sum('*', i)   <= 1 for i in nodes
    )

# II: Incoming == Outgoing (undirected case only)
m.addConstrs((matching[i, j] == matching[j, i] for i, j in matching))

# III-a: Flow conservation (a: if demand source)
m.addConstrs(
    (x.sum(i, '*', s, t) - x.sum('*', i, s, t) == 1 for s, t in inflow.keys() for i in nodes if s ==i)
)

# III-b: Flow conservation (b: if demand sink)
m.addConstrs(
    (x.sum(i, '*', s, t) - x.sum('*', i, s, t) == -1 for s, t in inflow.keys() for i in nodes if t ==i)
)

# III-c: Flow conservation (c: else)
m.addConstrs(
    (x.sum(i, '*', s, t) - x.sum('*', i, s, t) == 0 for s, t in inflow.keys() for i in nodes if( s !=i and t!=i))
)

# IV: Path cost
path_lengths={}
for start, end in inflow.keys():
    d_val = 0
    for i, j, _, _ in x.keys().select('*','*', start, end):
            d_val += (x[i,j, start, end] - y[i,j, start, end]) * cost['Static'] + y[i,j, start, end] * cost['Optic'] 
    path_lengths[start, end] =d_val
                    

# V-b Matching
m.addConstrs(
    y.sum(i, j, '*', '*') <= 9999 * matching[i, j] for i, j in o_arcs
)

# V-c1 Matching case1: routing is possible in static topology (and probably optical)
m.addConstrs(
    y[i, j, s, t] <= x[i, j, s, t] for i, j, s, t  in y.keys() 
)

# V-c1 Matching case1: routing is possible in static topology (and probably optical)
m.addConstrs(
    y[start, end, i, j] == 0 for start, end, i, j in y.keys() if (start, end) not in o_arcs
)

# V-c2 Matching case2: routing is possible optical topology only
m.addConstrs(
    y[start, end, i, j] == x[start, end, i, j] for start, end, i, j in y.keys() if (start, end) not in s_arcs
)

obj = gp.quicksum(inflow[i, j] * path_lengths[i, j] for i, j in inflow.keys())

m.setObjective(obj, gp.GRB.MINIMIZE)


# Compute optimal solution
m.optimize()

"""
for start, end in arcs:
    for i, j, _, _ in x.keys().select('*','*', start, end):
        print(x[i,j,start,end])
 """       
"""
# Print solution
if m.status == GRB.OPTIMAL:
    solution_optic = m.getAttr('x', y)
    for s,t in inflow.keys():
        print('\nOptimal flows in optical topology from %s to %s:' % (s, t))
        for i, j in inflow.keys():
            if solution_optic[ i, j, s, t] > 0:
                print('%s -> %s: %g' % (i, j, solution_optic[i, j, s,t]))

if m.status == GRB.OPTIMAL:
    solution_static = m.getAttr('x', x)
    for s, t in inflow.keys():
        print('\nOptimal flows in the topology from %s to %s:' % (s,t))
        for i, j in inflow.keys():
            if solution_static[ i, j, s,t] > 0:
                print('%s -> %s: %g' % (i, j, solution_static[i, j, s, t]))

if m.status == GRB.OPTIMAL:
    solution_matching = m.getAttr('x', matching)
    print("\n\nMatchings:\n")
    for i, j in o_arcs:
        if solution_matching[ i, j] > 0:
            print('%s -> %s: %g' % (i, j, solution_matching[i, j]))
"""
    
print(f"Total cost is {round(m.objVal)}.")    