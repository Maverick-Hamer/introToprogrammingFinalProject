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

        