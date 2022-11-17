import espn_api
from espn_api.football import League
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from info import league, owners, league_mates, teams, draft, league_ids
from datetime import datetime
import streamlit as st
import base64


home_data = []
away_data = []
    

def get_scores(current_week : int, owner_name : str):
    for team in teams:
        if owner_name == team.owner:
            scores = team.scores[0:current_week]
    return scores


def split_array(array):
    arr = []
    [arr.append(array[i:i+9]) for i in range(0, len(array)-8, 9)]
    return arr

def write_to_excel(df, df1):
    writer = pd.ExcelWriter('homeffb.xlsx')
    df.to_excel(writer, sheet_name='Home Teams')
    df1.to_excel(writer, sheet_name='Away Teams')
    writer.save()


def to_web_app(df1, df2, year, current_week : int, avg_pts, name_to_roster_map):
    # select_box = st.selectbox()
    home = False
    st.title(f'Fantasy Football Week {current_week}, {year} Stats')
    st.markdown("""
    This web app takes data from an ESPN Fantasy Football League and creates a webpage out of it
    """)
    col1, col2 = st.columns(2)
    col1.header('Home Teams Stats')
    sort = df1.sort_values(by='Points', ascending=False)
    col1.write(sort)
    col2.header('Away Teams Stats')
    sort2 = df2.sort_values(by='Points', ascending=False)
    col2.write(sort2)

    if st.button('Average Points Per Roster Graph'):
        max_pts = max(avg_pts)
        min_pts = min(avg_pts)
        for key in name_to_roster_map.keys():
            if name_to_roster_map[key] == max_pts:
                max_name = key
            if name_to_roster_map[key] == min_pts:
                min_name = key
        arr1 = league_mates
        arr2 = avg_pts
        xLabel = 'Rosters'
        yLabel = 'Average Points'
        st.header('Average Points Per Roster(Season)')
        st.write(f'{max_name} has averaged the most points per week : {max_pts}')
        st.write(f'{min_name} has averaged the least points per week : {min_pts}')
        fig = plt.figure(figsize = (10, 7))
        plt.bar(arr1, arr2)
        plt.xlabel(xLabel)
        plt.ylabel(yLabel)
        st.pyplot(fig)





def save_player_data(current_week : int): 
    # saves each team's data into excel
    home_lineups, away_lineups, home_lineup, away_lineup = [], [], [], []
    player_count = 0
    box_scores = league.box_scores(current_week)
    for box_score in box_scores:
        for player in box_score.home_lineup:
            if player.slot_position != 'BE' and player.slot_position != 'IR':
                home_lineup.append(player)

    for box_score in box_scores:
        for player in box_score.away_lineup:
            if player.slot_position != 'BE' and player.slot_position != 'IR':
                away_lineup.append(player)

   
    home_data = split_array(home_lineup)
    away_data = split_array(away_lineup)


    x = []
    y = []

    for fantasy_team in home_data:
        for index, player in enumerate(fantasy_team):
            x.append([current_week, player.proTeam, player.name, player.position, player.points])

    for fantasy_team in away_data:
        for index, player in enumerate(fantasy_team):
            y.append([current_week, player.proTeam, player.name, player.position, player.points])

    df1 = pd.DataFrame(columns=['Week', 'Team', 'Player', 'Position', 'Points'], data=x)
    df2 = pd.DataFrame(columns=['Week', 'Team', 'Player', 'Position', 'Points'], data=y)  
        
    write_to_excel(df1, df2)
    return (df1, df2)

def main(): # refresh gets newest league data, call every week
    today = datetime.now()
    year = datetime.now().year
    name_to_roster_map = {}
    if today.isoweekday() > 4: # if it is thursday or friday, refresh
        league.refresh()  
    curr_week = league.current_week
    pts, pts_against,avg_pts, rosters = [], [], [], []
    for id in league_ids:
        pts.append(league.get_team_data(id).points_for)
        rosters.append(league.get_team_data(id).roster)
    for i in range(len(pts)):
        avg_pts.append(pts[i] / curr_week)
    for count, pts in enumerate(avg_pts):
        name_to_roster_map[league_mates[count]] = pts
    
    df1, df2 = save_player_data(curr_week)
    to_web_app(df1, df2, year, curr_week, avg_pts, name_to_roster_map)

main()