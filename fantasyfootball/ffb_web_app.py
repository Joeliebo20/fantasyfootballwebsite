import espn_api
from espn_api.football import League
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from info import league, owners, league_mates, teams, draft, league_ids
from datetime import datetime
import streamlit as st

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


def to_web_app(df1, df2, year, current_week : int, avg_pts, name_to_roster_map, home, away):
    data = []
    home_team_names = []
    away_team_names = []
    playoff_pct_data = []
    st.title(f'Family Fantasy Football Week {current_week}, {year} Stats')
    st.markdown("""
    This web app takes data from an ESPN Fantasy Football League and creates a webpage out of it
    """)
    col1, col2 = st.columns(2)
    col1.header('Home Teams Stats')
    for team in home:
        home_team_names.append(team.owner)
    col1.caption(f"Home Teams this week: {home_team_names}")
    sort = df1.sort_values(by='Points', ascending=False)
    col1.write(sort)
    col2.header('Away Teams Stats')
    for team in away:
        away_team_names.append(team.owner)
    sort2 = df2.sort_values(by='Points', ascending=False)
    col2.caption(f'Away teams this week: {away_team_names}')
    col2.write(sort2)

    if col1.button('Average Points Per Roster Graph'):
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
    if col2.button("Other team's average pts per roster"):
        for name, pts in name_to_roster_map.items():
            data.append([name, pts])
        avg_pts_df = pd.DataFrame(columns=['Name', 'Average Points'], data=data)
        sorted = avg_pts_df.sort_values(by='Average Points', ascending=False)
        st.write('Numbers on the left are corresponding team ids - the order in which a player joined the league')
        st.caption('For example - 0 corresponds to Joe, who joined the league first.')
        st.table(sorted)
    if col1.button('Playoff percentages'):
        for team in home:
            playoff_pct_data.append([team.owner, team.playoff_pct])
        for team in away:
            playoff_pct_data.append([team.owner, team.playoff_pct])
        playoff_pct_df = pd.DataFrame(columns=['Team Name', 'Playoff Pct (%)'], data=playoff_pct_data)
        sorted_df = playoff_pct_df.sort_values(by='Playoff Pct (%)', ascending=False)
        st.table(sorted_df)
    choice = col2.selectbox('Other data', ['League Standings', 'Team Records'])
    if choice == 'League Standings':
        standings = league.standings()
        s = []
        standing = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th']
        for index, team in enumerate(standings):
            s.append([team.owner, standing[index]])
        standings_df = pd.DataFrame(columns=['Name', 'Standing'], data=s)
        st.table(standings_df)
    elif choice == 'Team Records':
        records = []
        for team in teams:
            records.append([team.owner, team.wins, team.losses])
        records_df = pd.DataFrame(columns=["Name", "Wins", "Losses"], data=records)
        sorted_records = records_df.sort_values(by='Wins', ascending=False)
        st.table(sorted_records)





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
    pts, pts_against,avg_pts, rosters, home_teams, away_teams = [], [], [], [], [], []
    box_scores = league.box_scores(curr_week)
    for box_score in box_scores:
        home_teams.append(box_score.home_team)
        away_teams.append(box_score.away_team)
        # fix this get every single teams data (aunt michele and uncle scott)
        # prob do boxScore
    for team in teams:
        pts.append(team.points_for)
    for i in range(len(pts)):
        avg_pts.append(pts[i] / curr_week)
    for count, pts in enumerate(avg_pts, start=0):
        name_to_roster_map[owners[count]] = pts
    
    df1, df2 = save_player_data(curr_week)
    to_web_app(df1, df2, year, curr_week, avg_pts, name_to_roster_map, home_teams, away_teams)

main()
