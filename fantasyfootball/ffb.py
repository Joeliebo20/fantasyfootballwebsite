import espn_api
from espn_api.football import League
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from info import league, owners, league_mates, teams, draft
from datetime import datetime



LEAGUE_ID = 65345194
YEAR = 2022


league = League(LEAGUE_ID, YEAR)

league_mates = ["Joe", "Ryan", "Anthony", "Chris", "Jason", "Matt", 'Andrew', "Colin", "Paula", "Garrett"]
owners = ["Joe Lieberman", "Ryan Lieberman", "Anthony I", "Chris Irving", "Big J", "Matt Lazz", "Andrew Howard", "colin mitchell", "paula lieberman", "Garrett Welch", "Michele Lazzara", "Scott Lazzara"]
league_ids = [1, 2, 3, 4, 5, 7, 9, 10, 11, 12]
teams = league.teams
draft = league.draft

home_data = []
away_data = []

def plot(arr1, arr2, title, xLabel, yLabel):
        
    fig = plt.figure(figsize = (10, 7))
    plt.bar(arr1, arr2)
    plt.title(title)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.show()


def get_scores(current_week : int, owner_name : str):
    for team in teams:
        if owner_name == team.owner:
            scores = team.scores[0:current_week]
    return scores

def get_starters(lineup, team):
    # team is of type team, lineup is of type List[boxPlayers]
    temp, starters = [], []
    counter = 0
    for boxPlayer in lineup:
        if boxPlayer.slot_position != 'BE':
            temp.append(boxPlayer.name)
    for player in team.roster:
        if player.name in temp:
            starters.append(player)
    return starters

def get_player_averages(lineup, team, current_week : int):
    starters = get_starters()
    for player in starters:
        stats = league.player_info(player.name).stats
        points = stats[week]['points']
        # need if they were on bye yet

def split_array(array):
    arr = []
    [arr.append(array[i:i+10]) for i in range(0, len(array)-9, 10)]
    return arr

def get_pts(current_week : int, owner_name : str):
    box_scores = league.box_scores(current_week)
    pts_per_week = []
    # almost there need to fix this function up
    # home_lineup 
    for box_score in box_scores:
        counter = 0
        home_team = box_score.home_team # part of team class
        away_team = box_score.away_team
        if owner_name == home_team.owner:
            home_lineup = box_score.home_lineup
            starters = get_starters(home_lineup, home_team)
            averages = get_player_averages(home_lineup, home_team)
            for player in starters: # this will eventually loop through 'starters'
                sum = 0
                week = 1
                pts = []
                gamesMissed = 0
                bye_week = False
                while week <= current_week:
                    try:
                        if league.player_info(player.name).stats[week]['points'] == 0:
                            gamesMissed += 1
                        pts.append(league.player_info(player.name).stats[week]['points'])
                        week += 1
                    except KeyError:
                        bye_week = True
                        pts.append(0.0)
                        week += 1
        
                for pt in pts:
                    pts_per_week.append(pt)
                
        elif owner_name == away_team.owner:
            away_lineup = box_score.away_lineup
            starters = get_starters(away_lineup, away_team)
            averages = get_player_averages(away_lineup, away_team)
            for player in starters:
                sum = 0
                week = 1
                pts = []
                gamesMissed = 0
                bye_week = False
                while week <= current_week:
                    try:
                        if league.player_info(player.name).stats[week]['points'] == 0:
                            gamesMissed += 1
                        pts.append(league.player_info(player.name).stats[week]['points'])
                        week += 1
                    except KeyError:
                        bye_week = True 
                        pts.append(0.0)
                        week += 1
    
                for pt in pts:
                    pts_per_week.append(pt)
                
                
    return pts_per_week
    
def save_player_data(current_week : int): 
    # saves each team's data into excel
    home_lineups, away_lineups, home_lineup, away_lineup = [], [], [], []
    player_count = 0
    box_scores = league.box_scores(current_week)
    for box_score in box_scores:
        counter = 0
        cntr = 0
        for player in box_score.home_lineup:
            if box_score.home_lineup[counter].slot_position != 'BE':
                home_lineup.append(player)

        for player in box_score.away_lineup:
            if box_score.away_lineup[cntr].slot_position != 'BE':
                away_lineup.append(player)
            cntr += 1

   

    for player in home_lineup: 
        home_data.append([player.name, player.position, player.points]) 
    for player in away_lineup: 
        away_data.append([player.name, player.position, player.points]) 

    home_teams_df = pd.DataFrame(columns=["Player", "Position", "Points"], data=home_data)
    away_teams_df = pd.DataFrame(columns=["Player", "Position", "Points"], data=away_data)    
        
    home_teams_df.to_excel('homeffb.xlsx', sheet_name='Home Teams') # store weekly data in a dataframe
    away_teams_df.to_excel('awayffb.xlsx', sheet_name='Away Teams')


    
def linear_model(x, y, current_week : int, owner_name : str):
    # x will be array of averages from each starter, y will be average points scored weekly
    # x  = [[18.416, 15.86, 13.41, 17.45, 7.3, 21.608, 7.7, 8.85, 6.2]]
    # y = [124.56] points per week
    print(f"{owner_name}'s team")
    x, y = np.array(x), np.array(y)
    x_train, x_test, y_train, y_test = train_test_split(np.transpose(x), y, test_size=0.1)
    model = LinearRegression()
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    print(f"Prediction for next week: {pred}")
    score = mean_squared_error(y_test, pred)
    print(f"Mean Squared Error: {score}")


        
def main(): # refresh gets newest league data, call every week
    today = datetime.now()
    if today.isoweekday() > 4:
        league.refresh()  
    print(f"The current NFL week: is {league.current_week}. Please enter: {league.current_week}")  
    curr_week = int(input("Current week: "))
    pts, pts_against,avg_pts, rosters = [], [], [], []
    for id in league_ids:
        pts.append(league.get_team_data(id).points_for)
        rosters.append(league.get_team_data(id).roster)
    for i in range(len(pts)):
        avg_pts.append(pts[i] / curr_week)
    # plot(league_mates, avg_pts, "Average pts per roster", "Rosters", 'Average Pts')
    save_player_data(curr_week)
    team_scores = get_scores(curr_week, owners[2])
    player_avgs = get_pts(curr_week, owners[2])
    player_pts = split_array(player_avgs)
    linear_model(player_pts, avg_pts, curr_week, teams[2].owner)
    
    
main()