import streamlit as st
import altair as alt
from vega_datasets import data
st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

cars = data.cars()

# write a scatter plot using cars dataset
st.write("## Cars scatter plot")
c = alt.Chart(cars).mark_circle().encode(
    x='Horsepower',
    y='Miles_per_Gallon',
    color='Origin'
).interactive()
st.altair_chart(c, use_container_width=True)


