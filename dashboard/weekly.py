from collections import Counter

import pandas as pd


def generate_weekly_summary(df: pd.DataFrame) -> dict:

    if df.empty:
        return {
            "entries": 0,
            "average_mood": None,
            "mood_change": None,
            "trend": "No data",
            "top_emotion": None,
            "top_themes": [],
        }

    # Make sure timestamps are datetime
    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    # ------------------------------------------------
    # LAST 7 DAYS
    # ------------------------------------------------

    latest_date = df["timestamp"].max()

    seven_days_ago = (
        latest_date - pd.Timedelta(days=7)
    )

    weekly_df = df[
        df["timestamp"] >= seven_days_ago
    ].copy()

    if weekly_df.empty:
        return {
            "entries": 0,
            "average_mood": None,
            "mood_change": None,
            "trend": "No data",
            "top_emotion": None,
            "top_themes": [],
        }

    # ------------------------------------------------
    # AVERAGE MOOD
    # ------------------------------------------------

    average_mood = weekly_df[
        "mood_score"
    ].mean()

    # ------------------------------------------------
    # MOOD CHANGE
    # ------------------------------------------------

    weekly_df = weekly_df.sort_values(
        "timestamp"
    )

    first_mood = weekly_df.iloc[0]["mood_score"]

    last_mood = weekly_df.iloc[-1]["mood_score"]

    mood_change = last_mood - first_mood

    # ------------------------------------------------
    # TREND
    # ------------------------------------------------

    if mood_change > 0.5:

        trend = "Improving"

    elif mood_change < -0.5:

        trend = "Declining"

    else:

        trend = "Stable"

    # ------------------------------------------------
    # MOST FREQUENT EMOTION
    # ------------------------------------------------

    emotions = (
        weekly_df["primary_emotion"]
        .dropna()
        .astype(str)
        .tolist()
    )

    if emotions:

        top_emotion = Counter(
            emotions
        ).most_common(1)[0][0]

    else:

        top_emotion = "Not enough data"

    # ------------------------------------------------
    # MOST COMMON THEMES
    # ------------------------------------------------

    themes = []

    for theme_string in weekly_df[
        "themes"
    ].dropna():

        for theme in str(
            theme_string
        ).split(","):

            theme = theme.strip()

            if theme:

                themes.append(theme)

    top_themes = [
        theme
        for theme, count in Counter(
            themes
        ).most_common(5)
    ]

    return {
        "entries": len(weekly_df),
        "average_mood": round(
            average_mood,
            1
        ),
        "mood_change": round(
            mood_change,
            1
        ),
        "trend": trend,
        "top_emotion": top_emotion,
        "top_themes": top_themes,
    }


def show_weekly_summary(df: pd.DataFrame):

    import streamlit as st

    st.subheader(
        "📅 Weekly Reflection"
    )

    summary = generate_weekly_summary(
        df
    )

    if summary["entries"] == 0:

        st.info(
            "Not enough data for a weekly reflection yet."
        )

        return

    # ------------------------------------------------
    # SUMMARY METRICS
    # ------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Weekly Average Mood",
        f"{summary['average_mood']}/10"
    )

    col2.metric(
        "Mood Change",
        f"{summary['mood_change']:+.1f}"
    )

    col3.metric(
        "Entries",
        summary["entries"]
    )

    # ------------------------------------------------
    # TREND
    # ------------------------------------------------

    if summary["trend"] == "Improving":

        st.success(
            "📈 Your mood trend appears to be improving."
        )

    elif summary["trend"] == "Declining":

        st.warning(
            "📉 Your mood trend appears to be declining."
        )

    else:

        st.info(
            "➡️ Your mood trend appears relatively stable."
        )

    # ------------------------------------------------
    # TOP EMOTION
    # ------------------------------------------------

    st.write(
        f"**Most frequent emotion:** "
        f"{summary['top_emotion']}"
    )

    # ------------------------------------------------
    # TOP THEMES
    # ------------------------------------------------

    if summary["top_themes"]:

        st.write(
            "**Common themes:**"
        )

        for theme in summary["top_themes"]:

            st.write(
                f"• {theme}"
            )