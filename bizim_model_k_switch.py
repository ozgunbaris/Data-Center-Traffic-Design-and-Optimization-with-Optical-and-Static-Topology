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

from random import random, randrange, sample


N = int(input("Enter the number of nodes:"))
switch_input = int(input("How many switch there are in the topology?:"))

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
    #print(nodes_not_added)
    
#print(connected)

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
   
print("Static Topology is the following:", s_arcs)
print("Number of static arcs:", (len(s_arcs)/2))

#Updating the static topology for ReconfigDijkstra
s_arcs_with_weight=[]
for i in s_arcs:
    empty=[]
    empty.append(int(i[0]))
    empty.append(int(i[1]))
    empty.append(5)
    empty.append(False)
    s_arcs_with_weight.append(empty)
    

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
   
print("\nDemand Matrix is the following:", inflow)


nodes = []
               
for i in range(N):
    nodes.append(str(i))
    
print("\nNode list is the following:", nodes)



switches = [x for x in range(switch_input)]
print("\nSwitch list is the following:",switches,"\n")

#Optic Topology Generator
general_optic = []
for k in switches:
    empty=[]
    
    optic_set = sample(nodes,randrange(1,len(nodes)))
    
    for i in optic_set:
        for j in optic_set:
            if i != j and i < j: # If topology is not indirected alter this line!
                empty.append((str(i),str(j)))
                empty.append((str(j),str(i))) # If topology is not indirected alter this line!
                 
    general_optic.append(empty)

print("\nGeneral list is the following:",general_optic,"\n")

#Updating the static topology for ReconfigDijkstra
o_arcs_with_weight=[]
for k in range(len(general_optic)):
    for i in general_optic[k]:
        empty=[]
        empty.append(int(i[0]))
        empty.append(int(i[1]))
        empty.append(1)
        empty.append(True)
        empty.append(k)
        o_arcs_with_weight.append(empty)
        
#All links for ReconfigDijkstra
all_links = s_arcs_with_weight + o_arcs_with_weight 

#print(s_arcs_with_weight,"\n") 
#print(o_arcs_with_weight,"\n")
     
#Create the list with all possible optic arcs
o_arcs = []

for i in general_optic:
    for j in o_arcs:
        for k in i:
            if j == k:
                i.remove(k)
    o_arcs = o_arcs + i    

print("\nAll optic list is the following:",o_arcs,"\n")

#print("\nOptic Topology is the following:", o_arcs)            
print("Number of optic arcs:", (len(o_arcs)/2))

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
matching = m.addVars(o_arcs, switches, name="matching", vtype=gp.GRB.BINARY)

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
    matching.sum('*',j,t) <= 1 for j in nodes for t in switches
    )

m.addConstrs(
    matching.sum(j,'*',t) <= 1 for j in nodes for t in switches
    )
m.addConstrs(
     (matching[i,j,t] == matching[j,i,t] for i,j in o_arcs for t in switches)
     )

m.addConstrs(
    gp.quicksum(optic_flow[i,j,s] for s in nodes) <= 9999 * gp.quicksum(matching[i,j,t] for t in switches )for i, j in o_arcs
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