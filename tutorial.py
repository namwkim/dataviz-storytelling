import streamlit as st
import altair as alt
from vega_datasets import data
from PIL import Image

# st.set_page_config(page_title="Interactive Dashboard", layout="wide")

st.title("Getting Started with Streamlit")

st.header("Basic Content Display with `st.write()`")

st.markdown('''`st.write()` is Streamlit's most versatile method for displaying text, data, and media. It can render Markdown, images, dataframes, and even interactive widgets like charts—all with a single command.''')

st.markdown("Here are some examples of `st.write()` in action:")
st.code('''            
    # Formatting with Markdown
    st.write("**Boston college**: *Data Visualization and Storytelling*")  
    
    # Display an image
    st.write(Image.open('bc.jpg'))

    # Display a DataFrame
    st.write(cars) 

    # Display an interactive chart
    st.write(alt.Chart(cars).mark_circle().encode(
        x='Horsepower',
        y='Miles_per_Gallon',
        color='Origin'
    ).interactive())
''')

st.markdown("And here's how they look:")

st.divider()

st.write("**Boston college**: *Data Visualization and Storytelling*")  

st.write(Image.open('bc.jpg'))

cars = data.cars()
st.write(cars) # Display a DataFrame

st.write(alt.Chart(cars).mark_circle().encode(
    x='Horsepower',
    y='Miles_per_Gallon',
    color='Origin'
).interactive())

st.divider()

st.markdown("While `st.write` is great, Streamlit also provides specialized methods for displaying specific types of content. For example, `st.dataframe()` is a more specialized method for displaying DataFrames, and `st.altair_chart()` is a more specialized method for displaying Altair charts.")

st.markdown("Using these specific methods can make your code more readable and maintainable, and can also provide additional parameters that are specific to the type of content you're displaying. For instance, if `theme` is set to `None` in `st.altair_chart()`, Streamlit defaults to Altair's color theme.")
# st.altair_chart(c, )


st.header("Interactive Filtering with Input Widgets")


st.markdown("""
Streamlit provides **various UI widgets** that allow users to interact with an app. In this section, we focus on:  
✅ **`st.selectbox()`** – Choose one option from a dropdown list.  
✅ **`st.radio()`** – Select a single option from a horizontal/vertical list.  
✅ **`st.slider()`** – Select a numerical range with a slider.  

You can combine these widgets with Altair visualizations to create **interactive filters** that update the chart based on user input.

Below is an example that demonstrates how to use these widgets to filter a dataset of cars by origin and horsepower, and display the filtered data in a scatterplot or bar chart.
""")


st.code('''
    # Selectbox: Filter by Origin
    origin = st.selectbox("Filter by Origin", options=cars["Origin"].unique())

    # Radio: Choose Chart Type
    chart_type = st.radio("Choose Chart Type", ["Scatterplot", "Bar Chart"])

    # Slider: Filter by Horsepower
    horsepower_range = st.slider("Select Horsepower Range",
                                int(cars["Horsepower"].min()), 
                                int(cars["Horsepower"].max()), 
                                (50, 200))

    # Apply filters
    filtered_cars = cars[(cars["Origin"] == origin) & 
                        (cars["Horsepower"].between(*horsepower_range))]

    # Generate chart dynamically
    if chart_type == "Scatterplot":
        chart = alt.Chart(filtered_cars).mark_circle(size=60).encode(
            x="Horsepower",
            y="Miles_per_Gallon",
            color="Origin",
            tooltip=["Name", "Horsepower", "Miles_per_Gallon"]
        )
    else:
        chart = alt.Chart(filtered_cars).mark_bar().encode(
            x="Origin",
            y="average(Horsepower)",
            color="Origin"
        )

    # Display the chart
    st.altair_chart(chart, use_container_width=True)
''')

st.markdown("Here's how the interactive filtering looks in action:")
st.divider()

# Selectbox: Filter by Origin (Includes "All" Option)
origin_options = ["All"] + list(cars["Origin"].unique())
origin = st.selectbox("Filter by Origin", options=origin_options)

# Radio: Choose Chart Type
chart_type = st.radio("Choose Chart Type", ["Scatterplot", "Histogram"])

# Slider: Filter by Horsepower
horsepower_range = st.slider("Select Horsepower Range",
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

st.divider()

st.markdown("While Altair provides its own interactive widgets, Streamlit's widgets can be used across the entire page rather than being limited to individual Altair charts. Additionally, they offer a more aesthetically pleasing look and feel. You can check out other input widgets in the [Streamlit documentation: Input Widgets](https://docs.streamlit.io/develop/api-reference/widgets).")


st.header("Layout Customization – Structuring Your Dashboard")

st.markdown("""
##### 1️⃣ Setting the Page Width

By default, Streamlit apps use a `centered` layout, but we can adjust the width using `st.set_page_config()`.

```python

st.set_page_config(page_title="Interactive Dashboard", layout="wide")

```

The `layout` parameter can be set to `centered` (default) or `wide`. The `wide` layout extends the app to the full width of the browser window. This can be useful for multi-column dashboards or apps with wide visualizations. 

The parameter `page_title` sets the title of the app, which appears in the browser tab. Feel free to check out the [Streamlit documentation: Configuration](https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config) for more information on `st.set_page_config()`.

Here's a visual comparison of the `centered` and `wide` layouts:
""")
st.divider()
st.text("Centered:")
st.image("centered_layout.png")

st.text("Wide:")
st.image("wide_layout.png")
st.divider()
st.markdown("""
##### 2️⃣ Arranging Components with Columns

Streamlit's `st.columns()` helps create **side-by-side layouts** for a more structured dashboard. 

Below is an example that splits the screen into two equal-width columns, with a scatterplot in one column and a histogram in the other.


```python

col1, col2 = st.columns(2)  # Split into two equal-width columns

with col1:
    st.subheader("📊 Scatterplot")
    scatter = alt.Chart(cars).mark_circle(size=60).encode(
        x="Horsepower", y="Miles_per_Gallon", color="Origin"
    )
    st.altair_chart(scatter, use_container_width=True)

with col2:
    st.subheader("📊 Histogram")
    histogram = alt.Chart(cars).mark_bar().encode(
        x=alt.X("Horsepower", bin=True), y="count()", color="Origin"
    )
    st.altair_chart(histogram, use_container_width=True)
```

Here is how the layout looks in action:
""") 

st.divider()
col1, col2 = st.columns(2)  # Split into two equal-width columns

with col1:
    st.text("📊 Scatterplot")
    scatter = alt.Chart(cars).mark_circle(size=60).encode(
        x="Horsepower", y="Miles_per_Gallon", color="Origin"
    )
    st.altair_chart(scatter, use_container_width=True)

with col2:
    st.text("📊 Histogram")
    histogram = alt.Chart(cars).mark_bar().encode(
        x=alt.X("Horsepower", bin=True), y="count()", color="Origin"
    )
    st.altair_chart(histogram, use_container_width=True)
    
st.divider()

st.markdown("""
##### 3️⃣ Using the Sidebar for Filters & Navigation

The **sidebar** (`st.sidebar`) is useful for placing global filters, navigation menus, or extra information without cluttering the main content.

Below is an example that uses the sidebar to filter the dataset by origin and horsepower range. The filtered data is then displayed in the main content area.

```python
st.sidebar.header("🔍 Filters")

# Sidebar Filters
origin = st.sidebar.selectbox("Filter by Origin", ["All"] + list(cars["Origin"].unique()))
horsepower_range = st.sidebar.slider("Select Horsepower Range",
                                     int(cars["Horsepower"].min()), 
                                     int(cars["Horsepower"].max()), 
                                     (50, 200))

# Apply Filters
filtered_cars = cars if origin == "All" else cars[cars["Origin"] == origin]
filtered_cars = filtered_cars[filtered_cars["Horsepower"].between(*horsepower_range)]

# Display Data
st.write(f"Showing results for **{origin}** with horsepower between **{horsepower_range}**")
st.dataframe(filtered_cars)
```

Here's how the sidebar filters look in action:
""")

st.divider()

st.video("sidebar_example.mp4")

st.divider()

st.markdown("You can combine these layout customization techniques to create a more structured and visually appealing dashboard. Check out different layout and container options in the [Streamlit documentation: Layouts & containers](https://docs.streamlit.io/develop/api-reference/layout).")