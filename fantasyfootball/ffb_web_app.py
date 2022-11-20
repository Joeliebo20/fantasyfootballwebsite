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
    for t in teams:
        if owner_name == t.owner:
            scores = t.scores[0:current_week]
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


def to_web_app(year, current_week : int, avg_pts, name_to_roster_map):
    home, away = [], []
    st.sidebar.header('User Input Features')
    selected_week = st.sidebar.selectbox('Week', list(reversed(range(1,current_week + 1))))      
    df1, df2 = save_player_data(selected_week)
    box_scores = league.box_scores(selected_week)
    for box_score in box_scores:
        home.append(box_score.home_team)
        away.append(box_score.away_team)
    data = []
    home_team_names = []
    away_team_names = []
    playoff_pct_data = []
    st.title(f'Family Fantasy Football Week {selected_week}, {year} Stats')
    st.markdown("""
    This web app takes data from my ESPN Fantasy Football League and provides data about it
    * Created by Joe Lieberman
    * Code Link: https://github.com/Joeliebo20/fantasyfootballwebsite
    """)
    col1, col2 = st.columns(2)
    col1.header('Home Teams Stats')
    for t in home:
        home_team_names.append(t.owner)
    col1.caption(f"Home Teams this week: {home_team_names}")
    sort = df1.sort_values(by='Points', ascending=False).reset_index(drop=True)
    max_home_player_pts = max(sort['Points'])
    home_max_player = sort['Player'][0]
    
    col1.write(sort)
    col2.header('Away Teams Stats')
    for t in away:
        away_team_names.append(t.owner)
    sort2 = df2.sort_values(by='Points', ascending=False).reset_index(drop=True)
    col2.caption(f'Away teams this week: {away_team_names}')
    max_away_player_pts = max(sort2['Points'])
    away_max_player = sort2['Player'][0]
    col2.write(sort2)

    if max_home_player_pts > max_away_player_pts:
        col1.caption(f'Player with the highest score in week {selected_week} is {home_max_player}, with {max_home_player_pts} pts')
    elif max_away_player_pts > max_home_player_pts:
        col1.caption(f'Player with the highest score in week {selected_week} is {away_max_player}, with {max_away_player_pts} pts')

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
    choice = col2.selectbox('More league data', ['Weekly Matchups', 'League Standings', 'Team Records', 'Adds, Drops, and Trades', 'Best and Worst Week', 'League Scoring Rules', 'Extra League Data and Rules'])
    if choice == 'Weekly Matchups':
        matchups = league.scoreboard(selected_week)
        matchup_data = []
        for matchup in matchups:
            if matchup.home_score > matchup.away_score:
                winner = matchup.home_team.owner
            else:
                winner = matchup.away_team.owner
            matchup_data.append([selected_week, matchup.home_team.owner, matchup.home_score, matchup.away_team.owner, matchup.away_score, winner])
        matchup_df = pd.DataFrame(columns=['Week', 'Home Team', 'Home Score', 'Away Team', 'Away Score', 'Winner'], data=matchup_data)
        st.write(matchup_df)

    elif choice == 'League Standings':
        standings = league.standings()
        s = []
        standing = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th']
        for index, t in enumerate(standings, start=0):
            s.append([t.owner, standing[index]])
        standings_df = pd.DataFrame(columns=['Name', 'Standing'], data=s)
        st.table(standings_df)
    elif choice == 'Team Records':
        records = []
        for t in teams:
            records.append([t.owner, t.wins, t.losses, t.points_for, t.points_against])
        records_df = pd.DataFrame(columns=["Name", "Wins", "Losses", "PF", 'PA'], data=records)
        sorted_records = records_df.sort_values(by='Wins', ascending=False).reset_index(drop=True)
        st.table(sorted_records)
    elif choice == 'Adds, Drops, and Trades':
        data = []
        for t in teams:
            data.append([t.owner, t.acquisitions, t.drops, t.trades])
        other_data_df = pd.DataFrame(columns=['Name', '# of Adds', '# of Drops', '# of Trades'], data=data)
        st.table(other_data_df)
    elif choice == 'Best and Worst Week':
        best = league.top_scored_week()
        worst = league.least_scored_week()
        best_name = best[0].owner
        best_score = best[1]
        worst_name = worst[0].owner
        worst_score = worst[1]
        
        arr1 = [best_name, worst_name]
        arr2 = [best_score, worst_score]
        xLabel = 'Teams'
        yLabel = 'Points Scored'
        st.header(f'Best and Worst scores of the {year} season')
        st.write(f'The best score in the {year} season was {best_score} points from {best_name}')
        st.write(f'The worst score in the {year} season was {worst_score} points from {worst_name}')
        fig = plt.figure(figsize = (10, 7))
        plt.bar(arr1, arr2)
        plt.xlabel(xLabel)
        plt.ylabel(yLabel)
        st.pyplot(fig)
    elif choice == 'League Scoring Rules':
        st.write('For information on league scoring, click the link below:')
        st.write('https://fantasy.espn.com/football/league/settings?leagueId=65345194&view=scoring')
    elif choice == 'Extra League Data and Rules':
        settings = league.settings
        st.write(f'Number of regular season weeks: {settings.reg_season_count}')
        st.write(f'Number of teams: {settings.team_count}')
        st.write(f'Number of playoff teams: {settings.playoff_team_count}')
        st.write(f'Number of veto votes required for trades: {settings.veto_votes_required}')
        # if st.button('League Draft'):

    if col2.button("Other team's average pts per roster"):
        for name, pts in name_to_roster_map.items():
            data.append([name, pts])
        avg_pts_df = pd.DataFrame(columns=['Name', 'Average Points'], data=data)
        sorted = avg_pts_df.sort_values(by='Average Points', ascending=False).reset_index(drop=True)
        st.table(sorted)
    if col1.button('Playoff percentages'):
        for t in home:
            playoff_pct_data.append([t.owner, t.playoff_pct])
        for t in away:
            playoff_pct_data.append([t.owner, t.playoff_pct])
        playoff_pct_df = pd.DataFrame(columns=['Team Name', 'Playoff Pct (%)'], data=playoff_pct_data)
        sorted_df = playoff_pct_df.sort_values(by='Playoff Pct (%)', ascending=False).reset_index(drop=True)
        st.table(sorted_df)





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
    league.refresh()  
    curr_week = league.current_week
    pts, pts_against,avg_pts, rosters = [], [], [], []

    for t in teams:
        pts.append(t.points_for)
    for i in range(len(pts)):
        avg_pts.append(pts[i] / curr_week)
    for count, pts in enumerate(avg_pts, start=0):
        name_to_roster_map[owners[count]] = pts
    
    to_web_app(year, curr_week, avg_pts, name_to_roster_map)

main()
