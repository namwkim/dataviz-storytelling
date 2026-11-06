import inspect
import streamlit as st
import story_charts as sc

st.set_page_config(page_title="Breakdown of the H1B Data Story", layout="wide")

STORY_URL = "https://dataviz-storytelling-story.streamlit.app/"
TABLEAU_URL = ("https://public.tableau.com/app/profile/nam.wook.kim7382/viz/"
               "PBL-2024-Fall-Dashboard-Excercise/Story1")


@st.cache_data
def get_data():
    return sc.load_data()


df = get_data()
us_map = sc.load_us_map()


def show_code(func):
    """Show the exact source code of a chart function from story_charts.py."""
    st.code(inspect.getsource(func), language="python")


with st.sidebar:
    st.markdown("# Outline")
    st.markdown("[0. Plan the Story](#plan)")
    st.markdown("[1. Load the Data](#load)")
    st.markdown("[2. Point 1: Overall Trend](#point1)")
    st.markdown("[3. Point 2: Top Employers](#point2)")
    st.markdown("[4. Point 3: Geography](#point3)")
    st.markdown("[5. Point 4: Salary vs. Volume](#point4)")
    st.markdown("[6. Point 5: Free Exploration](#point5)")
    st.markdown("[7. Assemble the Story](#assemble)")
    st.markdown("[8. Deploy](#deploy)")

st.title("📖 Breakdown of the H1B Data Story")
st.markdown(f"""
In the Tableau module, we used **Story Points** to turn the H1B dashboard into a guided
data story ([see the Tableau version]({TABLEAU_URL})). Here we build **the same story with
Altair and Streamlit**. Each section below explains one step, shows the code, and shows
the live output. The final story is deployed here: **[{STORY_URL}]({STORY_URL})**.
""")

# ---------------------------------------------------------------------------
st.header("0. Plan the Story", anchor="plan")
st.markdown("""
Before writing code, we sketch the narrative. The Tableau story follows a
**martini glass structure**: the author first drives a short, focused sequence of
findings (the stem), then opens up the data for the reader to explore (the bowl).

| # | Story point (caption) | Chart | Altair technique for the "author's voice" |
|---|---|---|---|
| 1 | Petitions Have Surged, Peaking in 2015 | Line chart by year | Highlight + text annotation on the peak |
| 2 | IT & Consulting Giants Dominate Filings | Bar chart by employer | Conditional color to highlight the top 6 |
| 3 | Filings Are Concentrated in US Tech & Business Hubs | Map of cities | Highlight + label the top cities |
| 4 | High-Volume Filers Tend to Offer Mid-Range Salaries | Scatter plot by employer | Trend line + red box + note |
| 5 | Now, It's Your Turn to Explore the Data | Interactive dashboard | Brush filter and dropdowns |

Tableau gives us story points, captions, and annotations out of the box. With Altair and
Streamlit, we build each piece ourselves:

- **Charts and annotations** → Altair layers (`+`) of marks such as `mark_text` and `mark_rect`.
- **Emphasis** → `alt.condition` to color the marks we want readers to notice.
- **Narrative text** → `st.info` boxes next to each chart.
- **Story point navigation** → a row of `st.button`s plus `st.session_state`.

To keep things tidy, all chart code lives in `story_charts.py`. The final app
(`story.py`) and this walkthrough (`story-steps.py`) both import it.
""")

# ---------------------------------------------------------------------------
st.header("1. Load the Data", anchor="load")
st.markdown("""
We use the same H1B dataset as the dashboard module (190,633 petitions, 2011–2016).
We attach a latitude and longitude to each city so we can draw the map. We keep the raw
salary values here (no outlier removal), so the numbers match the Tableau story exactly.
In the app, we wrap the loader with `@st.cache_data` so the CSV is read only once.
""")
show_code(sc.load_data)
st.code('''@st.cache_data
def get_data():
    return sc.load_data()

df = get_data()''', language="python")
st.dataframe(df.head(), use_container_width=True)

# ---------------------------------------------------------------------------
st.header("2. Story Point 1: Petitions Have Surged, Peaking in 2015", anchor="point1")
st.markdown("""
We count petitions per year with `pandas` and draw a line chart. To give the chart an
author's voice, we **layer** extra marks on top of the line:

- a large red circle on the peak year (2015),
- a bold label with the exact count, and
- a short note: *"A steady four-year climb culminates here."*

Each annotation is just another `alt.Chart` built from a one-row DataFrame, combined
with `+`. We also stretch the y-axis to 62,000 to leave room for the label above the peak.
""")
show_code(sc.trend_chart)
st.markdown("**Output:**")
st.altair_chart(sc.trend_chart(df), use_container_width=True)

# ---------------------------------------------------------------------------
st.header("3. Story Point 2: IT & Consulting Giants Dominate Filings", anchor="point2")
st.markdown("""
Next, we ask *who* drives the trend. We rank employers by petition count and keep the
top 30. Instead of coloring every bar the same, we use `alt.condition` to paint the
**top 6 in dark blue** and the rest in light gray. Value labels appear only on the
highlighted bars. This directs the reader's eye, just like Tableau's highlight.

One gotcha: `sort="-x"` does not work on a **layered** chart (bars + labels). So we pass
the sorted list of employer names to `sort=` instead.
""")
show_code(sc.employer_chart)
st.markdown("**Output:**")
st.altair_chart(sc.employer_chart(df), use_container_width=True)

# ---------------------------------------------------------------------------
st.header("4. Story Point 3: Filings Are Concentrated in US Tech & Business Hubs",
          anchor="point3")
st.markdown("""
Now we look at *where* the petitions come from. We aggregate petitions by city and draw
circles on a US map (`mark_geoshape` with the `albersUsa` projection for the background).

- Circle **size** encodes the number of petitions.
- The **top 10 cities** are highlighted and labeled. Other cities stay light gray as context.
- To avoid overlapping labels, we skip a label when a bigger labeled city is right next
  to it (e.g., Seattle next to Redmond). We also move some labels to the left side.
- `order=` draws large circles on top so they are not hidden.
""")
show_code(sc.city_map)
st.markdown("**Output:**")
st.altair_chart(sc.city_map(df, us_map), use_container_width=True)

# ---------------------------------------------------------------------------
st.header("5. Story Point 4: High-Volume Filers Tend to Offer Mid-Range Salaries",
          anchor="point4")
st.markdown("""
Finally, we relate volume to salary. Each point is one employer: x is the median salary
and y is the number of petitions. We add three layers:

- a **linear trend line** with `transform_regression` (Tableau's trend line),
- a **red box** around the \\$60k–\\$80k band with `mark_rect(fill=None, stroke=...)`, and
- a **note** inside the box with `mark_text` (`lineBreak="|"` splits it into two lines).

The red box makes the takeaway obvious: the largest filers cluster in that salary band.
""")
show_code(sc.salary_scatter)
st.markdown("**Output:**")
st.altair_chart(sc.salary_scatter(df), use_container_width=True)

# ---------------------------------------------------------------------------
st.header("6. Story Point 5: Now, It's Your Turn to Explore the Data", anchor="point5")
st.markdown(f"""
The last point opens the "bowl" of the martini glass. We hand control to the reader with
a compact version of the dashboard from the previous module:

- a **measure** dropdown (number of petitions or median salary),
- a line chart with a **brush** (`alt.selection_interval`). We read the selected years with
  `on_select="rerun"` and filter the data for the views below,
- a bar chart by employer or job title, a city map, and a scatter plot.

See it live in the final story (last story point): [{STORY_URL}]({STORY_URL}).
""")
with st.expander("Show the code for the exploration dashboard"):
    show_code(sc.explore_dashboard)

# ---------------------------------------------------------------------------
st.header("7. Assemble the Story", anchor="assemble")
st.markdown("""
Now we put the pieces together in `story.py`. Each story point is a small dictionary with
a **caption** (shown in the navigator), the **narrative text**, and a **chart**.
We wrap each chart in a `lambda` so it is only built when that point is shown.
""")
st.code('''STORY = [
    {
        "caption": "Petitions Have Surged, Peaking in 2015",
        "text": "Let's begin by looking at the overall trend. ...",
        "chart": lambda: sc.trend_chart(df),
    },
    {
        "caption": "IT & Consulting Giants Dominate Filings",
        "text": "The surge in petitions isn't spread evenly across all companies. ...",
        "chart": lambda: sc.employer_chart(df),
    },
    # ... story points 3 and 4 ...
    {
        "caption": "Now, It's Your Turn to Explore the Data",
        "text": "You've seen the author's story. Now use the dashboard below ...",
        "chart": None,  # the interactive dashboard is drawn instead
    },
]''', language="python")

st.markdown("""
Streamlit reruns the whole script on every click, so we remember the current story point
in `st.session_state`. The navigator is a row of buttons, like Tableau's caption boxes:
◀ and ▶ move one step, and each caption jumps straight to its point. The current point
uses `type="primary"` so it stands out.
""")
st.code('''if "point" not in st.session_state:
    st.session_state.point = 0

def go(i):
    st.session_state.point = max(0, min(len(STORY) - 1, i))

nav = st.columns([0.5] + [2] * len(STORY) + [0.5])
nav[0].button("◀", on_click=go, args=(st.session_state.point - 1,),
              disabled=st.session_state.point == 0, use_container_width=True)
for i, point in enumerate(STORY):
    nav[i + 1].button(
        point["caption"], key=f"nav{i}", on_click=go, args=(i,),
        type="primary" if i == st.session_state.point else "secondary",
        use_container_width=True,
    )
nav[-1].button("▶", on_click=go, args=(st.session_state.point + 1,),
               disabled=st.session_state.point == len(STORY) - 1,
               use_container_width=True)''', language="python")

st.markdown("""
Last, we draw the current point: the narrative in an `st.info` box on the left and the
chart on the right. For the final point we draw the exploration dashboard instead.
""")
st.code('''point = STORY[st.session_state.point]
st.subheader(point["caption"])

if point["chart"] is None:
    st.info(point["text"])
    sc.explore_dashboard(df, us_map)
else:
    text_col, chart_col = st.columns([1, 2.4], vertical_alignment="center")
    with text_col:
        st.info(point["text"])
    with chart_col:
        st.altair_chart(point["chart"](), use_container_width=True)''', language="python")

with st.expander("Show the full story.py"):
    with open("story.py") as f:
        st.code(f.read(), language="python")

# ---------------------------------------------------------------------------
st.header("8. Deploy", anchor="deploy")
st.markdown(f"""
We deploy the story the same way as the dashboard:

1. Put `story.py`, `story_charts.py`, `h1b_data.csv`, `us_cities.csv`, and
   `requirements.txt` in a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io), click **Create app**, pick the
   repository, and set the main file to `story.py`.
3. Share the app URL, or embed it in a web page with an `<iframe>`.

Final story: **[{STORY_URL}]({STORY_URL})**
""")
