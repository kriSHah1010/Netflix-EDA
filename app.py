import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Streaming Content Insights",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_CANDIDATES = [
    Path("data/processed/netflix_clean.csv"),
    Path("data/raw/netflix_titles.csv"),
]


def load_data() -> pd.DataFrame:
    for path in DATA_CANDIDATES:
        if path.exists():
            df = pd.read_csv(path)
            return prepare_data(df)
    return pd.DataFrame()


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "date_added" in df.columns:
        df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
        df["year_added"] = df["date_added"].dt.year
        df["month_added"] = df["date_added"].dt.month_name()

    if "duration" in df.columns:
        duration_split = df["duration"].astype(str).str.extract(r"(?P<duration_value>\d+)\s*(?P<duration_unit>\w+)")
        df["duration_value"] = pd.to_numeric(duration_split["duration_value"], errors="coerce")
        df["duration_unit"] = duration_split["duration_unit"].str.lower()

    for col in ["country", "listed_in", "cast", "director"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    return df


def normalize_multivalue(series: pd.Series) -> pd.Series:
    return series.fillna("Unknown").astype(str).str.split(",")


@st.cache_data
def get_filtered_data(df: pd.DataFrame, content_types, year_range, selected_countries, selected_ratings):
    filtered = df.copy()

    if content_types and "type" in filtered.columns:
        filtered = filtered[filtered["type"].isin(content_types)]
    if "release_year" in filtered.columns:
        filtered = filtered[filtered["release_year"].between(year_range[0], year_range[1])]
    if selected_countries and "country" in filtered.columns:
        pattern = "|".join(re.escape(country) for country in selected_countries)
        filtered = filtered[filtered["country"].astype(str).str.contains(pattern, case=False, na=False)]
    if selected_ratings and "rating" in filtered.columns:
        filtered = filtered[filtered["rating"].isin(selected_ratings)]

    return filtered


def main():
    st.title("Streaming Content Insights")
    st.caption("An interactive exploratory dashboard built from the Netflix titles dataset.")

    df = load_data()

    if df.empty:
        st.error("No dataset found. Add `data/raw/netflix_titles.csv` or `data/processed/netflix_clean.csv`.")
        st.stop()

    with st.sidebar:
        st.header("Filters")
        content_types = st.multiselect(
            "Content type",
            sorted([x for x in df.get("type", pd.Series(dtype=str)).dropna().unique().tolist()]),
            default=sorted([x for x in df.get("type", pd.Series(dtype=str)).dropna().unique().tolist()]),
        )

        min_year = int(df["release_year"].min()) if "release_year" in df.columns and df["release_year"].notna().any() else 1900
        max_year = int(df["release_year"].max()) if "release_year" in df.columns and df["release_year"].notna().any() else 2025
        year_range = st.slider("Release year", min_year, max_year, (min_year, max_year))

        country_options = []
        if "country" in df.columns:
            countries = (
                df["country"].fillna("Unknown").astype(str).str.split(",").explode().str.strip().replace("", "Unknown")
            )
            country_options = sorted(countries.dropna().unique().tolist())
        selected_countries = st.multiselect("Country contains", country_options[:50], default=[])

        rating_options = []
        if "rating" in df.columns:
            rating_options = sorted(df["rating"].dropna().astype(str).unique().tolist())
        selected_ratings = st.multiselect("Rating", rating_options, default=[])

    filtered = get_filtered_data(df, content_types, year_range, selected_countries, selected_ratings)

    total_titles = len(filtered)
    movies = int((filtered["type"] == "Movie").sum()) if "type" in filtered.columns else 0
    tv_shows = int((filtered["type"] == "TV Show").sum()) if "type" in filtered.columns else 0
    unique_countries = int(filtered["country"].nunique()) if "country" in filtered.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Titles", f"{total_titles:,}")
    col2.metric("Movies", f"{movies:,}")
    col3.metric("TV Shows", f"{tv_shows:,}")
    col4.metric("Countries", f"{unique_countries:,}")

    st.divider()

    left, right = st.columns((1.2, 1))

    with left:
        if "type" in filtered.columns:
            fig = px.histogram(filtered, x="type", color="type", text_auto=True, title="Content split")
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

    with right:
        if "release_year" in filtered.columns:
            yearly = filtered.groupby("release_year", dropna=True).size().reset_index(name="count")
            fig = px.line(yearly, x="release_year", y="count", markers=True, title="Titles by release year")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        if "listed_in" in filtered.columns:
            genres = filtered["listed_in"].fillna("Unknown").astype(str).str.split(",").explode().str.strip()
            top_genres = genres.value_counts().head(10).reset_index()
            top_genres.columns = ["genre", "count"]
            fig = px.bar(top_genres, x="count", y="genre", orientation="h", title="Top genres")
            fig.update_layout(height=450, yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

    with col6:
        if "rating" in filtered.columns:
            rating_counts = filtered["rating"].fillna("Unknown").value_counts().head(10).reset_index()
            rating_counts.columns = ["rating", "count"]
            fig = px.pie(rating_counts, names="rating", values="count", title="Ratings")
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Filtered dataset preview")
    st.dataframe(filtered.head(50), use_container_width=True)

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name="filtered_netflix_titles.csv",
        mime="text/csv",
    )

    st.markdown(
        "---\n"
        "### Suggested portfolio talking points\n"
        "- Built a reusable cleaning pipeline and dashboard around public streaming content data.\n"
        "- Explored content mix, release trends, genre concentration, and rating distribution.\n"
        "- Designed the app for stakeholder-style filtering and fast exploration."
    )


if __name__ == "__main__":
    main()
