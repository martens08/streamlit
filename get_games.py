#NBA API
from nba_api import *
from nba_api.stats.endpoints import scoreboardv2
from nba_api.stats.endpoints import boxscoretraditionalv2
from nba_api.stats.endpoints import boxscoresummaryv2
from nba_api.stats.endpoints import playoffpicture
from nba_api.stats.endpoints import PlayByPlayV2

#DATE
from datetime import datetime, timedelta
import time #add delay

from nba_functions import *

last_night = datetime.now().date()- timedelta(days=1)
three_days = datetime.now().date()- timedelta(days=3)

with st.expander('Remember last three game days'):
        selected_date = st.date_input(
        "📅 Select a date:",
        last_night,
        min_value=three_days,
        max_value=last_night
        )# - timedelta(days=1)

day_ofset = '0'
date = selected_date 
league_ID = '00'

try:
    scoreboard = scoreboardv2.ScoreboardV2(day_ofset, date, league_ID).get_dict()
    go_on = True

except KeyError as e:
    st.error(f"⚠️ Data for this date is incomplete: {e}")
    go_on = False

if go_on == True:
    IDs = get_games_IDs(scoreboard)

    stands = playoffpicture.PlayoffPicture().get_dict()
    standings = get_standings(stands)
            
    games = []
    final_rates = []
    break_downs = []

    prop = [0.1, 0.1, 0.2, 0.6]

    for ID in IDs:
        boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=ID).get_dict()
        summary = boxscoresummaryv2.BoxScoreSummaryV2(game_id=ID).get_dict()
        pbp = PlayByPlayV2(game_id=ID,end_period='4',start_period='4').get_dict()
        
        teams = get_game_stats(summary, boxscore)
        players = get_players_stats(boxscore)
        
        t_rate = get_rates(teams,pbp,prop,players)
        t_mult = get_teams_mult(teams,standings)#ok!
        
        game = teams[0]
        games.append(game)
        final_rate = round(t_rate[3]*t_mult,2)

        if final_rate > 100:
            final_rate = 100

        final_rates.append(final_rate)

        t_rate.append(t_mult)
        t_rate.append(final_rate)
        break_downs.append(t_rate)

        #print(game)
        #print(t_rate)
        #print(final_rate)
        

        time.sleep(3)  # Delay of 3 seconds between each request

    message = create_message(games, final_rates, break_downs, last_night)

    #send_mail(message, last_night) 

    open_window(message)

    

   

    

    


   

    
