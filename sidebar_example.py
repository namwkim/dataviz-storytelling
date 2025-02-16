import streamlit as st
import altair as alt
from vega_datasets import data

cars = data.cars()

st.sidebar.header("🔍 Filters")

# Selectbox: Filter by Origin (Includes "All" Option)
origin_options = ["All"] + list(cars["Origin"].unique())
origin = st.sidebar.selectbox("Filter by Origin", options=origin_options)

# Radio: Choose Chart Type
chart_type = st.sidebar.radio("Choose Chart Type", ["Scatterplot", "Histogram"])

# Slider: Filter by Horsepower
horsepower_range = st.sidebar.slider("Select Horsepower Range",
                            int(cars["Horsepower"].min()), 
                            int(cars["Horsepower"].max()), 
                            (50, 200))

# Apply filters
filtered_cars = cars[cars["Horsepower"].between(*horsepower_range)]

# Apply origin filter if not "All"
if origin != "All":
    filtered_cars = filtered_cars[filtered_cars["Origin"] == origin]

# Generate chart dynamically
if chart_type == "Scatterplot":
    chart = alt.Chart(filtered_cars).mark_circle(size=60).encode(
        x="Horsepower",
        y="Miles_per_Gallon",
        color="Origin",
        tooltip=["Name", "Horsepower", "Miles_per_Gallon"]
    )
else:  # Histogram of Horsepower
    chart = alt.Chart(filtered_cars).mark_bar().encode(
        x=alt.X("Horsepower", bin=True), 
        y="count()",
        color="Origin"
    )

# Display the chart
st.altair_chart(chart, use_container_width=True)
