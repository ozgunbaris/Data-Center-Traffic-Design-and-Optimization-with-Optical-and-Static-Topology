#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 20:01:21 2021

@author: ozgunbaris
"""

import math

def ReconfigDijkstra(start:int,end:int,M:list,links:list):
    N = M.copy()
    permanent_labeled = {start:[0,[start], False, {}]}
    
    temp_labeled = {}
    previous_dict ={}
    
    for i in N:
        if i not in permanent_labeled.keys():
            temp_labeled[i]= [math.inf,[], False,{}]
    current = start
    
    while(end not in permanent_labeled.keys()):
        dummy = 0
        to_be_deleted=[]
        """
        for j in temp_labeled.keys():
            for i in links:
                if i[1]== j:
                    dummy += 1
            if dummy == 0 and temp_labeled[j] != math.inf:
                permanent_labeled[j] = temp_labeled[j]
                to_be_deleted.append(j)
                
        for k in to_be_deleted:
            del temp_labeled[current]
            
         """   
        links_new = links.copy()
        
        for i in links_new:
            if i[1] in permanent_labeled.keys() and i in links:
                links.remove(i)
                
            else:
                if i[0] == current:
                    if temp_labeled[i[1]][0] > i[2] + permanent_labeled[i[0]][0]:
                        
                        temp_labeled[i[1]][0] = i[2] + permanent_labeled[i[0]][0]
                        temp_labeled[i[1]][1] = permanent_labeled[i[0]][1] + [i[1]] 
                        links.remove(i)
                        
                        if i[3] or permanent_labeled[i[0]][2]:
                            temp_labeled[i[1]][2] = True
                            
                            if i[4] in previous_dict.keys():
                                previous_dict[i[4]] = previous_dict[i[4]] + [[i[0],i[1]]]
                            
                            else:
                                if i[4] != None:
                                    temp_labeled[i[1]][3][i[4]] = [[i[0],i[1]]]
                                
                            temp_labeled[i[1]][3] = {k: v for d in (temp_labeled[i[1]][3], previous_dict) for k, v in d.items()}

                            for j in links:
                                if j[0] == i[1] and j[3] and j in links and j[4] == i[4]:
                                    links.remove(j)
       
                    elif temp_labeled[i[1]][0] <= i[2] + permanent_labeled[i[0]][0]:
                        links.remove(i)
                        
        first_values = [first[0] for first in temp_labeled.values()] 
        current = [key for key in temp_labeled.keys() if temp_labeled[key][0] == min(first_values)][0]
        permanent_labeled[current] = temp_labeled[current]
        previous_dict = temp_labeled[current][3]
        del temp_labeled[current]
        #print(current)
        #print(permanent_labeled)
        #print(temp_labeled,"\n")
    #print(permanent_labeled)
    return permanent_labeled[end]