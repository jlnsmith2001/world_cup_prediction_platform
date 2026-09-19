import pandas as pd  # type: ignore[reportMissingModuleSource]
import numpy as np  # type: ignore
import json
from datafc import eloratings 


def elo_checker(team, date): #takes in a date and a team 
    elo = pd.read_csv("../data/cleaned/elo_ratings.csv") #read in the elo dataframe 
    team_history = elo[(elo["team_a"] == team) | (elo["team_b"] == team)].copy() #assigns the team history to a variable, first ensures that it has to be team_a or team_b 
    team_history["date"] = pd.to_datetime(team_history["date"]) #ensure that date is properly represented as date time 
    prev_dates = team_history[team_history["date"] < date] #assign a vairalbe to represent the entire  team history before the input (date) 
    if prev_dates.empty: #if its a empty dataframe (aka, if u are trying to access a date of a match before the first recorded date)
        return None  #then we return none 
    
    latest_date = prev_dates[prev_dates["date"] == prev_dates["date"].max()] #the very most recent date is represented using .max() 
    latest_value = latest_date.iloc[0] #get specifically the series of the latest date 
    if latest_value["team_a"] == team:   #if its team a, then 
        team_rating = latest_value["team_a_rating"] #assign its team a rating 
    else:
        team_rating = latest_value["team_b_rating"] #otherwise assign its team b rating 
    return team_rating # then return it 


#todo: refactor elo / rank to avoid duplicate logic 
def rank_checker(team, date): 
    rank = pd.read_csv("../data/cleaned/elo_ratings.csv")
    team_history = rank[(rank["team_a"] == team) | (rank["team_b"] == team)].copy()
    team_history["date"] = pd.to_datetime(team_history["date"])
    prev_dates = team_history[team_history["date"] < date]
    if prev_dates.empty:
        return None 

    latest_date = prev_dates[prev_dates["date"] == prev_dates["date"].max()]
    latest_value = latest_date.iloc[0]
    if latest_value["team_a"] == team:
        team_rank = latest_value["team_a_rank"]
    else:
        team_rank = latest_value["team_b_rank"]

    return team_rank 


def last_5_checker(team, date): 
    matches = pd.read_csv("../data/cleaned/elo_ratings.csv") #again, read in date, 
    team_history = matches[(matches["team_a"] == team) | (matches["team_b"] == team)].copy()  #ensure the team represented is either team a or b 
    team_history["date"] = pd.to_datetime(team_history["date"])  #ensure date is being converted to date time 
    prev_dates = team_history[team_history["date"] < date] #previous matches are represented by anything before the input date 
    prev_dates = prev_dates.sort_values(by = "date", ascending = False) #then sort by date, ascending = false, so all the most recent matches are at the top of the dataframe 
    if prev_dates.empty: #if empty, return none 
        return None 

    latest5_matches = prev_dates[:5] #returns a mini dataframe of the 5 most recent matches 

    num_wins = 0
    num_losses = 0
    tot_goals_scored = 0
    tot_goals_conceded = 0  #initialize everything to 0 for now 
    num_matches = latest5_matches.shape[0]

    for _, match in latest5_matches.iterrows() : #_ would be replaced by index but we dont need index so just _, match 
        if match["team_a"] == team:  #if itsteam a, 
            tot_goals_scored += match["team_a_score"] #reflect goals scored and conceded 
            tot_goals_conceded += match["team_b_score"]
            if match["team_a_score"] > match["team_b_score"]: #and do the same for w/l 
                num_wins += 1 
            elif match["team_a_score"] < match["team_b_score"]:
                num_losses += 1
        else: #otherwise that indicates its team b, so update accordingly
            tot_goals_scored += match["team_b_score"]
            tot_goals_conceded += match["team_a_score"]
            if match["team_b_score"] > match["team_a_score"]:
                num_wins += 1 
            elif match["team_b_score"] < match["team_a_score"]:
                num_losses += 1

    win_rate = num_wins / num_matches  
    loss_rate = num_losses / num_matches
    scoring_rate = tot_goals_scored / num_matches
    conceding_rate = tot_goals_conceded / num_matches #then 

    return win_rate, loss_rate, scoring_rate, conceding_rate 



def tournament_checker(tournament):
    with open("../src/models/X_column_names.json", "r", encoding="utf-8") as file:
        column_names = json.load(file)

    tournament_names = {} 
    for column in column_names: 
        if column.startswith("tournament_"):
            tournament_names[column] = 0

    tourney = "tournament_" + tournament
    if tourney not in tournament_names:
        return None 
    else: 
        tournament_names[tourney] = 1

    return tournament_names 


def neutral_venue(team_a, team_b, location):
    codes = eloratings.country_codes_data() 
    team_a_check = codes[codes["country_code"] == team_a]
    if team_a_check.empty:
        return None

    teamA_row = team_a_check.iloc[0]
    teamA_country = teamA_row["country_name"]

    team_b_check = codes[codes["country_code"] == team_b]
    if team_b_check.empty: 
        return None 

    teamB_row = team_b_check.iloc[0]
    teamB_country = teamB_row["country_name"]

    if teamA_country == location or teamB_country == location:
        return 0 
    else:
        return 1

def gather_match_features(home_team, away_team, date, tourney, location):
   home_elo = elo_checker(home_team , date)
   away_elo = elo_checker(away_team, date)

   home_rank = rank_checker(home_team, date)
   away_rank = rank_checker(away_team, date) 

   elo_diff = home_elo - away_elo
   rank_diff = away_rank - home_rank

   home_win_r, home_loss_r, home_score_r, home_concede_r = last_5_checker(home_team, date)
   away_win_r, away_loss_r, away_score_r, away_concede_r = last_5_checker(away_team, date)

   tournament_bracket = tournament_checker(tourney)

   is_match_neutral = neutral_venue(home_team, away_team, location)

   with open("../src/models/x_column_names.json", "r", encoding = "utf-8") as file:
    x_cols = json.load(file)
   
   match_features = {}
   
   match_features["home_elo"] = home_elo
   match_features["away_elo"] = away_elo
   match_features["home_ranking"] = home_rank
   match_features["away_ranking"] = away_rank
   match_features["elo_difference"] = elo_diff
   match_features["rank_difference"] = rank_diff
   match_features["home_last5_W"] = home_win_r 
   match_features["home_last5_L"] = home_loss_r
   match_features["home_last5_scoring"] = home_score_r
   match_features["home_last5_conceding"] = home_concede_r
   match_features["away_last5_W"] = away_win_r
   match_features["away_last5_L"] = away_loss_r 
   match_features["away_last5_scoring"] = away_score_r 
   match_features["away_last5_conceding"] = away_concede_r
   match_features["neutral"] = is_match_neutral 
   match_features |= tournament_bracket

   match_df = pd.DataFrame([match_features], columns = x_cols)
   print(match_df.isna().sum().sum())
   return match_df


print(gather_match_features("ES", "AR", "2026-07-19", "FIFA World Cup", "United States").T)