#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 10:03:46 2021

@author: ozgunbaris
"""

import gurobipy as gp
from gurobipy import GRB

#from Pseudo_Random_Generator import *

from random import random, randrange, sample, randint
import ReconfigDijkstra

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
            
            if r_number > 0.8:
                empty.append((str(i),str(j)))
                empty.append((str(j),str(i))) #If topology is undirected alter this line!
             
                
s_arcs = empty.copy()       
   
#print("Static Topology is the following:", s_arcs)
#print("Number of static arcs:", (len(s_arcs)/2))

#Updating the static topology for ReconfigDijkstra
s_arcs_with_weight=[]
for i in s_arcs:
    empty=[]
    empty.append(int(i[0]))
    empty.append(int(i[1]))
    empty.append(5)
    empty.append(False)
    empty.append(None)
    s_arcs_with_weight.append(empty)
    

#Demand Generator

empty_dict= {}

for i in range(N):
    for j in range(N):
        if i != j:
            r_number = random()
    
            if r_number > 0.6:
                empty_dict[i,j] = randint(1,10)
            else:
                empty_dict[i,j] = 0 
                
demand_matrix = empty_dict

print("\nDemand Matrix is the following:", demand_matrix)             



nodes = []
               
for i in range(N):
    nodes.append(i)
    
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

#print("\nGeneral list is the following:",general_optic,"\n")

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
print(all_links)
all_links_1 = all_links.copy()
s_arcs_with_weight_1 = s_arcs_with_weight.copy()

"""
all_links_new=[]
for i in range(int(len(all_links)/2)):
    if all_links[2*i][0] > all_links[2*i +1][0]:
        all_links_new.append(all_links[2*i +1])
    else:
        all_links_new.append(all_links[2*i])
        
"""
   
#print(all_links_new)
"""
start = 5
end = 1

shortest = ReconfigDijkstra.ReconfigDijkstra(start, end, nodes, all_links)
print('Shortest distance bewtween node {} and {} is'.format(start, end), shortest[0], 'by passing nodes', shortest[1])



all_links = all_links_1
start = 5
end = 2

shortest = ReconfigDijkstra.ReconfigDijkstra(start, end, nodes, all_links)
print('Shortest distance bewtween node {} and {} is'.format(start, end), shortest[0], 'by passing nodes', shortest[1])
"""

#Create values dictionary according to the demand
total_cost = 0

while( len(demand_matrix.keys()) > 0):  
    values = {}
    demand_matrix_1 = demand_matrix.copy()
    
    for l in demand_matrix_1:
        if demand_matrix_1[l] == 0:
            del demand_matrix[l]
    
    for d in demand_matrix.keys():
        
        if demand_matrix[d] > 0:
            start = d[0]
            end = d[1]
            
            all_links = all_links_1.copy()
            s_arcs_with_weight = s_arcs_with_weight_1.copy()
            
            static_shortest = ReconfigDijkstra.ReconfigDijkstra(start, end, nodes, s_arcs_with_weight)
            total_cost_static = static_shortest[0] * demand_matrix[d]
        
            shortest = ReconfigDijkstra.ReconfigDijkstra(start, end, nodes, all_links)
            total_cost_matching = shortest[0] * demand_matrix[d]
            
            gain = total_cost_static - total_cost_matching
            
            values[(start,end)] = gain
        
            
    print('Demand Matrix:',demand_matrix)
    print(values)
    
    #Sorting the Values Dict(Gains)
    sorted_values = sorted(values.values(), reverse=True) # Sort the values
    sorted_dict = {}
    
    for ic in sorted_values:
        for kc in values.keys():
            if values[kc] == ic:
                sorted_dict[kc] = values[kc]
                break
    
    gain_matrix = sorted_dict       
       
    print("\nGain Matrix(sorted) is the following:", gain_matrix)
        
    #Finding the maximum(first) entry in values
    for kt in gain_matrix.keys():
        if gain_matrix[kt] > 0:
            start = kt[0]
            end = kt[1]
        del demand_matrix[kt]
        break
        
    all_links = all_links_1.copy()
    
    shortest = ReconfigDijkstra.ReconfigDijkstra(start, end, nodes, all_links)
    
    if shortest[2]:
        print('Shortest distance bewtween node {} and {} is'.format(start, end), shortest[0], 'by passing nodes', shortest[1],'and using optical switches',shortest[3])
        
        all_links_2 = all_links_1.copy()
        
        for i in all_links_2:
            if i[3]:
                for matching in shortest[3].keys():
                    for k in range(len(shortest[3][matching])):
                        if (i[0] == shortest[3][matching][k][0] and i[1] == shortest[3][matching][k][1]) or (i[1] == shortest[3][matching][k][0] and i[0] == shortest[3][matching][k][1]):
                            pass
                        elif i[0] == shortest[3][matching][k][0] and matching == i[4]:
                            all_links_1.remove(i)
                        elif i[0] == shortest[3][matching][k][1] and matching == i[4]:
                            all_links_1.remove(i)
                        elif i[1] == shortest[3][matching][k][0] and matching == i[4]:
                            all_links_1.remove(i)
                        elif i[1] == shortest[3][matching][k][1] and matching == i[4]:
                            all_links_1.remove(i) 
        
    else:
        print('Shortest distance bewtween node {} and {} is'.format(start, end), shortest[0], 'by passing nodes', shortest[1])
    
    total_cost = total_cost + gain_matrix[kt] * shortest[0]
        
print('Total cost is: ', total_cost)
