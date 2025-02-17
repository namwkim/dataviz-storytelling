import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from scipy import stats

st.set_page_config(page_title="H1B Visa Analysis Dashboard", layout="wide")

# Load H1B dataset
@st.cache_data
def load_h1b_data():
    return pd.read_csv("h1b_data.csv")  # Ensure this file is available

df = load_h1b_data()

# Load city dataset (for latitude & longitude)
@st.cache_data
def load_city_data():
    return pd.read_csv("us_cities.csv")  # Ensure this file is available

# Load TopoJSON for the US Map
@st.cache_data
def load_us_map():
    return alt.topo_feature("https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json", "states")


us_map = load_us_map()

city_df = load_city_data()

# Merge H1B data with city coordinates
df["STATE"] = df["STATE"].str.strip()
df["CITY"] = df["CITY"].str.strip()

city_df["city"] = city_df["city"].str.strip().str.upper()
city_df["state_name"] = city_df["state_name"].str.strip().str.upper()

df = df.merge(city_df[['city', 'state_name', 'lat', 'lng']],
              left_on=['CITY', 'STATE'],
              right_on=['city', 'state_name'],
              how='left')

# Outlier removal
z = np.abs(stats.zscore(df['PREVAILING_WAGE']))
df = df[(z < 3)]

# Configure layout
st.title("📊 H1B Visa Analysis Dashboard")

# **Top Section ****************************************************************
st.subheader("📈 Overview of H1B Petitions Over Time")

# Dropdown to select measure
measure_options = {"Number of Petitions": "Count of Petitions",
                   "Salary (Prevailing Wage)": "Prevailing Wage"}
selected_measure = st.selectbox(
    "Select Measure:", list(measure_options.keys()))

# Aggregate data for line chart
if selected_measure == "Number of Petitions":
    trend_data = df.groupby("YEAR").size().reset_index(
        name="Count of Petitions")
else:
    trend_data = df.groupby("YEAR")["PREVAILING_WAGE"].median(
    ).reset_index(name="Prevailing Wage")

# Line Chart
brush = alt.selection_interval(name="brush", encodings=['x']) # Brush for selection

line_chart = alt.Chart(trend_data).mark_line(point=True).encode(
    x="YEAR:O",
    y=measure_options[selected_measure],
    tooltip=["YEAR", measure_options[selected_measure]]
).add_params(brush) # Add brush to chart

# Grab selection
selection = st.altair_chart(line_chart, use_container_width=True, on_select='rerun')

# Filter based on selection e.g., [2021, 2022, 2023]
if 'YEAR' in selection['selection']['brush']:
    years = selection['selection']['brush']['YEAR']
    df = df[df['YEAR'].isin(years)]

st.divider()

# **Bottom Section: Three Columns ************************************************
col1, col2, col3 = st.columns([1, 1, 1])

# **First Column: Job Title / Employer Name**
with col1:
    st.subheader("📌 Breakdown by Job Title / Employer")

    # Dropdown for selecting category
    category_options = {"Job Title": "JOB_TITLE",
                        "Employer Name": "EMPLOYER_NAME"}
    selected_category = st.selectbox("Select Dimension:", list(
        category_options.keys()), key="category")

    # Aggregate data
    if selected_measure == "Number of Petitions":
        bar_data = df.groupby(category_options[selected_category]).size(
        ).reset_index(name="Count of Petitions")
    else:
        bar_data = df.groupby(category_options[selected_category])[
            "PREVAILING_WAGE"].mean().reset_index(name="Prevailing Wage")

    bar_data = bar_data.nlargest(
        20, measure_options[selected_measure])  # Select Top 10

    # Bar Chart
    bar_chart = alt.Chart(bar_data).mark_bar().encode(
        x=measure_options[selected_measure],
        y=alt.X(category_options[selected_category] +
                ":O", sort="-x"),  # Ensures descending order
        tooltip=[category_options[selected_category],
                 measure_options[selected_measure]]
    ).properties(height=alt.Step(20))

    st.altair_chart(bar_chart, use_container_width=True)

# **Second Column: Map / Boxplot**
with col2:
    st.subheader("🌍 Geographical Analysis")

    # Radio button to select Map or Boxplot
    chart_type = st.radio("Choose View:", ["Map", "Boxplot"], key="map_or_boxplot")
    print(chart_type)
    if chart_type == "Map":
        # Aggregate data for cities
        if selected_measure == "Number of Petitions":
            map_data = df.groupby(["CITY", "STATE", "lat", "lng"]).size().reset_index(name="Count of Petitions")
        else:
            map_data = df.groupby(["CITY", "STATE", "lat", "lng"])["PREVAILING_WAGE"].mean().reset_index(name="Prevailing Wage")

        # Background US Map (TopoJSON)
        background = alt.Chart(us_map).mark_geoshape(
            fill="whitesmoke",
            stroke="white"
        ).project(
            type="albersUsa"
        )
        # Overlay: Altair Map of cities
        city_layer = alt.Chart(map_data).mark_circle().encode(
            longitude="lng:Q",
            latitude="lat:Q",
            size=alt.Size(measure_options[selected_measure]+":Q", scale=alt.Scale(range=[10, 500])),
            color=alt.Color(measure_options[selected_measure]+":Q", scale=alt.Scale(scheme="reds")),
            tooltip=["CITY", "STATE", measure_options[selected_measure]]
        )

        # Combine Background + City Layer
        map_chart = background + city_layer
        st.altair_chart(map_chart, use_container_width=True)

    elif chart_type == "Boxplot":  # Make sure to use elif for clarity
        if selected_measure == "Number of Petitions":
            boxplot_data = df.groupby(["STATE", category_options[selected_category]]).size(
            ).reset_index(name="Count of Petitions")
        else:
            boxplot_data = df.groupby(["STATE", category_options[selected_category]])[
                "PREVAILING_WAGE"].mean().reset_index(name="Prevailing Wage")
            
        # Boxplot
        boxplot = alt.Chart(boxplot_data).mark_boxplot().encode(
            y="STATE:N",
            x=measure_options[selected_measure]+":Q"
        )
        st.altair_chart(boxplot, use_container_width=True)

# **Third Column: Scatter Plot**
with col3:
    st.subheader("🔄 Correlation Analysis")

    scatter_data = df.groupby(category_options[selected_category]).agg(
       **{"Count of Petitions": (category_options[selected_category], "count"),  # Count of rows**
       "Prevailing Wage": ("PREVAILING_WAGE", "median")}  # Median Salary
    ).reset_index()
    
    # Dropdown for second measure
    second_measure = st.selectbox("Select Second Measure:", list(
        measure_options.keys()), key="scatter_measure")

    # Scatter Plot
    scatter_chart = alt.Chart(scatter_data).mark_circle(size=60).encode(
        x=measure_options[selected_measure]+":Q",
        y=measure_options[second_measure]+":Q",
        color=alt.Color(measure_options[selected_measure]+":Q",scale=alt.Scale(scheme="blues")),
        tooltip=[category_options[selected_category], measure_options[selected_measure], measure_options[second_measure]]
    ).properties(height=350)

    st.altair_chart(scatter_chart, use_container_width=True)
