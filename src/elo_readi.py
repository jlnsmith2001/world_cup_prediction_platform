import pandas as pd  # type: ignore[reportMissingModuleSource]
import numpy as np  # type: ignore


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
    matches = pd.read_csv("../data/cleaned/elo_ratings.csv")
    team_history = matches[(matches["team_a"] == team) | (matches["team_b"] == team)].copy() 
    team_history["date"] = pd.to_datetime(team_history["date"])
    prev_dates = team_history[team_history["date"] < date]
    prev_dates = prev_dates.sort_values(by = "date", ascending = False)
    if prev_dates.empty:
        return None 

    latest5_matches = prev_dates[:5]

    num_wins = 0
    num_losses = 0
    tot_goals_scored = 0
    tot_goals_conceded = 0 
    num_matches = latest5_matches.shape[0]

    for _, match in latest5_matches.iterrows() :
        if match["team_a"] == team: 
            tot_goals_scored += match["team_a_score"]
            tot_goals_conceded += match["team_b_score"]
            if match["team_a_score"] > match["team_b_score"]:
                num_wins += 1 
            elif match["team_a_score"] < match["team_b_score"]:
                num_losses += 1
        else:
            tot_goals_scored += match["team_b_score"]
            tot_goals_conceded += match["team_a_score"]
            if match["team_b_score"] > match["team_a_score"]:
                num_wins += 1 
            elif match["team_b_score"] < match["team_a_score"]:
                num_losses += 1

    win_rate = num_wins / num_matches 
    loss_rate = num_losses / num_matches
    scoring_rate = tot_goals_scored / num_matches
    conceding_rate = tot_goals_conceded / num_matches

    return win_rate, loss_rate, scoring_rate, conceding_rate 



print(last_5_checker("US", "2026-07-06"))










