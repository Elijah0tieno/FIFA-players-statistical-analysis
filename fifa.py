import re

import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot

players = pd.read_csv("fifa_data.csv", low_memory=False)
print(players.columns)
print(players.shape)
print(players.info())

#Check if any values are missing
print(players.isna().sum())

print(players[players['Weight'].isna()].head())

#Discard missing attributes
players.dropna(subset= ['Weight','Height'],inplace=True)
print(players.isna().sum())

#Convert Value and Wages in numerical data format
"""Convert player market value to millions"""
players['Value'] = players['Value'].fillna('NaN')
players['Value'] = players['Value'].apply(lambda x:
                                    float(re.findall('€(.*)M',x)[0]) if 'M' in x
                                    else (float(re.findall('€(.*)K',x)[0])/1000 if 'K' in x  else 0))

"""Convert player wages into value in Thousands(K)"""
players['Wage'] = players['Wage'].fillna('NaN')
players['Wage'] = players['Wage'].apply(lambda x:float(re.findall('€(.*)K',x)[0]) if 'K' in x
                                  else float(re.findall('€(.*)',x)[0])/1000)


"""Convert Players release clause in millions"""
players['Release Clause'] = players['Release Clause'].fillna('NaN')
players['Release Clause'] = players['Release Clause'].apply(lambda x:
                                    float(re.findall('€(.*)M',x)[0]) if 'M' in x
                                    else (float(re.findall('€(.*)K',x)[0])/1000 if 'K' in x  else 0))

#Find number of players
print("Total players in fifa 20 -",players.shape[0])

forwards = ['ST','LF','RF','CF','LW','RW']
midfielders = ['CM','LCM','RCM','RM','LM','CDM','LDM','RDM','CAM','LAM','RAM','LCM','RCM']
defenders = ['CB','RB','LB','RCB','LCB','RWB','LWB']
goalkeepers = ['GK']
players['Overall_position'] = None
forward_players = players[players['Position'].isin(forwards)]
midfielder_players = players[players['Position'].isin(midfielders)]
defender_players = players[players['Position'].isin(defenders)]
goalkeeper_players = players[players['Position'].isin(goalkeepers)]
players.loc[forward_players.index,'Overall_position'] = 'forward'
players.loc[defender_players.index,'Overall_position'] = 'defender'
players.loc[midfielder_players.index,'Overall_position'] = 'midfielder'
players.loc[goalkeeper_players.index,'Overall_position'] = 'goalkeeper'

tm = players['Overall_position'].value_counts()
plt_data = [go.Bar(
    x = tm.index,
    y = tm
    )]

layout = go.Layout(
    autosize=False,
    width=500,
    height=500,
    title="Total Players in the overall positions"
)
fig = go.Figure(data=plt_data, layout=layout)
plot(fig)
fig.show()


#Find the top 5 best players in these three overall positions
print("TOP 5 FORWARDS")
print(players[players['Overall_position'] == 'forward'].sort_values
      (by='Overall',ascending=False)[['Name','Age','Overall','Position']].head())

#Find the top 5 midfielders
print("TOP 5 MIDFIELDERS")
print(players[players['Overall_position'] == 'midfielder'].sort_values(
    by='Overall',ascending=False)[['Name','Age','Overall','Position']].head())

#Find Top Five Defenders
print("TOP 5 DEFENDERS")
print(players[players['Overall_position'] == 'defender'].sort_values(
    by='Overall',ascending=False)[['Name','Age','Overall','Position']].head())


#Find Top Five Golkeepers
print("TOP 5 GOLKEEPERS")
print(players[players['Overall_position'] == 'goalkeeper'].sort_values(
    by='Overall',ascending=False)[['Name','Age','Overall','Position']].head())

#Players with highest valuation
print("--------------Top 10 Highest Market Value in Millions € -------------- ")
print(players.sort_values(by = 'Value',ascending = False)
[['Name','Age','Value','Overall','Potential','Position']].head(10))

#Total players from a nation
tm = players.groupby('Nationality').count()['ID'].sort_values(ascending=False)
plt_data = [go.Bar(
    x = tm.index,
    y = tm
)]
layout = go.Layout(
    autosize=False,
    width=500,
    height=600,
    title='Total Players from a Nation in the whole game'
)
fig = go.Figure(data=plt_data,layout=layout)
plot(fig)

#Average rating of a player from a nationality
national_team_data = players.groupby(['Nationality'],as_index=False).agg(['mean','count','sum'])

print(national_team_data.head())

#Find avg overall for national_teams with at least 200 players
tm = national_team_data[national_team_data['ID']['count']>200]['Overall']['mean'].sort_values(
    ascending=False)
plt_data = [go.Bar(
    x = tm.index,
    y = tm
)]
layout = go.Layout(
    autosize=False,
    width=1000,
    height=500,
    title="Average Overall Rating of a player from a nation have at least 200 players"
)
fig = go.Figure(data=plt_data,layout=layout)
plot(fig)

"""CLUB ANALYSIS"""
#We will only use the top 50 clubs considering there are numerous clubs
top_50_clubs = players[players['Age']>18].groupby('Club').mean()['Overall'].sort_values(
    ascending=False).head(50)

top_50_clubs = top_50_clubs.index.tolist()
top_50_clubs = players[players['Club'].isin(top_50_clubs)]

print(top_50_clubs.head())

"""RADAR PLOT OF TOP TEN FORWARDS"""

top_fwds = players[players['Overall_position'] == 'forward'].sort_values(by='Overall', ascending=False).head(2)
plt_cols = ['Crossing', 'Finishing', 'HeadingAccuracy', 'ShortPassing', 'Volleys', 'Dribbling',
            'Curve', 'FKAccuracy', 'LongPassing', 'BallControl', 'Acceleration',
            'SprintSpeed', 'Agility', 'Reactions', 'Balance', 'ShotPower',
            'Jumping', 'Stamina', 'Strength', 'LongShots', 'Aggression',
            'Interceptions', 'Positioning', 'Vision', 'Penalties', 'Composure',
            'Marking', 'StandingTackle', 'SlidingTackle']
top_fwds.reset_index(inplace=True)
plt_data = []
for i in range(top_fwds.shape[0]):
    trace = go.Scatterpolar(
        r=top_fwds.loc[i, plt_cols],
        theta=plt_cols,
        # mode = 'lines',
        name=top_fwds.loc[i, 'Name'],
    )
    plt_data.append(trace)

layout = go.Layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[15, 100],
        )
    ),
    height=900,
    width=900,
    title="Top 2 forwards",
    showlegend=True
)

fig = go.Figure(data=plt_data, layout=layout)
plot(fig)

"""RADAR PLOT FOR TOP 10 MIDFILDERS"""
top_fwds = players[players['Overall_position'] == 'midfielder'].sort_values(by='Overall', ascending=False).head(3)
top_fwds.reset_index(inplace=True)
plt_data = []
for i in range(top_fwds.shape[0]):
    trace = go.Scatterpolar(
        r=top_fwds.loc[i, plt_cols],
        theta=plt_cols,
        # mode = 'lines',
        name=top_fwds.loc[i, 'Name'],
    )
    plt_data.append(trace)

layout = go.Layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[10, 100],
        )
    ),
    height=900,
    width=900,
    title="Top 3 midfielders",
    showlegend=True
)

fig = go.Figure(data=plt_data, layout=layout)
plot(fig)

"""RADAR PLOT FOR TOP 10 DEFENDERS"""
# top_fwds = players[players['Overall_position'] == 'defender'].sort_values(by='Overall', ascending=False).head(10)
# top_fwds.reset_index(inplace=True)
# plt_data = []
# for i in range(top_fwds.shape[0]):
#     trace = go.Scatterpolar(
#         r=top_fwds.loc[i, plt_cols],
#         theta=plt_cols,
#         # mode = 'lines',
#         name=top_fwds.loc[i, 'Name'],
#     )
#     plt_data.append(trace)
#
# layout = go.Layout(
#     polar=dict(
#         radialaxis=dict(
#             visible=True,
#             range=[10, 100],
#         )
#     ),
#     height=900,
#     width=900,
#     title="Top 10 defenders",
#     showlegend=True
# )
#
# fig = go.Figure(data=plt_data, layout=layout)
# plot(fig)

"""RADAR PLOT FOR TOP 10 GOALKEEPERS"""
# top_fwds = players[players['Overall_position'] == 'goalkeeper'].sort_values(by='Overall', ascending=False).head(10)
# plt_cols = ['Reactions', 'Jumping', 'Strength', 'GKDiving', 'GKHandling', 'GKKicking', 'GKPositioning', 'GKReflexes']
# top_fwds.reset_index(inplace=True)
# plt_data = []
# for i in range(top_fwds.shape[0]):
#     trace = go.Scatterpolar(
#         r=top_fwds.loc[i, plt_cols],
#         theta=plt_cols,
#         # mode = 'lines',
#         name=top_fwds.loc[i, 'Name'],
#     )
#     plt_data.append(trace)
#
# layout = go.Layout(
#     polar=dict(
#         radialaxis=dict(
#             visible=True,
#             range=[40, 100],
#         )
#     ),
#     height=900,
#     width=900,
#     title="Top 10 goalkeepers",
#     showlegend=True
# )
#
# fig = go.Figure(data=plt_data, layout=layout)
# plot(fig)











