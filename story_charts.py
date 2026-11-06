"""Chart functions for the H1B data story (Altair version of the Tableau story).

Both story.py (final story) and story-steps.py (walkthrough) import from here,
so the code shown in the walkthrough is exactly the code that draws the story.
"""
import pandas as pd
import altair as alt

# Colors used across the story
HIGHLIGHT = "#2f5d8a"   # dark blue for the marks we want readers to notice
MUTED = "#c9d3de"       # light gray-blue for context marks
ACCENT = "#d62728"      # red for annotation boxes


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
def load_data(h1b_path="h1b_data.csv", cities_path="us_cities.csv"):
    """Load the H1B petitions and attach a latitude/longitude to each city."""
    df = pd.read_csv(h1b_path)
    df["STATE"] = df["STATE"].str.strip()
    df["CITY"] = df["CITY"].str.strip()

    cities = pd.read_csv(cities_path)
    cities["city"] = cities["city"].str.strip().str.upper()
    cities["state_name"] = cities["state_name"].str.strip().str.upper()
    cities = cities.drop_duplicates(["city", "state_name"])

    df = df.merge(
        cities[["city", "state_name", "lat", "lng"]],
        left_on=["CITY", "STATE"],
        right_on=["city", "state_name"],
        how="left",
    ).drop(columns=["city", "state_name"])
    return df


def load_us_map():
    """US state boundaries (TopoJSON) for the map background."""
    return alt.topo_feature(
        "https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json", "states"
    )


# ---------------------------------------------------------------------------
# Story point 1: Petitions have surged, peaking in 2015
# ---------------------------------------------------------------------------
def trend_chart(df):
    trend = df.groupby("YEAR").size().reset_index(name="Petitions")
    peak = trend.loc[trend["Petitions"].idxmax()]

    base = alt.Chart(trend).encode(
        x=alt.X("YEAR:O", title="Year", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Petitions:Q", title="Number of Petitions",
                scale=alt.Scale(domain=[0, 62000])),
    )
    line = base.mark_line(color=HIGHLIGHT, strokeWidth=3)
    points = base.mark_circle(color=HIGHLIGHT, size=70).encode(
        tooltip=["YEAR:O", alt.Tooltip("Petitions:Q", format=",")]
    )

    # Annotation: a callout on the peak year
    peak_df = pd.DataFrame([{
        "YEAR": int(peak["YEAR"]),
        "Petitions": int(peak["Petitions"]),
        "label": f"2015: {int(peak['Petitions']):,} petitions",
        "note": "A steady four-year climb culminates here.",
    }])
    peak_point = alt.Chart(peak_df).mark_circle(
        size=220, color=ACCENT, opacity=0.9
    ).encode(x="YEAR:O", y="Petitions:Q")
    peak_label = alt.Chart(peak_df).mark_text(
        align="center", dy=-38, fontSize=13, fontWeight="bold"
    ).encode(x="YEAR:O", y="Petitions:Q", text="label:N")
    peak_note = alt.Chart(peak_df).mark_text(
        align="center", dy=-20, fontSize=12, color="#555"
    ).encode(x="YEAR:O", y="Petitions:Q", text="note:N")

    return (line + points + peak_point + peak_label + peak_note).properties(
        height=420, title="Number of H1B Petitions per Year"
    )


# ---------------------------------------------------------------------------
# Story point 2: IT & consulting giants dominate filings
# ---------------------------------------------------------------------------
def employer_chart(df, top_n=30, highlight_n=6):
    employers = (
        df.groupby("EMPLOYER_NAME").size().reset_index(name="Petitions")
        .nlargest(top_n, "Petitions")
    )
    employers["Rank"] = range(1, len(employers) + 1)

    bars = alt.Chart(employers).mark_bar().encode(
        x=alt.X("Petitions:Q", title="Number of Petitions"),
        # Keep the bars in descending order (pass the order explicitly,
        # because sort="-x" is ignored when charts are layered)
        y=alt.Y("EMPLOYER_NAME:N", sort=list(employers["EMPLOYER_NAME"]), title=None,
                axis=alt.Axis(labelLimit=260, labelOverlap=False)),
        # Highlight the top filers, mute the rest
        color=alt.condition(
            f"datum.Rank <= {highlight_n}",
            alt.value(HIGHLIGHT),
            alt.value(MUTED),
        ),
        tooltip=["EMPLOYER_NAME", alt.Tooltip("Petitions:Q", format=",")],
    )
    labels = bars.mark_text(align="left", dx=4, fontSize=11).encode(
        text=alt.Text("Petitions:Q", format=","),
        color=alt.value("#333"),
    ).transform_filter(f"datum.Rank <= {highlight_n}")

    return (bars + labels).properties(
        height=alt.Step(20), title=f"Top {top_n} Employers by Number of Petitions"
    )


# ---------------------------------------------------------------------------
# Story point 3: Filings are concentrated in US tech & business hubs
# ---------------------------------------------------------------------------
def city_map(df, us_map, label_n=10):
    cities = (
        df.dropna(subset=["lat", "lng"])
        .groupby(["CITY", "STATE", "lat", "lng"]).size()
        .reset_index(name="Petitions")
        .sort_values("Petitions", ascending=False)
    )
    cities["Rank"] = range(1, len(cities) + 1)
    cities["Label"] = cities["CITY"].str.title()

    # Label the top cities, skipping a city that sits right next to a bigger
    # labeled one (e.g., Seattle next to Redmond) so labels do not overlap
    top = cities.head(label_n)
    keep = []
    for _, row in top.iterrows():
        near = any(abs(row.lat - k.lat) < 0.5 and abs(row.lng - k.lng) < 0.5 for k in keep)
        if not near:
            keep.append(row)
    labeled = pd.DataFrame(keep)
    # Put a label on the left side when a bigger labeled city is close by
    labeled["side"] = ["left" if i > 0 and any(
        abs(r.lat - o.lat) < 2 and abs(r.lng - o.lng) < 2 for o in keep[:i])
        else "right" for i, r in enumerate(keep)]

    background = alt.Chart(us_map).mark_geoshape(
        fill="#f2f2f2", stroke="white"
    ).project(type="albersUsa")

    circles = alt.Chart(cities).mark_circle(stroke="white", strokeWidth=0.5).encode(
        longitude="lng:Q",
        latitude="lat:Q",
        size=alt.Size("Petitions:Q", scale=alt.Scale(range=[5, 900]),
                      legend=alt.Legend(title="Petitions", format=",.0f")),
        color=alt.condition(
            f"datum.Rank <= {label_n}", alt.value(HIGHLIGHT), alt.value(MUTED)
        ),
        opacity=alt.condition(
            f"datum.Rank <= {label_n}", alt.value(0.9), alt.value(0.6)
        ),
        order=alt.Order("Petitions:Q"),  # draw big circles on top
        tooltip=["CITY", "STATE", alt.Tooltip("Petitions:Q", format=",")],
    )

    text = dict(fontSize=12, fontWeight="bold")
    right = alt.Chart(labeled[labeled.side == "right"]).mark_text(
        align="left", dx=12, **text
    ).encode(longitude="lng:Q", latitude="lat:Q", text="Label:N")
    left = alt.Chart(labeled[labeled.side == "left"]).mark_text(
        align="right", dx=-12, dy=6, **text
    ).encode(longitude="lng:Q", latitude="lat:Q", text="Label:N")

    return (background + circles + right + left).properties(
        height=480, title=f"Petitions by City (top {label_n} labeled)"
    )


# ---------------------------------------------------------------------------
# Story point 4: High-volume filers tend to offer mid-range salaries
# ---------------------------------------------------------------------------
def salary_scatter(df, low=60000, high=80000):
    employers = df.groupby("EMPLOYER_NAME").agg(
        Petitions=("EMPLOYER_NAME", "size"),
        MedianSalary=("PREVAILING_WAGE", "median"),
    ).reset_index()

    x = alt.X("MedianSalary:Q", title="Median Salary (USD)",
              axis=alt.Axis(format="$,.0f"))
    y = alt.Y("Petitions:Q", title="Number of Petitions")

    points = alt.Chart(employers).mark_point(
        filled=False, size=60, color=HIGHLIGHT
    ).encode(
        x=x, y=y,
        tooltip=["EMPLOYER_NAME",
                 alt.Tooltip("Petitions:Q", format=","),
                 alt.Tooltip("MedianSalary:Q", format="$,.0f")],
    )

    # Linear trend line, like Tableau's trend line
    trend = alt.Chart(employers).transform_regression(
        "MedianSalary", "Petitions"
    ).mark_line(color="gray").encode(x=x, y=y)

    # Annotation: a red box around the $60k-$80k band and a note
    top = int(employers["Petitions"].max() * 1.03)
    band = alt.Chart(pd.DataFrame([{"x1": low, "x2": high, "y1": 6000, "y2": top}]))
    box = band.mark_rect(fill=None, stroke=ACCENT, strokeWidth=2).encode(
        x="x1:Q", x2="x2:Q", y="y1:Q", y2="y2:Q"
    )
    note = alt.Chart(pd.DataFrame([{
        "x": low + 1000, "y": top * 0.80,
        "text": "Top filers fall within the|$60k–$80k median salary range",
    }])).mark_text(align="left", fontSize=12, color=ACCENT, lineBreak="|").encode(
        x="x:Q", y="y:Q", text="text:N"
    )

    return (trend + points + box + note).properties(
        height=440, title="Number of Petitions vs. Median Salary (one point per employer)"
    )


# ---------------------------------------------------------------------------
# Story point 5: Now it's your turn to explore the data
# ---------------------------------------------------------------------------
def explore_dashboard(df, us_map):
    """A compact version of the dashboard from 6.3, so readers can explore freely."""
    import streamlit as st

    measures = {"Number of Petitions": "Petitions", "Median Salary": "Median Salary"}
    dimensions = {"Employer Name": "EMPLOYER_NAME", "Job Title": "JOB_TITLE"}

    def aggregate(data, keys, measure):
        g = data.groupby(keys)
        if measure == "Petitions":
            return g.size().reset_index(name="Petitions")
        return g["PREVAILING_WAGE"].median().reset_index(name="Median Salary")

    measure = measures[st.selectbox("Measure", list(measures), key="ex_measure")]

    # Top: trend with a brush to filter the views below
    brush = alt.selection_interval(name="brush", encodings=["x"])
    line = alt.Chart(aggregate(df, "YEAR", measure)).mark_line(point=True).encode(
        x=alt.X("YEAR:O", title="Year", axis=alt.Axis(labelAngle=0)),
        y=alt.Y(f"{measure}:Q"),
        tooltip=["YEAR", alt.Tooltip(f"{measure}:Q", format=",.0f")],
    ).add_params(brush).properties(height=220, title=f"{measure} over Time (drag to filter years)")
    event = st.altair_chart(line, use_container_width=True, on_select="rerun", key="ex_line")

    years = event.selection.get("brush", {}).get("YEAR") if event else None
    if years:
        df = df[df["YEAR"].isin(years)]
        st.caption(f"Filtered to years: {', '.join(map(str, years))}")

    col1, col2, col3 = st.columns(3)

    with col1:
        dim_label = st.selectbox("Dimension", list(dimensions), key="ex_dim")
        dim = dimensions[dim_label]
        bars = aggregate(df, dim, measure).nlargest(15, measure)
        st.altair_chart(alt.Chart(bars).mark_bar(color=HIGHLIGHT).encode(
            x=alt.X(f"{measure}:Q"),
            y=alt.Y(f"{dim}:N", sort="-x", title=None,
                    axis=alt.Axis(labelOverlap=False, labelLimit=180)),
            tooltip=[dim, alt.Tooltip(f"{measure}:Q", format=",.0f")],
        ).properties(height=alt.Step(20), title=f"Top 15 by {dim_label}"),
            use_container_width=True)

    with col2:
        pts = aggregate(df.dropna(subset=["lat", "lng"]), ["CITY", "STATE", "lat", "lng"], measure)
        bg = alt.Chart(us_map).mark_geoshape(fill="#f2f2f2", stroke="white").project("albersUsa")
        dots = alt.Chart(pts).mark_circle(opacity=0.7).encode(
            longitude="lng:Q", latitude="lat:Q",
            size=alt.Size(f"{measure}:Q", scale=alt.Scale(range=[5, 400]), legend=None),
            color=alt.Color(f"{measure}:Q", scale=alt.Scale(scheme="blues"), legend=None),
            tooltip=["CITY", "STATE", alt.Tooltip(f"{measure}:Q", format=",.0f")],
        )
        st.altair_chart((bg + dots).properties(height=300, title="By City"),
                        use_container_width=True)

    with col3:
        sc = df.groupby(dim).agg(
            Petitions=(dim, "size"), MedianSalary=("PREVAILING_WAGE", "median")
        ).reset_index()
        st.altair_chart(alt.Chart(sc).mark_point(color=HIGHLIGHT).encode(
            x=alt.X("MedianSalary:Q", title="Median Salary", axis=alt.Axis(format="$,.0f"),
                    scale=alt.Scale(zero=False)),
            y=alt.Y("Petitions:Q"),
            tooltip=[dim, "Petitions", alt.Tooltip("MedianSalary:Q", format="$,.0f")],
        ).properties(height=300, title=f"Petitions vs. Median Salary by {dim_label}"),
            use_container_width=True)
