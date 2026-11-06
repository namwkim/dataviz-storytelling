import streamlit as st
import story_charts as sc

st.set_page_config(page_title="An Analysis of US Petition Filing Trends", layout="wide")


@st.cache_data
def get_data():
    return sc.load_data()


df = get_data()
us_map = sc.load_us_map()

# ---------------------------------------------------------------------------
# Story points: a caption (shown in the navigator), narrative text, and a chart
# ---------------------------------------------------------------------------
STORY = [
    {
        "caption": "Petitions Have Surged, Peaking in 2015",
        "text": "Let's begin by looking at the overall trend. The number of petitions "
                "filed saw a dramatic increase between 2011 and 2015, more than tripling "
                "in volume. However, this period of rapid growth ended with a sharp "
                "decline in 2016. This raises the question: **who is driving this trend?**",
        "chart": lambda: sc.trend_chart(df),
    },
    {
        "caption": "IT & Consulting Giants Dominate Filings",
        "text": "The surge in petitions isn't spread evenly across all companies. A closer "
                "look reveals that a handful of Information Technology and consulting "
                "firms are the primary drivers. Companies like **Infosys** and **Tata "
                "Consultancy** lead the pack by a significant margin.",
        "chart": lambda: sc.employer_chart(df),
    },
    {
        "caption": "Filings Are Concentrated in US Tech & Business Hubs",
        "text": "Geographically, these petitions are not filed uniformly across the "
                "country. Instead, they are heavily concentrated in major economic "
                "centers known for their technology and business sectors, particularly "
                "in **California, Texas, and the Northeast**.",
        "chart": lambda: sc.city_map(df, us_map),
    },
    {
        "caption": "High-Volume Filers Tend to Offer Mid-Range Salaries",
        "text": "Finally, let's look at the relationship between petition volume and "
                "salary. An interesting pattern emerges: the employers filing the most "
                "petitions consistently offer median salaries in the **\\$60,000 to "
                "\\$80,000** range. Companies offering higher salaries tend to file far "
                "fewer petitions.",
        "chart": lambda: sc.salary_scatter(df),
    },
    {
        "caption": "Now, It's Your Turn to Explore the Data",
        "text": "You've seen the author's story. Now use the dashboard below to ask your "
                "own questions. Switch the measure, drag across the line chart to pick "
                "years, and compare employers or job titles.",
        "chart": None,  # the interactive dashboard is drawn instead
    },
]

if "point" not in st.session_state:
    st.session_state.point = 0


def go(i):
    st.session_state.point = max(0, min(len(STORY) - 1, i))


# ---------------------------------------------------------------------------
# Title and story-point navigator (like Tableau's story caption boxes)
# ---------------------------------------------------------------------------
st.title("An Analysis of US Petition Filing Trends")

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
               use_container_width=True)

st.progress((st.session_state.point + 1) / len(STORY),
            text=f"Story point {st.session_state.point + 1} of {len(STORY)}")

# ---------------------------------------------------------------------------
# Current story point
# ---------------------------------------------------------------------------
point = STORY[st.session_state.point]
st.subheader(point["caption"])

if point["chart"] is None:
    st.info(point["text"])
    sc.explore_dashboard(df, us_map)
else:
    text_col, chart_col = st.columns([1, 2.4], vertical_alignment="center")
    with text_col:
        st.info(point["text"])
    with chart_col:
        st.altair_chart(point["chart"](), use_container_width=True)

st.caption("Data: H1B petitions 2011–2016 (sample of 190,633 petitions from 89 employers). "
           "Built with Altair and Streamlit. Tableau version: "
           "[Story Points on Tableau Public]"
           "(https://public.tableau.com/app/profile/nam.wook.kim7382/viz/PBL-2024-Fall-Dashboard-Excercise/Story1)")
