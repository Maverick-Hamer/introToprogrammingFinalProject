'''
My final Project

A world cup outcome simulator with data based out comes

'''

#sources 
#Maverick Hamer
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
from WorldCupGroup import WorldCupGroup
from GoHomeRounds import WorldCupKnockOut
import scipy.stats
from Match import WorldCupMatch



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


#sources
# for world cup (see http://www.eloratings.net/about)
# has the team strenghth data

class WorldCupMatch(object):
    def __init__(self,team1,team2):
        self.played = False
        self.penalties = False
        self.team1 = team1
        self.team2 = team2
        self.eloK = 60 # for world cup (see http://www.eloratings.net/about)
        self.run_change = True
        self.elo_only_model()
        
    def __repr__(self,name):
        if self.played:
            return "Match %s %s vs %s %s"  (self.team1.name, self.team1_goals, self.team2_goals, self.team2.name)
        else:
            return "Match %s vs %s."  (self.team1.name, self.team2.name)
        
    def elo_only_model(self):
        self.const = 0.1557
        self.xe = 0.169 # coeff elo_diff / 100
        self.eloHA = 0.182/self.xe*100
     # get regression coefficient in units of elo difference
        self.model = "Elo"
            
    def set_group_stats(self,team1_goals, team2_goals, stage, group_matches):
        # update 
        self.played = True
        if stage=='GRP':
           self.team1.group_matches += 1
        self.team1.total_matches += 1
        self.team2.total_matches += 1
        self.team1_goals = team1_goals
        self.team2_goals = team2_goals
        self.team1.goals_for += team1_goals
        self.team1.goals_against += team2_goals
        self.team2.goals_for += team2_goals
        self.team2.goals_against += team1_goals       
        self.team1.goal_dif = self.team1.goals_for - self.team1.goals_against
        self.team2.goal_dif = self.team2.goals_for - self.team2.goals_against   
        if self.team1_goals > self.team2_goals:
            self.winner = self.team1
            if stage=='GRP':
                self.team1.points += 3                        
        elif self.team1_goals < self.team2_goals:
            self.winner = self.team2            
            if stage=='GRP':
                self.team2.points += 3
        else:
            if stage=='GRP':
                self.team1.points += 1
                self.team2.points += 1
     
    
    def generate_result(self,stage,penalties=False,verbose=False):
        # Does one team have home advantage (i.e. the host)?
        if self.team1.host:
            HA = self.eloHA
        elif self.team2.host:
            HA = -self.eloHA
        else:
            HA = 0.0
        assert not (self.team1.host and self.team2.host)
        # Elo differences, including home advantage effect
        elo_diff = self.team1.elorank - self.team2.elorank + HA
        # Select model & calculated Poisson means
        if self.model=="Elo": 
            mu1 = float(np.exp( self.const + elo_diff*self.xe/100 ))
            mu2 = float(np.exp( self.const - elo_diff*self.xe/100 ))
        # Draw goals from Poisson distribution
        team1_goals = int(scipy.stats.poisson.rvs(mu1,size=1))
        team2_goals = int(scipy.stats.poisson.rvs(mu2,size=1))
        if verbose:
            print; "%s %d vs %d %s" % (self.team1.name, team1_goals, team2_goals, self.team2.name)
            print;"Mus: %1.1f, %1.1f" % (mu1,mu2)
            print;"Elos: %1.1f, %1.1f" % (self.team1.elorank,self.team2.elorank)
        # Update group stats
        self.set_group_stats(team1_goals,team2_goals,stage)
        # Simulate penalty shoot-out if necessary
        if penalties and team1_goals==team2_goals: 
            self.penalty_shootout()
        # Finally, update elo score for each team if running 'change'
        if self.run_change:
            self.update_elo_scores_ELORATING( team1_goals-team2_goals, elo_diff)
        if verbose:
            print; "Elos: %1.1f, %1.1f" % (self.team1.elorank,self.team2.elorank)


    def update_elo_scores_ELORATING(self, goal_diff, elo_diff):
        # see http://www.eloratings.net/about
        if np.abs( goal_diff ) == 2:
            K = self.eloK * 1.5
        elif np.abs( goal_diff ) > 2:
            K = self.eloK * (1.75 + ( np.abs( goal_diff ) - 3 ) / 8. )
        else:
            K = self.eloK
        W = 1. if goal_diff>0 else 0. if goal_diff<0 else 0.5
        We = 1. / ( 10**(-1.*elo_diff/400.) + 1. )        
        self.team1.elorank += K * (W-We)
        self.team2.elorank += K * (We-W)


    def penalty_shootout(self, penaltyskill,Ninit = 5):
        # generate 5 penalties each and check against skill
        self.penaltyskill
        self.penalties = True
        team1_success = np.sum(np.random.uniform(size=Ninit)<=self.team1.penaltyskill)
        team2_success = np.sum(np.random.uniform(size=Ninit)<=self.team2.penaltyskill)
        if team1_success > team2_success:
            self.winner = self.team1
        elif team1_success < team2_success:
            self.winner = self.team2
        else: # determine winner based on penalty strenghts
            high = self.team1.penaltyskill + self.team2.penaltyskill
            if np.random.uniform(size=1,high=high)<self.team1.penaltyskill:
                self.winner = self.team1
            else:
                self.winner = self.team2




class WorldCupKnockOut(object):
    def __init__(self,groups):
        self.groups = groups
        
    def simulate_Round16_matches(self,simall=False):
        if simall: [m.generate_result('R16',penalties=True) for m in self.R16matches]
        else: [m.generate_result('R16',penalties=True) for m in self.R16matches if not m.played] 
        
    def simulate_QF_matches(self,simall=False):
        if simall: [m.generate_result('QF',penalties=True) for m in self.QFmatches]
        else: [m.generate_result('QF',penalties=True) for m in self.QFmatches if not m.played]  
        
    def simulate_SF_matches(self,simall=False):
        if simall: [m.generate_result('SF',penalties=True) for m in self.SFmatches]
        else: [m.generate_result('SF',penalties=True) for m in self.SFmatches if not m.played]          
        
    def simulate_Final(self):
        [m.generate_result('Final',penalties=True) for m in self.Final]
        
    def Round16(self):
        # Set up Round of 16 matches based on groups
        self.R16matches = []
        self.R16teamnames = []
        self.GroupWinners = []
        self.R16matches.append(WorldCupMatch(self.groups[0].winner,self.groups[1].runner)) #1A vs 2B
        self.R16matches.append(WorldCupMatch(self.groups[2].winner,self.groups[3].runner)) #1C vs 2D
        self.R16matches.append(WorldCupMatch(self.groups[1].winner,self.groups[0].runner)) #1B vs 2A
        self.R16matches.append(WorldCupMatch(self.groups[3].winner,self.groups[2].runner)) #1D vs 2C
        self.R16matches.append(WorldCupMatch(self.groups[4].winner,self.groups[5].runner)) #1E vs 2F
        self.R16matches.append(WorldCupMatch(self.groups[6].winner,self.groups[7].runner)) #1G vs 2H
        self.R16matches.append(WorldCupMatch(self.groups[5].winner,self.groups[4].runner)) #1F vs 2E
        self.R16matches.append(WorldCupMatch(self.groups[7].winner,self.groups[6].runner)) #1H vs 2G
        # Record group winners and round of 16 team names (for metrics)
        for group in self.groups:
            self.GroupWinners.append(group.winner.name)
        for m in self.R16matches:
            self.R16teamnames.append(m.team1.name)
            self.R16teamnames.append(m.team2.name)
    
    def ManuallySetRound16(self,R16teams):
        # Manually set Round of 16 matches
        self.R16matches = []
        self.R16teamnames = []
        for i in np.arange(0,15,step=2):
            self.R16matches.append( WorldCupMatch(R16teams[i], R16teams[i+1] ) )
        for m in self.R16matches:
            self.R16teamnames.append(m.team1.name)
            self.R16teamnames.append(m.team2.name)
    
    def QuarterFinal(self):
        # Quarter Final Matches
        self.QFmatches = []
        self.QFteamnames = []
        self.QFmatches.append(WorldCupMatch( self.R16matches[0].winner, self.R16matches[1].winner) ) # 1A/2B vs 1C/2D
        self.QFmatches.append(WorldCupMatch( self.R16matches[2].winner, self.R16matches[3].winner) ) # 1B/2A vs 1D/2C
        self.QFmatches.append(WorldCupMatch( self.R16matches[4].winner, self.R16matches[5].winner) ) # 1E/2F vs 1G/2H
        self.QFmatches.append(WorldCupMatch( self.R16matches[6].winner, self.R16matches[7].winner) ) # 1F/2E vs 1H/2G
        for m in self.QFmatches:
            self.QFteamnames.append(m.team1.name)
            self.QFteamnames.append(m.team2.name)
        
    def SemiFinal(self):
        # Semi final matches
        self.SFmatches = []
        self.SFteamnames = []
        self.SFmatches.append(WorldCupMatch( self.QFmatches[0].winner, self.QFmatches[2].winner) ) # 1A/2B/1C/2D vs 1E/2F/1G/2H
        self.SFmatches.append(WorldCupMatch( self.QFmatches[1].winner, self.QFmatches[3].winner) ) # 1B/2A/1D/2C vs 1F/2E/1H/2G
        for m in self.SFmatches:
            self.SFteamnames.append(m.team1.name)
            self.SFteamnames.append(m.team2.name)
    
    def Final(self):
        # Final
        self.Final = [WorldCupMatch( self.SFmatches[0].winner, self.SFmatches[1].winner)]
        self.Finalteamnames = [self.Final[0].team1.name, self.Final[0].team2.name]
    
        
    def print_matches(self,matches):
        print
        for m in matches:
            if m.played:
                if m.penalties:
                    print; m.__repr__() + " --->  %s wins on penalties." % (m.winner.name)
                else:
                    print; m.__repr__() + " --->  %s wins." % (m.winner.name)
            else:
                print; m 



class WorldCupSim(object):
    def __init__(self,group_names,teams,verbose):
        self.group_names = group_names
        self.teams = teams
        self.groups = []
        self.verbose = verbose
        
    def runsim(self):
        # Run full World Cup Sim
        # Put teams in groups
        for g in self.group_names:
            group_teams = [t for t in self.teams if t.group==g]
            self.groups.append(WorldCupGroup(g,group_teams))
        # Simulation group matches
        for g in self.groups:
            g.simulate_group_matches()
            if self.verbose:
                g.print_matches()
                g.print_table()
        # BUild knock-out stage of tournament
        self.KnockOut = WorldCupKnockOut(self.groups)
        # ROUND OF 16
        self.KnockOut.Round16()
        self.KnockOut.simulate_Round16_matches()
        if self.verbose:        
            self.KnockOut.print_matches(self.KnockOut.R16matches)
        # Quarter Finals
        self.KnockOut.QuarterFinal()
        self.KnockOut.simulate_QF_matches()
        if self.verbose:
            self.KnockOut.print_matches(self.KnockOut.QFmatches)
        # Semi Finals
        self.KnockOut.SemiFinal()
        self.KnockOut.simulate_SF_matches()
        if self.verbose:        
            self.KnockOut.print_matches(self.KnockOut.SFmatches)
        # Final
        self.KnockOut.Final()
        self.KnockOut.simulate_Final()
        if self.verbose:
            self.KnockOut.print_matches(self.KnockOut.Final)