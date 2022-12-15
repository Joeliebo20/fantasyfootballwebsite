import espn_api
from espn_api.football import League
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from info import *
from datetime import datetime
import streamlit as st
from PIL import Image



def get_starters(lineup, team):
    '''
    This function gets a team's "starting 9" players and returns them
    '''
    temp, starters = [], []
    counter = 0
    for boxPlayer in lineup:
        if boxPlayer.slot_position != 'BE' and boxPlayer.slot_position != 'IR':
            temp.append(boxPlayer.name)
    for player in team.roster:
        if player.name in temp:
            starters.append(player)
    return starters
    

def get_scores(current_week : int, owner_name : str):
    '''
    This function returns a team's weekly scores
    '''
    for t in teams:
        if owner_name == t.owner:
            scores = t.scores[0:current_week]
    return scores

def get_playoff_teams(home, away):
    '''
    This function returns an array of the playoff teams
    '''
    pcts = dict()
    playoff_tms = list()
    for team in teams:
        pcts[team.owner] =  float(team.playoff_pct)
    # for t in away:
    #     pcts[t.owner] =  float(t.playoff_pct)
    for team in teams:
        if pcts[team.owner] > 0:
            playoff_tms.append(team.owner)
    return playoff_tms


def split_array(array):
    '''
    This function splits an array of every player into teams (9 players)
    '''
    arr = []
    for i in range(0, len(array) - 8, 9):
        arr.append(array[i:i+9])
    return arr

def write_to_excel(df, df1):
    '''
    This function writes player data to an excel spreadsheet
    '''
    writer = pd.ExcelWriter('homeffb.xlsx')
    df.to_excel(writer, sheet_name='Home Teams')
    df1.to_excel(writer, sheet_name='Away Teams')
    writer.save()

def predict_final_rankings(map, pcts):
    '''
    This function predicts rhe league winnner using power rankings, playoff percent, and points for
    '''
    power_rankings = league.power_rankings()
    scores = dict()
    data = list()
    predicted_final_rankings = list()
    for rank in power_rankings:
        scores[rank[1].owner] = float(rank[0])
        # key = name, value = power_rank

    for owner, pts in map.items():
        data.append([owner, pts])
    df = pd.DataFrame(columns=['Owner', 'Pts'], data=data)
    sorted_df = df.sort_values(by='Pts', ascending=False).reset_index(drop=True)
    # top 3 teams get better point multipliers
    highest_scoring_pts = [1.6, 1.5, 1.5, .85, .8, .75, .7, .65, .6, .55, .50, .45]
    highest_scoring_weights = dict()
    for i, team in enumerate(teams):
        if sorted_df['Owner'][i] not in highest_scoring_weights:
            highest_scoring_weights[sorted_df['Owner'][i]] = highest_scoring_pts[i]
    for team in teams:
        weight = highest_scoring_weights[team.owner]
        power_rank_score = scores[team.owner] / 100
        playoff_pct = pcts[team.owner] / 100
        score = weight * power_rank_score * playoff_pct
        predicted_final_rankings.append([team.owner, score * 100])
    predicted_df = pd.DataFrame(columns=['Team', 'Calculated score'], data=predicted_final_rankings)
    sorted_df = predicted_df.sort_values(by='Calculated score', ascending=False).reset_index(drop=True)
    pred_winner = sorted_df['Team'][0]
    return (sorted_df, pred_winner)
    
    



def main_page(year, current_week : int, avg_pts, name_to_roster_map):
    '''
    This function constructs ths streamlit web app
    '''
    img = Image.open('fantasyfootball/FFL-Logo.webp')
    img.load()
    st.image(img)
    st.sidebar.header('User Input Features')
    selected_week = st.sidebar.selectbox('Week', list(reversed(range(1,current_week + 1))))     
    df1, df2 = save_player_data(selected_week)
    box_scores = league.box_scores(selected_week)
    home, away = [], []
    for box_score in box_scores:
        home.append(box_score.home_team)
        away.append(box_score.away_team)
    data, home_team_names, away_team_names, playoff_pct_data = [], [], [], []
    st.title(f'Family Fantasy Football Week {selected_week}, {year} Stats')
    st.markdown("""
    This web app takes data from my ESPN Fantasy Football League and provides data about it
    * Created by Joe Lieberman
    * Code Link: https://github.com/Joeliebo20/fantasyfootballwebsite
    """)
    if selected_week > 14:
        st.balloons()
        pteams = get_playoff_teams(home, away)
        st.header(f"""
        Welcome to the {year} playoffs!
        Playoff teams this year are shown below:
        """)
        df = pd.DataFrame(columns=['Team'], data=pteams)
        st.table(df)
        st.selectbox('Who do you think will win?', ['Pick a team', f'{pteams[0]}', f'{pteams[1]}', f'{pteams[2]}', f'{pteams[3]}', f'{pteams[4]}', f'{pteams[5]}'])
    col1, col2 = st.columns(2)
    col1.header('Player stats')
    merged = pd.concat([df1, df2], axis=0)
    sort = merged.sort_values(by='Points', ascending=False).reset_index(drop=True)
    max_player_pts = max(sort['Points'])
    max_player = sort['Player'][0]
    col1.dataframe(sort)
    col1.caption(f'Player with the highest score in week {selected_week} is {max_player}, with {max_player_pts} pts')

    week = 1
    max_player_pts_arr = []
    while week <= current_week:
        tmp, tmp2 = save_player_data(week)
        merge = pd.concat([tmp, tmp2], axis=0)
        s = merge.sort_values(by='Points', ascending=False).reset_index(drop=True)
        max_player_pts = s['Points'][0]
        max_player_name = s['Player'][0]
        max_player_pts_arr.append([week, max_player_name, max_player_pts])
        week += 1
    max_df = pd.DataFrame(columns=['Week', 'Player', 'Points'], data=max_player_pts_arr)
    sorted_max = max_df.sort_values(by='Points', ascending=False).reset_index(drop=True)
    max_max_player_pts = sorted_max['Points'][0]
    max_max_player = sorted_max['Player'][0]
    col2.header('Players with highest points in week')
    col2.dataframe(sorted_max)
    col2.caption(f'Highest score in the {year} season is {max_max_player}, with {max_max_player_pts} pts')
        
   
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
    choice = col2.selectbox('More league data', ['Choose an option', 'Weekly Matchups', 'League Standings', 'Team Records', 'Adds, Drops, and Trades', 'Best and Worst Week', 'Previous League Winners', 'League Scoring Rules', 'Extra League Data and Rules'])
    if choice == 'Weekly Matchups':
        matchups = league.scoreboard(selected_week)
        matchup_data = []
        for matchup in matchups:
            if matchup.home_score == 0 and matchup.away_score == 0:
                winner = 'No winner yet'
            elif matchup.home_score != 0 and (matchup.home_score == matchup.away_score):
                winner = 'Tie'
            elif matchup.home_score > matchup.away_score:
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
    elif choice == 'Previous League Winners':
        league_winner_data = list()
        for year, winner in previous_league_winners.items():
            league_winner_data.append([year, winner])
        data = pd.DataFrame(columns=['Year', 'League Winner'], data=league_winner_data)
        st.table(data)
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

    if col1.button("Other team's average pts per roster"):
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
    if col2.button('League winner predictor'):
        playoff_pct = dict()
        for team in teams:
            playoff_pct[team.owner] = float(team.playoff_pct)
        preds, pred_winner = predict_final_rankings(name_to_roster_map, playoff_pct)
        st.caption(f'Predicted league winner: {pred_winner}')
        st.table(preds)
    
    

def page2(teams):
    st.markdown("# Meet the Teams 🎉")
    col1, col2 = st.columns(2)
    for index, team in enumerate(teams):
        if index % 2 == 0:
            col1.write(team.owner)
        else:
            col2.write(team.owner)
        # put images and description of everyone here
    





def save_player_data(current_week : int): 
    '''
    This function writes data to excel and puts each team's starters into a dataframe
    '''
    home_lineups, away_lineups, home_lineup, away_lineup, home_data, away_data, x, y = [], [], [], [], [], [], [], []
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


    for fantasy_team in home_data:
        for index, player in enumerate(fantasy_team):
            x.append([player.name, player.position, player.points, player.proTeam])

    for fantasy_team in away_data:
        for index, player in enumerate(fantasy_team):
            y.append([player.name, player.position, player.points, player.proTeam])

    df1 = pd.DataFrame(columns=['Player', 'Position', 'Points', 'Team'], data=x)
    df2 = pd.DataFrame(columns=['Player', 'Position', 'Points', 'Team'], data=y)  
        
    write_to_excel(df1, df2)
    return (df1, df2)

def main():
    today = datetime.now()
    year = datetime.now().year
    league.refresh() # refresh gets newest league data, called everytime website is loaded 
    curr_week = league.current_week
    pts, pts_against, avg_pts, rosters = [], [], [], []
    name_to_roster_map = {}

    for t in teams:
        pts.append(t.points_for)
    for i in range(len(pts)):
        avg_pts.append(pts[i] / curr_week)
    for count, pts in enumerate(avg_pts, start=0):
        name_to_roster_map[owners[count]] = pts
    # to_web_app(year, curr_week, avg_pts, name_to_roster_map)

    page_names_to_funcs = {
        "Home Page": main_page,
        "Meet The Players": page2
    }
    selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
    if selected_page == "Home Page":
        page_names_to_funcs[selected_page](year, curr_week, avg_pts, name_to_roster_map)
    elif selected_page == "Meet The Players":
        page_names_to_funcs[selected_page](teams)


if __name__ == '__main__':
    main()
