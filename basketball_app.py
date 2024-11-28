import streamlit as st
import pandas as pd
import base64
from PIL import Image
import altair as alt

st.set_page_config(
     page_title="NBA Statistics App",
     page_icon="🏀")

# Sidebar - Year selection

st.sidebar.header('User Input')
selected_year = st.sidebar.selectbox('Year',list(reversed(range(1976,2025))))


# Web scraping and Data cleaning
@st.cache

def load_data(year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_totals.html"
    html = pd.read_html(url, header = 0)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index) # Deletes repeating headers in content
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)
    return playerstats
playerstats = load_data(selected_year)


# Sidebar - Team selection
playerstats = playerstats[playerstats['Team'] != 'TOT'] 
playerstats['Team']=playerstats['Team'].astype(str)
sorted_unique_team = sorted(playerstats.Team.unique())
selected_team = st.sidebar.selectbox('Team',sorted_unique_team[:])
#selected_team = st.sidebar.multiselect('Team',sorted_unique_team, sorted_unique_team[:1])


# Sidebar - Position selection
unique_pos = ['C','PF','SF','PG','SG']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

with st.sidebar:
    st.write(" **C**= Center **PF**= Power Foward  **SF**= Small Foward **PG** = Point Gard **SG**= Shooting Gard")

# Filtering data
df_selected_team = playerstats[(playerstats.Tm.str.contains(selected_team)) & (playerstats.Pos.isin(selected_pos))]
#df_selected_team = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

# Title
st.title('NBA Player Statistics  '+''.join(selected_team)+' '+ str(selected_year) )

st.markdown("""
#### This app performs web data extraction of NBA players statistics

* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/)
""")

image = Image.open('NBA.jpg')

st.image(image, width=350) 

st.markdown("""
***
""")


st.header('Player Statistics of '+ ''.join(selected_team)+' Team in '+str(selected_year)+ ' Season' )
st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
test = df_selected_team.astype(str)
st.dataframe(test.sort_values(by=['Player']))

# Download NBA player stats data
test3=playerstats.astype(str) 
season=test3.sort_values(by=['Tm','Player'],
                         ascending = [True, True])

def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

#csv = convert_df(df_selected_team)
csv= convert_df(season)

st.download_button(
     label="Download " +str(selected_year)+ ' Season as CSV',
     data=csv,
     file_name='Season '+str(selected_year)+'.csv',
     mime='text/csv',
 )

# Visualization
df_selected_team = df_selected_team.astype({'PTS':'int','G':'int','TRB':'int'})
df_selected_team['PG'] = (df_selected_team['PTS'] / df_selected_team['G']).round(2)
df_selected_team.loc[:,'PG'] = df_selected_team['PG'].map('{:.2f}'.format)
df_selected_team['TRB_per_Game'] = (df_selected_team['TRB'] / df_selected_team['G']).round(2)

keep_cols = ['Player', 'Age','Pos','G', 'PTS','3P','FG','2P','FT','PG','DRB','STL','BLK','AST','TOV','TRB','TRB_per_Game']

df_selected_team1 = df_selected_team.loc[:,keep_cols]
df_selected_team1['PG'] = pd.to_numeric(df_selected_team1['PG'],errors='coerce')
df_selected_team1['FG'] = pd.to_numeric(df_selected_team1['FG'],errors='coerce')
df_selected_team1['3P'] = pd.to_numeric(df_selected_team1['3P'],errors='coerce')
df_selected_team1['DRB'] = pd.to_numeric(df_selected_team1['DRB'],errors='coerce')
df_selected_team1['AST'] = pd.to_numeric(df_selected_team1['AST'],errors='coerce')
df_selected_team1['TRB_per_Game'] = pd.to_numeric(df_selected_team1['TRB_per_Game'],errors='coerce')
#st.dataframe(df_selected_team1.sort_values(by=['Player']))

st.subheader('Total Points by ' + ''.join(selected_team)+ ' Players '+str(selected_year)+' Season')
p = alt.Chart(df_selected_team1.sort_values(by=['PTS'])).mark_point(filled=True,size=30).encode(
    alt.X('PTS'),
    alt.Y('Player'),
    alt.Size('PG'),    
    tooltip = ['Player','PTS','PG','FG','2P','2P','FT']               
              )
p = p.properties(
    width= 700,
    height=500  
)
st.write(p)

st.subheader('Defensive Statistics by  ' + ''.join(selected_team)+ ' Players '+str(selected_year)+' Season')
p2 = alt.Chart(df_selected_team1.sort_values(by=['FG'])).mark_point(filled=True,size=30).encode(
    alt.X('TRB'),
    alt.Y('Player'),
    alt.Size('AST'),
    tooltip = ['Player','TRB','TRB_per_Game','STL','AST','BLK','TOV']                
              )
p2 = p2.properties(
    width= 700,
    height=500  
)
st.write(p2)


st.subheader('Season '+str(selected_year)+' Information')


url = "https://www.basketball-reference.com/leagues/"
html = pd.read_html(url,header = 1)
df = html[0]
raw = df.drop(df[df.Champion == 'Champion'].index)
raw = raw.fillna(0)
Champion_stats = raw.drop(['Lg'], axis=1)
 

test2 = Champion_stats.astype(str)

n=(2023-selected_year)

st.dataframe(test2.loc[n,:])
