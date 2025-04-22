from nba_api import *
from nba_api.stats.endpoints import PlayByPlayV2
from nba_api.stats.endpoints import leaguedashplayerstats
import streamlit as st


def open_window(total):
     
    st.title("Game Recommendation")

    st.info("Start your day with last night's best NBA match spoilers-free.")

    st.write(total[0])

    with st.expander("Global Marks"):
        st.write(total[2])

    with st.expander("Ratings Info"):
        st.write(total[1])
     

def create_message(games, final_rates, break_downs, last_night):
    message_1 = f'Here the ranking of {last_night} NBA games:\n\n'
    message_2 = f'Here {last_night} NBA games with their global evaluation:\n\n'
    rates_2 = sorted(final_rates, reverse=True)
    break_down_1 = ''
    break_down_2 = ''
    n = 1
    for rate in rates_2:
        i = final_rates.index(rate)
        game = games[i]
        message_1 += f'{n}. {game[0]} - {game[1]}\n\n'
        message_2 += f'{n}. {game[0]} - {game[1]}:\t\t {rate}\n\n'
        break_down_2 += f'{game[0]} - {game[1]}\t{str(break_downs[i])}\n\n'
        n += 1

    break_down_1 += f'\n\n\n More detail in case you want it:\n\n'
    break_down_1 += '[[shooting_1, playing_1, defense_1], team1_rate, [shooting_2, playing_2, defense_2], team2_rate'
    break_down_1 += '[players, performace_mult, players_rate]'
    break_down_1 += '[difference, total_p, chance_lead, p_mult, ot_mult, general_rate], mark, team_mult, final_rate]\n\n'

    break_down_1 += break_down_2
    total = [message_1, break_down_1, message_2]

    return total
   
def get_games_IDs(data):
    for key, value in data.items():
        if key == 'resultSets':
            games = value[0]

    for key_1, value_1 in games.items():
        if key_1 == 'rowSet':
            games_1 = value_1

    game_IDs = []
    for game in games_1:
        game_IDs.append(game[2])

    return game_IDs

def calc_ot(team1, team2):
    if team1[12] != 0 or team2[12] and not(team1[13] != 0 or team2[13] != 0) != 0:
        overtime = 1

    elif team1[13] != 0 or team2[13] != 0 and not(team1[14] != 0 or team2[14] != 0):
        overtime = 2

    elif team1[14] != 0 or team2[14] != 0:
        overtime = 3

    else:
        overtime = 0

    return overtime

def get_game_stats(summary, boxscore):

        #print(summary)

        for key, value in summary.items():
            if key == 'resultSets':
                basics = value[1]
                points = value[5]


        for key, value in basics.items():
            if key == 'rowSet':
                data1 = value[0]
                data2 = value[1]

        games = [data1[2], data2[2]] #column 1 f'{data1[2]} - {data2[2]}'

        for key, value in points.items():
            if key == 'rowSet':
                data3 = value[0]
                data4 = value[1]

                if data4[4] == games[0]:
                      data3 = value[1]
                      data4 = value[0]




        difference = abs(data3[22] - data4[22])
        total_points = data3[22] + data4[22]
        overtime = calc_ot(data3, data4)
        times_tied = data1[9]
        largest_lead = max([data1[7], data2[7]])
        to_lead = data1[8]

        char_tot = [difference, overtime, total_points, times_tied, to_lead, largest_lead]

        for key, value in boxscore.items():
           if key == 'resultSets':
                team_stats = value [1]

        for key, value in team_stats.items():
            if key == 'rowSet':
                data5 = value[0]
                data6 = value[1]
                if data6[3] == games[0] :
                    data5 = value[1]
                    data6 = value[0]


        if (data3[22] - data4[22]) > 0:
            W_L_1 = 'W'
            W_L_2 = 'L'
        else:
            W_L_1 = 'L'
            W_L_2 = 'W'

        #examp = [W/L    FG%         FG3%       FG3M       AST         TO       OR        ST          BLK  ]
        char_1 = [W_L_1, data5[8], data5[11], data5[9], data5[18], data5[21], data5[15], data5[19], data5[20]]
        char_2 = [W_L_2, data6[8], data6[11], data6[9], data6[18], data6[21], data6[15], data6[19], data6[20]]


        #print(games)
        #print(team_stats)
        #print(basics)
        #print(points)
        #print(data3)
        t_ID_1 = data3[3]
        t_ID_2 = data4[3]

        team_data = [games, t_ID_1, t_ID_2, char_tot, char_1, char_2]

        return team_data

def get_players_stats(boxscore):
    for key, value in boxscore.items():
            if key == 'resultSets':
                bscore = value[0]

    for key, value in bscore.items():
        if key == 'rowSet':
            players = value


    stats = []
    for player in players:
        if player[8] == '':
            stats.append([player[5], player[27], player[22], player[21], player[23], player[24]])
            #21 reb, 22 ast, 23 stl, 24 blk, 27 pts, name [5]

    return stats

def get_rates(stats,pbp,prop,players):
    general = stats[3] #[difference, overtime, total_points, times_tied, to_lead, largest_lead]

    team_1 = stats[4] # [W/L    FG%         FG3%       FG3M       AST         TO       OR        ST          BLK  ]
    team_2 = stats [5]


    #individual [shoting, playability, intensity]
    rate_1 = get_individual_rate(team_1)
    rate_2 = get_individual_rate(team_2)

    rate_3 = get_players_rate(players)
    #print(rate_3)

    rate_4 = get_general_rate(general,pbp)#store

    t_1_rate = sum(rate_1)/3
    t_2_rate = sum(rate_2)/3

    teams_rate = [rate_1, t_1_rate, rate_2, t_2_rate]#store



    final_rate = prop[0]*t_1_rate + prop[1]*t_2_rate + prop[2]*rate_3[2] + prop[3]*rate_4[5]

    rates = [teams_rate, rate_3, rate_4, final_rate]

    return rates

def get_players_rate(players):

    top_players = get_top100_players()

    tier_1 = top_players[0:5]
    t_1 = 0; tier1_w = 25

    tier_2 = top_players[5:15]
    t_2 = 0; tier2_w = 20

    tier_3 = top_players[15:30]
    t_3 = 0; tier3_w = 10

    tier_4 = top_players[30:50]
    t_4 = 0; tier4_w = 5

    tier_5 = top_players[50:75]
    t_5 = 0; tier5_w = 2.5

    tier_6 = top_players[75:99]
    t_6 = 0; tier6_w = 1.25


    stats_mult = 1

    for player in players:
        name = player.pop(0)

        if name in tier_1:
            t_1 += 1

        elif name in tier_2:
            t_2 += 1

        elif name in tier_3:
            t_3 += 1

        elif name in tier_4:
            t_4 += 1

        elif name in tier_5:
            t_5 += 1

        elif name in tier_6:
            t_6 += 1

        #print(player)
        total = sum(player)
        pts = player[0]; ast = player[1]; reb = player[2]
        stl = player[3]; blk = player[4]

        if (total >= 80 and stats_mult < 1.5) or ast >= 17 or pts >= 55 or reb >= 22 or blk >= 8 or stl >= 7:
              stats_mult = 1.5

        elif total < 80 and total >= 60 and stats_mult < 1.25:
              stats_mult = 1.25

        elif total < 60 and total >= 45 and stats_mult < 1.25:
              stats_mult = 1.12

    ratio = t_1*tier1_w + t_2*tier2_w + t_3*tier3_w + t_4*tier4_w + t_5*tier5_w + t_6*tier6_w

    grade = ratio * stats_mult

    rate = [ratio, stats_mult, grade]
    #print(rate)

    return rate


def get_top100_players():
    # Fetch current season player stats
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats()
    stats_df = player_stats.get_data_frames()[0]

    # Calculate per-game stats
    stats_df['PTS/G'] = stats_df['PTS'] / stats_df['GP']
    stats_df['AST/G'] = stats_df['AST'] / stats_df['GP']
    stats_df['REB/G'] = stats_df['REB'] / stats_df['GP']

    # Create a ranking score
    stats_df['TOTAL/G'] = stats_df['PTS/G'] + stats_df['AST/G'] + stats_df['REB/G']

    # Get top 50 players' names in order
    top_players_list = stats_df.sort_values(by='TOTAL/G', ascending=False)['PLAYER_NAME'].head(100).tolist()

    # Display list
    #print(top_players_list)
    return(top_players_list)

def get_general_rate(stats,pbp):

    points = last_points(pbp)
    dif = stats[0]; ot = stats[1]; tot_p = stats[2]
    ties = stats[3]; c_lead = stats[4]; l_lead = stats[5]
    mark = create_range_list([100, 0])
    ratio = [0.5, 0.25, 0.25]

    #OT
    if ot == 0:
         ot_mult = 1

    elif ot == 1:
         ot_mult = 1.2

    elif ot == 2:
         ot_mult = 1.35

    elif ot >= 3:
         ot_mult = 1.5


    #last 10s [1] and 30s [0] points
    p_mult = 1

    # Result difference

    if dif <= 3:
        difference = mark[6]
        if points[1] == True and points[0] == True:
            p_mult = 1.25

        elif points[1] == True and points[0] == False:
            p_mult = 1.2


    elif dif == 4:
        difference = mark[5]
        if points[1] == True and points[0] == True:
            p_mult = 1.15

        elif points[1] == True and points[0] == False:
            p_mult = 1.1


    elif dif == 5 or dif == 6:
        difference = mark[4]

    elif dif >= 7 and dif <= 12:
        difference = mark[3]

    elif dif >= 13 and dif <= 20:
        difference = mark[2]

    elif dif > 20 and dif <= 30:
        difference = mark[1]
    
    elif dif > 30:
        difference = 0



    #Total points

    if tot_p <= 180:
         score = mark[0]

    elif tot_p > 180 and tot_p <= 200:
         score = mark[1]

    elif tot_p > 200 and tot_p <= 220:
         score = mark[2]

    elif tot_p > 220 and tot_p <= 240:
         score = mark[3]

    elif tot_p > 240 and tot_p <= 260:
         score = mark[4]

    elif tot_p > 260 and tot_p < 280:
         score = mark[5]

    elif tot_p >= 280:
         score = mark[6]


    #Chance to lead (include ties)

    if c_lead <= 4:
         leads = mark[1]

    elif c_lead > 4 and c_lead <= 8:
         leads = mark[2]

    elif c_lead > 8 and c_lead <= 14:
         leads = mark[3]

    elif c_lead > 14 and c_lead <= 20:
         leads = mark[4]

    elif c_lead > 20 and c_lead <= 25:
         leads = mark[5]

    elif c_lead > 25:
         leads = mark[6]


    grade = ot_mult*(difference*p_mult*ratio[0] + score*ratio[1] + leads*ratio[2])

    rates = [difference, score, leads, p_mult, ot_mult, grade]

    return rates

def last_points(pbp):
    for key, value in pbp.items():
           if key == 'resultSets':
                data = value[0]

    for key, value in data.items():
            if key == 'rowSet':
                    plays = value

    min = []
    result = []

    for play in plays:
            min.append(play[6])
            result.append(play[10])


    final_mins = min[-50:]


    position1 = []
    position2 = []
    for final_min in final_mins:
            if final_min.startswith('0:3') or final_min.startswith('0:2'):
                    pos1 = final_mins.index(final_min)
                    position1.append(pos1)
            elif final_min.startswith('0:1') or final_min.startswith('0:0'):
                    pos2 = final_mins.index(final_min)
                    position2.append(pos2)

    final_plays = result[-50:]


    if position1 != []:

        last_plays_3 = final_plays[position1[0]:]

        for last_play in last_plays_3:
            if last_play is not None:
                    points_3 = True
            else:
                    points_3 = False

    else:
        points_3 = False



    if position2 != []:
        last_plays_1 = final_plays[position2[0]:]

        for last_play in last_plays_1:
            if last_play is not None:
                    points_1 = True
            else:
                    points_1 = False

    else:
        points_1 = False

    points = [points_3, points_1]

    return points

def create_range_list(values):#FOR TEAMS AND PLAYERS
    min_val = min(values)
    max_val = max(values)
    mid1 = min_val + (max_val - min_val)/6
    mid2 = min_val + 2*(max_val - min_val)/6
    mid3 = min_val + 3*(max_val - min_val)/6
    mid4 = min_val + 4*(max_val - min_val)/6
    mid5 = min_val + 5*(max_val - min_val)/6

    return [min_val, mid1, mid2, mid3, mid4, mid5, max_val]

def get_individual_reference(): #REFERENCE VALUES FOR TEAM PERFORMANCES

    #CHANGE LIMITS HERE
    FGP_lim = [60, 35]
    F3P_lim = [50, 30]
    F3M_lim = [22, 10]
    AST_lim = [35, 18]
    TO_lim = [8, 20]
    OR_lim = [22, 6]
    STL_lim = [13, 4]
    BLK_lim = [8, 2]


    FGP = create_range_list(FGP_lim)
    F3P = create_range_list(F3P_lim)
    F3M = create_range_list(F3M_lim)
    AST = create_range_list(AST_lim)
    TO = sorted(create_range_list(TO_lim), reverse=True)
    OR = create_range_list(OR_lim)
    STL = create_range_list(STL_lim)
    BLK = create_range_list(BLK_lim)

    reference = [FGP, F3P, F3M, AST, TO, OR, STL, BLK]

    return reference

def get_individual_rate(team):

    #REFERENCE VALUES
    reference = get_individual_reference()

    FGP_ref = reference[0]; F3P_ref = reference[1]; F3M_ref = reference[2]
    AST_ref = reference[3]; TO_ref = reference[4]; OR_ref = reference[5]
    STL_ref = reference[6]; BLK_ref = reference[7]; MRK_ref = [100, 85.71, 71.42, 57.13, 42.89, 28.55, 14.29, 0]
    h_rate = 1 #apply to all deffense stats added
    h_rate_2 = 0.5 #apply OR
    m3_rel = 1.5 #3 point relevance over fg

    #REAL VALUES

    if team[1] is None:
        FGP = 0

    else:
        FGP = team[1]*100

    if team[2] is None:
        F3P = 0

    else:
        F3P = team[2]*100

    F3M = team[3]
    AST = team[4]; TO = team[5]; OR = team[6]*h_rate_2
    STL = team[7]; BLK = team[8]

    #SHOTING
    if (FGP+F3P*m3_rel)*F3M >= (FGP_ref[6]+F3P_ref[6]*m3_rel)*F3M_ref[6]:
        shoting = MRK_ref[0]

    elif ((FGP+F3P*m3_rel)*F3M < (FGP_ref[6]+F3P_ref[6]*m3_rel)*F3M_ref[6]) and ((FGP+F3P*m3_rel)*F3M >= (FGP_ref[5]+F3P_ref[5]*m3_rel)*F3M_ref[5]):
        shoting = MRK_ref[1]

    elif ((FGP+F3P*m3_rel)*F3M < (FGP_ref[5]+F3P_ref[5]*m3_rel)*F3M_ref[5]) and ((FGP+F3P*m3_rel)*F3M >= (FGP_ref[4]+F3P_ref[4]*m3_rel)*F3M_ref[4]):
        shoting = MRK_ref[2]

    elif ((FGP+F3P*m3_rel)*F3M < (FGP_ref[4]+F3P_ref[4]*m3_rel)*F3M_ref[4]) and ((FGP+F3P*m3_rel)*F3M >= (FGP_ref[3]+F3P_ref[3]*m3_rel)*F3M_ref[3]):
        shoting = MRK_ref[3]

    elif ((FGP+F3P*m3_rel)*F3M < (FGP_ref[3]+F3P_ref[3]*m3_rel)*F3M_ref[3]) and ((FGP+F3P*m3_rel)*F3M >= (FGP_ref[2]+F3P_ref[2]*m3_rel)*F3M_ref[2]):
        shoting = MRK_ref[4]

    elif ((FGP+F3P*m3_rel)*F3M < (FGP_ref[2]+F3P_ref[2]*m3_rel)*F3M_ref[2]) and ((FGP+F3P*m3_rel)*F3M >= (FGP_ref[1]+F3P_ref[1]*m3_rel)*F3M_ref[1]):
        shoting = MRK_ref[5]

    elif ((FGP+F3P*m3_rel)*F3M < (FGP_ref[1]+F3P_ref[1]*m3_rel)*F3M_ref[1]) and ((FGP+F3P*m3_rel)*F3M >= (FGP_ref[0]+F3P_ref[0]*m3_rel)*F3M_ref[0]):
        shoting = MRK_ref[6]

    else:
        shoting = MRK_ref[7]


    #PLAYING
    if AST/TO >= AST_ref[6]/TO_ref[6]:
        playing = MRK_ref[0]

    elif (AST/TO < AST_ref[6]/TO_ref[6]) and (AST/TO >= AST_ref[5]/TO_ref[5]):
        playing = MRK_ref[1]

    elif (AST/TO < AST_ref[5]/TO_ref[5]) and (AST/TO >= AST_ref[4]/TO_ref[4]):
        playing = MRK_ref[2]

    elif (AST/TO < AST_ref[4]/TO_ref[4]) and (AST/TO >= AST_ref[3]/TO_ref[3]):
        playing = MRK_ref[3]

    elif (AST/TO < AST_ref[3]/TO_ref[3]) and (AST/TO >= AST_ref[2]/TO_ref[2]):
        playing = MRK_ref[4]

    elif (AST/TO < AST_ref[2]/TO_ref[2]) and (AST/TO >= AST_ref[1]/TO_ref[1]):
        playing = MRK_ref[5]

    elif (AST/TO < AST_ref[1]/TO_ref[1]) and (AST/TO >= AST_ref[0]/TO_ref[0]):
        playing = MRK_ref[6]

    else:
        playing = MRK_ref[7]


    #HUSTLE
    if (OR + STL + BLK) >= (OR_ref[6]*h_rate_2 + STL_ref[6] + BLK_ref[6])*h_rate:
        hustle = MRK_ref[0]

    elif ((OR + STL + BLK) < (OR_ref[6]*h_rate_2 + STL_ref[6] + BLK_ref[6])*h_rate) and ((OR + STL + BLK) >= (OR_ref[5]*h_rate_2 + STL_ref[5] + BLK_ref[5])*h_rate):
        hustle = MRK_ref[1]

    elif ((OR + STL + BLK) < (OR_ref[5]*h_rate_2 + STL_ref[5] + BLK_ref[5])*h_rate) and ((OR + STL + BLK) >= (OR_ref[4]*h_rate_2 + STL_ref[4] + BLK_ref[4])*h_rate):
        hustle = MRK_ref[2]

    elif ((OR + STL + BLK) < (OR_ref[4]*h_rate_2 + STL_ref[4] + BLK_ref[4])*h_rate) and ((OR + STL + BLK) >= (OR_ref[3]*h_rate_2 + STL_ref[3] + BLK_ref[3])*h_rate):
        hustle = MRK_ref[3]

    elif ((OR + STL + BLK) < (OR_ref[3]*h_rate_2 + STL_ref[3] + BLK_ref[3])*h_rate) and ((OR + STL + BLK) >= (OR_ref[2]*h_rate_2 + STL_ref[2] + BLK_ref[2])*h_rate):
        hustle = MRK_ref[4]

    elif ((OR + STL + BLK) < (OR_ref[2]*h_rate_2 + STL_ref[2] + BLK_ref[2])*h_rate) and ((OR + STL + BLK) >= (OR_ref[1]*h_rate_2 + STL_ref[1] + BLK_ref[1])*h_rate):
        hustle = MRK_ref[5]

    elif ((OR + STL + BLK) < (OR_ref[1]*h_rate_2 + STL_ref[1] + BLK_ref[1])*h_rate) and ((OR + STL + BLK) >= (OR_ref[0]*h_rate_2 + STL_ref[0] + BLK_ref[0])*h_rate):
        hustle = MRK_ref[6]

    else:
        hustle = MRK_ref[7]


    return shoting, playing, hustle

def get_teams_mult(matchup, standings):

    rivalries_1 = [
        ['LAL', 'BOS'], ['BOS', 'LAL'],
        ['LAL', 'LAC'], ['LAC', 'LAL'],
        ['GSW', 'LAL'], ['LAL', 'GSW'],
        ['DEN', 'LAL'], ['LAL', 'DEN'],
        ['MIA', 'BOS'], ['BOS', 'MIA']
    ]

    rivalries_2 = [
        ['CHI', 'DET'], ['DET', 'CHI'],
        ['SAS', 'DAL'], ['DAL', 'SAS'],
        ['CHI', 'NYK'], ['NYK', 'CHI'],
        ['GSW', 'CLE'], ['CLE', 'GSW'],
        ['PHI', 'BOS'], ['BOS', 'PHI']
    ]

    rivalries_3 = [
        ['PHX', 'DAL'], ['DAL', 'PHX'],
        ['MEM', 'GSW'], ['GSW', 'MEM'],
        ['SAC', 'GSW'], ['GSW', 'SAC'],
        ['MIN', 'DEN'], ['DEN', 'MIN'],
        ['NYK', 'CLE'], ['CLE', 'NYK']
    ]

    if matchup[0] in rivalries_1:
        t_mult_1 = 1.15

    elif matchup[0] in rivalries_2:
        t_mult_1 = 1.1

    elif matchup[0] in rivalries_3:
        t_mult_1 = 1.05

    else:
        t_mult_1 = 1


    if matchup[1] in standings[0] and matchup[2] in standings[0]:
        t_mult_2 = 1.15

    elif matchup[1] in standings[0] and matchup[2] in standings[1]:
        t_mult_2 = 1.1

    elif matchup[1] in standings[1] and matchup[2] in standings[0]:
        t_mult_2 = 1.1

    elif not(matchup[1] in standings[1]) and not(matchup[1] in standings[0]) and not(matchup[2] in standings[1]) and not(matchup[2] in standings[0]):
        t_mult_2 = 1

    else:
        t_mult_2 = 1.05

    #print(t_mult_1)
    #print(t_mult_2)

    t_mult = t_mult_1*t_mult_2

    #print(t_mult)

    return t_mult

def get_standings(stands):

    east = []
    west = []

    for key, value in stands.items():
        if key == 'resultSets':
            orders_East = value[2]
            orders_West = value[3]

    for key, value in orders_East.items():
                if key == 'rowSet':
                    data1 = value
                    for data in data1:
                        east.append(data[4])

    for key, value in orders_West.items():
                if key == 'rowSet':
                    data1 = value
                    for data in data1:
                        west.append(data[4])

    top_5 = east[:5] + west[:5]
    bottom_5 = east[5:10] + west[5:10]

    return top_5, bottom_5
