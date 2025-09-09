import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go 
import pydeck as pdk

# Title
st.title("Motor Vehicle Collisions in New York City")
st.markdown("This is a platform for interactive analysis of vehicle collisions in NYC 🚦")

# Load dataset
DATA_URL = ("Motor_Vehicle_Collisions_-_Crashes.csv")

@st.cache_data(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)  # Drop Null values
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'data/time'}, inplace=True)
    return data

data = load_data(10000)
original_data = data

# Show raw data
if st.checkbox("Show Raw Data"):
    st.subheader('Raw Data')
    st.write(data)

# Where are the most people injured
st.header('📍 Where are the most people injured in New York City?')
injured_people = st.slider('Number of persons injured in vehicle collisions', 0, 20)
st.map(data.query('injured_persons >= @injured_people')[['latitude', 'longitude']].dropna(how='any'))

# How many collisions occur during a given time of the day
st.header('⏰ How many collisions occur during a given time of the day?')
hour = st.selectbox('Hour to look at', range(0, 24), 1)
data_hour = data[data['data/time'].dt.hour == hour]

st.markdown('Vehicle Collisions between %i:00 and %i:00' % (hour, (hour+1) % 24))

midpoint = (np.average(data_hour['latitude']), np.average(data_hour['longitude']))
st.write(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state={
        'latitude': midpoint[0],
        'longitude': midpoint[1],
        'zoom': 11,
        'pitch': 50
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data_hour[['data/time', 'longitude', 'latitude']],
            get_position='[longitude, latitude]',
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],
        ),
    ],
))

st.subheader('Breakdown by minute between %i:00 and %i:00' % (hour, (hour+1) % 24))
filtered = data[
    (data['data/time'].dt.hour == hour) & (data['data/time'].dt.hour < (hour+1))
]
hist = np.histogram(filtered['data/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minutes': range(60), 'crashes': hist})
fig = px.bar(chart_data, x='minutes', y='crashes', hover_data=['minutes', 'crashes'], height=400)
st.write(fig)

# =====================================================
# 📈 NEW SECTION: Time-series trend analysis
# =====================================================
st.header("📈 Collision Trends Over Time (Monthly)")

# Extract month-year
data['month_year'] = data['data/time'].dt.to_period('M')

# Group by month-year
monthly_trends = data.groupby('month_year').size().reset_index(name='collisions')
monthly_trends['month_year'] = monthly_trends['month_year'].dt.to_timestamp()

# Plot overall trend
fig_trend = px.line(
    monthly_trends,
    x='month_year',
    y='collisions',
    title="Monthly Collision Trends in NYC",
    labels={'month_year': 'Month-Year', 'collisions': 'Number of Collisions'}
)
st.plotly_chart(fig_trend, use_container_width=True)

# Optional: Year filter
years = monthly_trends['month_year'].dt.year.unique()
selected_year = st.selectbox("Select Year to Analyze", years)

filtered_trends = monthly_trends[monthly_trends['month_year'].dt.year == selected_year]

fig_year = px.line(
    filtered_trends,
    x='month_year',
    y='collisions',
    title=f"Collision Trends in {selected_year}",
    labels={'month_year': 'Month', 'collisions': 'Number of Collisions'}
)
st.plotly_chart(fig_year, use_container_width=True)

#display dangerous streets of NY