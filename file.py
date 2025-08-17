import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go 
import pydeck as pdk

#title
st.title("Motor vehicles collision in New York City")

st.markdown("this is a platform for analysis")

DATA_URL = ("Motor.csv")

@st.cache_data(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows,parse_dates=[['CRASH_DATE','CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'],inplace=True) #Dropped Null values
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase,axis='columns',inplace=True)
    data.rename(columns={'crash_date_crash_time': 'data/time'}, inplace=True)
    return data

data = load_data(10000)
original_data = data

#show the data
if st.checkbox("Show Raw Data"):
    st.subheader('Raw Data')
    st.write(data)

#where are the most people injured 
st.header('Where are the most people injured in New York City ?')
injured_people = st.slider('Number of persons injured in vehicle collisions', 0, 20)
st.map(data.query('injured_persons >= @injured_people')[['latitude','longitude']].dropna(how='any'))

#how many collisions occur during a given time of the day    

st.header('How many collisions occur during a given time of the day ?')
hour = st.selectbox('Hour to look at ', range(0,24),1)
data = data[data['data/time'].dt.hour == hour]

st.markdown('Vehicle Collisions between %i:00 and %i:00' % (hour, (hour+1) % 24))

midpoint = (np.average(data['latitude']),np.average(data['longitude']))
st.write(pdk.Deck (
    map_style = 'mapbox://styles/mapbox/light-v9',
    initial_view_state={
        'latitude':midpoint[0],
        'longitude':midpoint[1],
        'zoom':11,
        'pitch': 50
    },
    layers = [
        pdk.Layer(
            "HexagonLayer",
            data=data[['data/time','longitude','latitude']],   
            get_position='[longitude,latitude]',
            radius=100,
            extruded=True,
            pickable = True,
            elevation_scale=4,
            elevation_range=[0,1000],
        ),
    ],
))

st.subheader('Breakdown by minute between %i:00 and %i:00'%(hour, (hour+1) % 24))

# Will Breakdown into minutes and visualise using histogram

#display dangerous streets of NY