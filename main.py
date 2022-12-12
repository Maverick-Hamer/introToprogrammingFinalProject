'''
My final Project

'''

#sources 
#Piero Paialunga
#https://towardsdatascience.com/2022-world-cup-simulator-using-data-science-with-python-6bf56a543436
#http://www.eloratings.net/about
#file path to add libraries 
#C:\Users\Maverick.Hamer24\AppData\Local\Programs\Python\Python310\Scripts
#imported libraries 
import numpy as np
from WorldCupTeam import WorldCupTeam
from Simulation import WorldCupSim
import copy as copy
import pandas as pd
import scipy as scipy



class WorldCupTeam(object):
    def __init__(self, group,name,seed,hostname,strength,group_matches,total_matches,points,goals_for,goals_against):
       # Name means the country name
        self.name = name 
        self.group = group
        self.seed = seed
        self.hometeam = name=='Qatar'
        self.group_matches = 0
        self.total_matches = 0
        self.points = 0
        self.goals_for = 0
        self.goals_against = 0
        self.host = self.name == hostname
        self.strength = 0
        
              
        
    def __repr__(self):
        return "%s, %s, %s" % (self.name,self.group,)
