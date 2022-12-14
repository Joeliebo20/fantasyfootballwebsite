import espn_api
from espn_api.football import League

LEAGUE_ID = 65345194
YEAR = 2022


league = League(LEAGUE_ID, YEAR)

league_mates = ["Joe", "Ryan", "Anthony", "Chris", "Jason", "Matt", 'Andrew', "Colin", "Paula", "Garrett", 'Michele', 'Scott']
owners = ["Joe", "Ryan", "Anthony", "Chris Irving", "Big J", "Matt", "Andrew", "colin mitchell", "paula lieberman", "Garrett Welch", "Michele Lazzara", "Scott Lazzara"]
league_ids = [1, 2, 3, 4, 5, 7, 9, 10, 11, 12]
teams = league.teams
draft = league.draft
previous_league_winners = {2019 : "Joe Lieberman", 2020 : "Joe Lieberman", 2021 : "Matt Lazz"}
