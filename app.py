#C:\Users\asus\Downloads\football results dashboard

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Football Results Dashboard", layout="wide")

df = pd.read_csv("results.csv")
df['date'] = pd.to_datetime(df['date'])

st.title("Football Results Dashboard")
st.markdown("""
An interactive dashboard for analyzing international football match results.  
**Select your favorite teams, year, and get insights!**
""")

with st.sidebar:
    st.header("Filters")
    teams = sorted(list(set(df['home_team']).union(set(df['away_team']))))
    team1 = st.selectbox("Select Team 1", teams, index=teams.index('Iran') if 'Iran' in teams else 0)
    team2 = st.selectbox("Select Team 2 (optional)", [''] + teams)
    years = sorted(df['date'].dt.year.unique())
    year_range = st.slider("Select Year Range", int(min(years)), int(max(years)), (2000, int(max(years))))

filtered = df[
    ((df['home_team'] == team1) | (df['away_team'] == team1)) &
    (df['date'].dt.year >= year_range[0]) & (df['date'].dt.year <= year_range[1])
]

#team_stats
def get_team_stats(df, team):
    matches = df[(df['home_team'] == team) | (df['away_team'] == team)]
    wins = matches[((matches['home_team'] == team) & (matches['home_score'] > matches['away_score'])) |
                   ((matches['away_team'] == team) & (matches['away_score'] > matches['home_score']))]
    losses = matches[((matches['home_team'] == team) & (matches['home_score'] < matches['away_score'])) |
                     ((matches['away_team'] == team) & (matches['away_score'] < matches['home_score']))]
    draws = matches[matches['home_score'] == matches['away_score']]
    return len(wins), len(draws), len(losses), len(matches)

wins, draws, losses, total = get_team_stats(filtered, team1)

st.subheader(f"Summary for {team1} ({year_range[0]}–{year_range[1]})")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Wins", wins)
col2.metric("Draws", draws)
col3.metric("Losses", losses)
col4.metric("Total Matches", total)

fig1, ax1 = plt.subplots()
ax1.pie([wins, draws, losses], labels=["Wins", "Draws", "Losses"], autopct="%1.1f%%", startangle=140)
ax1.set_title(f"Results Distribution: {team1}")
st.pyplot(fig1)

trend = filtered.copy()
trend['result'] = trend.apply(
    lambda row: 'Win' if (
        (row['home_team'] == team1 and row['home_score'] > row['away_score']) or
        (row['away_team'] == team1 and row['away_score'] > row['home_score'])
    ) else ('Loss' if (
        (row['home_team'] == team1 and row['home_score'] < row['away_score']) or
        (row['away_team'] == team1 and row['away_score'] < row['home_score'])
    ) else 'Draw'), axis=1)
win_trend = trend.groupby(trend['date'].dt.year)['result'].value_counts().unstack().fillna(0)

st.subheader("Win/Loss/Draw Trend Over Time")
st.line_chart(win_trend)

# HeadToHead Table
if team2 and team2 != team1:
    st.subheader(f"Head-to-Head: {team1} vs {team2}")
    h2h = df[
        ((df['home_team'] == team1) & (df['away_team'] == team2)) |
        ((df['home_team'] == team2) & (df['away_team'] == team1))
    ]
    st.dataframe(h2h[['date', 'home_team', 'away_team', 'home_score', 'away_score', 'tournament', 'city']].sort_values('date', ascending=False))
    st.write(f"Total Matches: {len(h2h)}")
else:
    st.subheader(f"All Matches for {team1}")
    st.dataframe(filtered[['date', 'home_team', 'away_team', 'home_score', 'away_score', 'tournament', 'city']].sort_values('date', ascending=False))
