import pandas as pd
import plotly.express as px
import streamlit as st

from database.db import get_mood_entries
from dashboard.weekly import show_weekly_summary


# ============================================================
# LOAD MOOD DATA
# ============================================================

def get_mood_dataframe():

    rows = get_mood_entries()

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(
        rows,
        columns=[
            "id",
            "timestamp",
            "mood_score",
            "primary_emotion",
            "secondary_emotions",
            "themes",
            "confidence",
        ],
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    df = df.sort_values(
        "timestamp"
    )

    return df


# ============================================================
# SUMMARY METRICS
# ============================================================

def show_summary_metrics(df):

    average_mood = df["mood_score"].mean()
    highest_mood = df["mood_score"].max()
    lowest_mood = df["mood_score"].min()
    total_entries = len(df)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Average Mood",
            f"{average_mood:.1f}/10"
        )

    with col2:
        st.metric(
            "Highest",
            f"{highest_mood}/10"
        )

    with col3:
        st.metric(
            "Lowest",
            f"{lowest_mood}/10"
        )

    with col4:
        st.metric(
            "Entries",
            total_entries
        )


# ============================================================
# MOOD TREND
# ============================================================

def show_mood_trend(df):

    st.subheader("📈 Mood Over Time")

    fig = px.line(
        df,
        x="timestamp",
        y="mood_score",
        markers=True,
        labels={
            "timestamp": "Date",
            "mood_score": "Mood Score",
        },
    )

    fig.update_yaxes(
        range=[1, 10],
        dtick=1,
    )

    fig.update_layout(
        height=400,
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#cbd5e1"
        ),
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# EMOTION DISTRIBUTION
# ============================================================

def show_emotion_distribution(df):

    st.subheader("😊 Emotions")

    emotion_counts = (
        df["primary_emotion"]
        .value_counts()
        .reset_index()
    )

    emotion_counts.columns = [
        "emotion",
        "count",
    ]

    fig = px.bar(
        emotion_counts,
        x="emotion",
        y="count",
        labels={
            "emotion": "Emotion",
            "count": "Frequency",
        },
    )

    fig.update_layout(
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#cbd5e1"
        ),
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# THEME DISTRIBUTION
# ============================================================

def show_theme_distribution(df):

    st.subheader("🏷️ Common Themes")

    theme_list = []

    for themes in df["themes"].dropna():

        for theme in str(themes).split(","):

            theme = theme.strip()

            if theme:
                theme_list.append(theme)

    if not theme_list:

        st.info(
            "No themes available yet."
        )

        return

    theme_counts = (
        pd.Series(theme_list)
        .value_counts()
        .reset_index()
    )

    theme_counts.columns = [
        "theme",
        "count",
    ]

    fig = px.bar(
        theme_counts,
        x="theme",
        y="count",
        labels={
            "theme": "Theme",
            "count": "Frequency",
        },
    )

    fig.update_layout(
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#cbd5e1"
        ),
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# SEVEN DAY AVERAGE
# ============================================================

def show_seven_day_average(df):

    st.subheader("📅 Recent Mood")

    latest_date = df["timestamp"].max()

    seven_days_ago = (
        latest_date -
        pd.Timedelta(days=7)
    )

    recent_df = df[
        df["timestamp"] >= seven_days_ago
    ]

    if recent_df.empty:

        st.info(
            "Not enough recent data."
        )

        return

    recent_average = (
        recent_df["mood_score"].mean()
    )

    st.metric(
        "7-Day Average Mood",
        f"{recent_average:.1f}/10"
    )

    st.caption(
        f"Based on {len(recent_df)} "
        "journal entries from the last 7 days."
    )


# ============================================================
# RECENT ENTRIES
# ============================================================

def show_recent_entries(df):

    st.subheader("📝 Recent Entries")

    display_df = df[
        [
            "timestamp",
            "mood_score",
            "primary_emotion",
            "secondary_emotions",
            "themes",
            "confidence",
        ]
    ].copy()

    display_df = display_df.sort_values(
        "timestamp",
        ascending=False,
    )

    display_df["timestamp"] = (
        display_df["timestamp"]
        .dt.strftime("%Y-%m-%d %H:%M")
    )

    display_df["confidence"] = (
        display_df["confidence"]
        .round(2)
    )

    display_df = display_df.rename(
        columns={
            "timestamp": "Date",
            "mood_score": "Mood",
            "primary_emotion": "Primary Emotion",
            "secondary_emotions": "Other Emotions",
            "themes": "Themes",
            "confidence": "Confidence",
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# MAIN DASHBOARD
# ============================================================

def show_dashboard():

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.title("Reflection Insights 📊")

    st.caption(
        "Understand your mood patterns and reflection history "
        "over time."
    )

    st.divider()

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    df = get_mood_dataframe()

    if df.empty:

        st.info(
            "📭 No reflections yet. "
            "Write a few journal entries to start "
            "building your reflection history."
        )

        return

    # --------------------------------------------------------
    # WEEKLY REFLECTION
    # --------------------------------------------------------

    show_weekly_summary(df)

    st.divider()

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    st.subheader("📌 Mood Summary")

    show_summary_metrics(df)

    st.divider()

    # --------------------------------------------------------
    # MOOD TREND
    # --------------------------------------------------------

    show_mood_trend(df)

    st.divider()

    # --------------------------------------------------------
    # EMOTIONS + THEMES
    # --------------------------------------------------------

    left_column, right_column = st.columns(2)

    with left_column:

        show_emotion_distribution(df)

    with right_column:

        show_theme_distribution(df)

    st.divider()

    # --------------------------------------------------------
    # RECENT MOOD
    # --------------------------------------------------------

    show_seven_day_average(df)

    st.divider()

    # --------------------------------------------------------
    # RECENT ENTRIES
    # --------------------------------------------------------

    show_recent_entries(df)