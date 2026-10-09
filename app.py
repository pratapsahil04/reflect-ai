import calendar
import html
import re
import textwrap
from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
from companion.llm import get_companion_response
from safety.classifier import classify_risk
from safety.responses import get_crisis_response
from safety.elevated import get_elevated_response
from mood.extractor import extract_mood
from database.db import (
    initialize_database,
    save_mood,
    get_mood_entries,
)
# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="ReflectAI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ============================================================
# THEME
# ============================================================
st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
    }
    .stApp {
        background: #050B1A;
        color: #E5E7EB;
    }
    [data-testid="stHeader"] {
        background: #050B1A;
    }
    [data-testid="stSidebar"] {
        background: #080F20;
        border-right: 1px solid #202A3B;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem;
    }
    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3 {
        color: #F8FAFC !important;
    }
    p, label, .stCaption {
        color: #A7B2C5;
    }
    [data-testid="stMetric"] {
        background: #080F20;
        border: 1px solid #202A3B;
        padding: 22px;
        border-radius: 13px;
        min-height: 120px;
    }
    [data-testid="stMetricLabel"] {
        color: #A7B2C5;
    }
    [data-testid="stMetricValue"] {
        color: #F8FAFC;
    }
    div[data-testid="stChatMessage"] {
        background: #0B1426;
        border: 1px solid #202A3B;
        border-radius: 14px;
        margin-bottom: 12px;
    }
    [data-testid="stChatInput"] {
        border: 1px solid #26364A;
        border-radius: 12px;
    }
    div.stButton > button {
        border-radius: 9px;
        border: 1px solid #26364A;
        transition: 0.2s;
    }
    div.stButton > button:hover {
        border-color: #2DD4BF;
        color: #2DD4BF;
    }
    .brand {
        color: #2DD4BF;
        font-size: 1.55rem;
        font-weight: 800;
        padding: 0.5rem 0 0.2rem 0;
    }
    .muted {
        color: #94A3B8;
        font-size: 0.9rem;
    }
    .insight-card {
        background: #071B25;
        border: 1px solid #155E63;
        border-radius: 14px;
        padding: 22px;
        margin: 12px 0 22px 0;
    }
    .insight-title {
        color: #5EEAD4;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .panel {
        background: #080F20;
        border: 1px solid #202A3B;
        border-radius: 13px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .section-label {
        color: #94A3B8;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    footer {
        visibility: hidden;
    }
    #MainMenu {
        visibility: hidden;
    }
    /* Sidebar navigation buttons */
    [data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        text-align: left;
        justify-content: flex-start;
        background: transparent;
        color: #A7B2C5;
        border: 0;
        border-left: 3px solid transparent;
        border-radius: 8px;
        padding: 0.55rem 0.65rem;
        margin: 2px 0;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background: #1E293B;
        color: #2DD4BF;
        border-color: #1E293B;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# ============================================================
# DATABASE
# ============================================================
initialize_database()
# ============================================================
# SESSION STATE
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Dashboard"
if "insight_feedback" not in st.session_state:
    st.session_state.insight_feedback = None
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "journal_draft" not in st.session_state:
    st.session_state.journal_draft = ""
# ============================================================
# NAVIGATION
# ============================================================
PAGES = [
    "Dashboard",
    "Journal Entries",
    "Search & Analysis",
    "Insights",
    "Analytics",
    "Tags & Categories",
    "Calendar View",
    "Templates",
    "Shared Journals",
    "Settings",
    "Help & Support",
]
ICONS = {
    "Dashboard": "▦",
    "Journal Entries": "▤",
    "Search & Analysis": "⌕",
    "Insights": "✦",
    "Analytics": "▥",
    "Tags & Categories": "◇",
    "Calendar View": "▦",
    "Templates": "▧",
    "Shared Journals": "♧",
    "Settings": "⚙",
    "Help & Support": "?",
}
with st.sidebar:
    st.markdown(
        '<div class="brand">🧠 ReflectAI</div>',
        unsafe_allow_html=True,
    )
    st.caption("YOUR PERSONAL REFLECTION SPACE")
    st.divider()
    st.markdown("**WORKSPACE**")
    for page in PAGES:
        is_selected = page == st.session_state.selected_page
        button_label = f"{ICONS[page]}  {page}"
        if st.button(
            button_label,
            key=f"navigation_{page}",
            use_container_width=True,
            type="primary" if is_selected else "secondary",
        ):
            st.session_state.selected_page = page
            st.rerun()
    selected_page = st.session_state.selected_page
    st.divider()
    st.markdown("**PRIVACY**")
    st.caption("🔒 Mood records are stored locally in SQLite.")
    st.caption("ReflectAI is not a medical or crisis-care service.")
# ============================================================
# DATA HELPERS
# ============================================================
@st.cache_data(ttl=5)
def load_mood_dataframe():
    rows = get_mood_entries()
    if not rows:
        return pd.DataFrame(
            columns=[
                "id",
                "timestamp",
                "mood_score",
                "primary_emotion",
                "secondary_emotions",
                "themes",
                "confidence",
            ]
        )
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
        df["timestamp"], errors="coerce"
    )
    df["mood_score"] = pd.to_numeric(
        df["mood_score"], errors="coerce"
    )
    df["confidence"] = pd.to_numeric(
        df["confidence"], errors="coerce"
    )
    df = df.dropna(subset=["timestamp", "mood_score"])
    return df.sort_values("timestamp")
def get_streak(df):
    if df.empty:
        return 0
    active_dates = set(
        df["timestamp"].dt.date.tolist()
    )
    latest = max(active_dates)
    streak = 0
    current = latest
    while current in active_dates:
        streak += 1
        current -= timedelta(days=1)
    return streak
def get_emotion_counts(df):
    if df.empty:
        return pd.DataFrame(
            columns=["emotion", "count"]
        )
    result = (
        df["primary_emotion"]
        .fillna("unspecified")
        .value_counts()
        .rename_axis("emotion")
        .reset_index(name="count")
    )
    return result
def get_theme_counts(df):
    themes = []
    if not df.empty:
        for value in df["themes"].dropna():
            for theme in str(value).split(","):
                theme = theme.strip()
                if theme:
                    themes.append(theme)
    if not themes:
        return pd.DataFrame(
            columns=["theme", "count"]
        )
    return (
        pd.Series(themes)
        .value_counts()
        .rename_axis("theme")
        .reset_index(name="count")
    )
def build_insight(df):
    if df.empty:
        return (
            "Your reflection journey starts here. "
            "Write an entry to begin exploring your mood patterns."
        )
    if len(df) < 2:
        return (
            "You've started recording your reflections. "
            "With more entries, you can begin exploring patterns "
            "across different days."
        )
    latest_time = df["timestamp"].max()
    recent = df[
        df["timestamp"] >= latest_time - pd.Timedelta(days=7)
    ]
    previous = df[
        (df["timestamp"] < latest_time - pd.Timedelta(days=7))
        & (
            df["timestamp"]
            >= latest_time - pd.Timedelta(days=14)
        )
    ]
    if recent.empty:
        return (
            "Keep writing when it feels useful. "
            "Your dashboard will summarize the entries you record."
        )
    recent_avg = recent["mood_score"].mean()
    if not previous.empty:
        previous_avg = previous["mood_score"].mean()
        change = recent_avg - previous_avg
        if change > 0.5:
            return (
                "Your average recorded mood is higher than in the "
                "previous seven-day period. Consider what, if anything, "
                "has been different in your recent experiences."
            )
        if change < -0.5:
            return (
                "Your average recorded mood is lower than in the "
                "previous seven-day period. You may want to reflect "
                "on what has been happening and what support could help."
            )
    top_emotion = (
        recent["primary_emotion"]
        .dropna()
        .mode()
    )
    if not top_emotion.empty:
        emotion_text = str(top_emotion.iloc[0])
        return (
            f"Your recorded mood scores have been relatively steady "
            f"compared with the available recent entries. "
            f"'{emotion_text}' appears frequently in your recent records. "
            "Does that fit how you have been experiencing your days?"
        )
    return (
        "Keep reflecting at your own pace. More entries can help "
        "you notice patterns over time."
    )
def chart_layout(fig, height=330):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#A7B2C5"),
        margin=dict(l=15, r=15, t=20, b=15),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#263247",
    )
    fig.update_yaxes(
        gridcolor="#1B2638",
        zeroline=False,
    )
    return fig
# ============================================================
# SHARED HEADER
# ============================================================
header_left, header_right = st.columns(
    [5, 2],
    vertical_alignment="center",
)
with header_left:
    st.markdown(
        '<div class="muted">REFLECTAI / YOUR PRIVATE SPACE</div>',
        unsafe_allow_html=True,
    )
with header_right:
    st.session_state.search_query = st.text_input(
        "Search journal records",
        value=st.session_state.search_query,
        placeholder="Search journal...",
        label_visibility="collapsed",
    )
df = load_mood_dataframe()
# ============================================================
# DASHBOARD
# ============================================================
if selected_page == "Dashboard":
    title_col, button_col = st.columns(
        [5, 1.2],
        vertical_alignment="center",
    )
    with title_col:
        st.title("Dashboard")
        st.caption(
            "Welcome back. Here's an overview of your "
            "journaling insights."
        )
    with button_col:
        if st.button(
            "＋ New Entry",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.selected_page = "Journal Entries"
            st.rerun()
    insight = build_insight(df)
    safe_insight = html.escape(insight)
    insight_html = (
        '<div class="insight-card">'
        '<div class="insight-title">✦ AI Insight</div>'
        f'<div style="color:#C3D0E0;line-height:1.7;">{safe_insight}</div>'
        '</div>'
    )
    st.markdown(insight_html, unsafe_allow_html=True)
    feedback_left, feedback_right, spacer = st.columns(
        [1.2, 1.5, 7]
    )
    with feedback_left:
        if st.button("👍 Helpful"):
            st.session_state.insight_feedback = "Helpful"
    with feedback_right:
        if st.button("👎 Not Helpful"):
            st.session_state.insight_feedback = "Not Helpful"
    if st.session_state.insight_feedback:
        st.caption(
            f"Feedback recorded for this session: "
            f"{st.session_state.insight_feedback}"
        )
    st.write("")
    total_entries = len(df)
    average_mood = (
        df["mood_score"].mean() if total_entries else None
    )
    streak = get_streak(df)
    previous_month = date.today().replace(day=1)
    last_month_end = previous_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    last_month_df = df[
        (df["timestamp"].dt.date >= last_month_start)
        & (df["timestamp"].dt.date <= last_month_end)
    ]
    month_df = df[
        (df["timestamp"].dt.date >= previous_month)
    ]
    if not df.empty:
        latest_date = df["timestamp"].max().date()
        if latest_date < date.today() - timedelta(days=1):
            streak_label = f"Latest entry: {latest_date}"
        else:
            streak_label = "Consecutive recorded days"
    else:
        streak_label = "Start your first reflection"
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Total Entries",
            total_entries,
            help="Number of saved mood-analysis records.",
        )
    with col2:
        st.metric(
            "Journaling Streak",
            f"{streak} days",
            help="Consecutive dates with recorded mood entries.",
        )
        st.caption(streak_label)
    with col3:
        st.metric(
            "Average Mood",
            f"{average_mood:.1f}/10"
            if average_mood is not None
            else "No data",
        )
        st.caption("Based on saved mood records")
    st.write("")
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("### Emotional Trends")
        st.caption("Your recorded mood scores over time")
        if not df.empty:
            fig = px.line(
                df,
                x="timestamp",
                y="mood_score",
                markers=True,
                labels={
                    "timestamp": "Date",
                    "mood_score": "Mood score",
                },
            )
            fig.update_yaxes(range=[1, 10], dtick=1)
            fig = chart_layout(fig)
            st.plotly_chart(
                fig,
                use_container_width=True,
            )
        else:
            st.info(
                "Your mood trend will appear after your first entry."
            )
    with right:
        st.markdown("### Common Topics")
        st.caption("Themes extracted from your journal entries")
        themes = get_theme_counts(df)
        if not themes.empty:
            fig = px.bar(
                themes.head(8).sort_values("count"),
                x="count",
                y="theme",
                orientation="h",
                labels={
                    "theme": "Theme",
                    "count": "Frequency",
                },
            )
            fig = chart_layout(fig)
            st.plotly_chart(
                fig,
                use_container_width=True,
            )
        else:
            st.info(
                "Common themes will appear as you record entries."
            )
    st.divider()
    st.markdown("### Recent Journal Activity")
    if df.empty:
        st.info(
            "No reflections have been recorded yet. "
            "Select **New Entry** to begin."
        )
    else:
        recent = df.head(5).copy()
        recent["timestamp"] = recent["timestamp"].dt.strftime(
            "%d %b %Y, %H:%M"
        )
        recent = recent[
            [
                "timestamp",
                "mood_score",
                "primary_emotion",
                "themes",
            ]
        ].rename(
            columns={
                "timestamp": "Date",
                "mood_score": "Mood",
                "primary_emotion": "Primary Emotion",
                "themes": "Common Themes",
            }
        )
        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True,
        )
    st.caption(
        "Mood summaries are approximate reflection aids, "
        "not clinical assessments."
    )
# ============================================================
# JOURNAL ENTRIES
# ============================================================
elif selected_page == "Journal Entries":
    st.title("Journal Entries")
    st.caption(
        "Write about your day, thoughts, or emotions. "
        "ReflectAI will help you explore them."
    )
    st.info(
        "Safety note: ReflectAI is an AI journaling companion, "
        "not a therapist or medical professional."
    )
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if not st.session_state.messages:
        with st.container(border=True):
            st.markdown("### 🌱 Start wherever you are")
            st.write(
                "There is no right way to journal. Write freely."
            )
    user_message = st.chat_input(
        "What's on your mind today?"
    )
    if user_message:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )
        with st.chat_message("user"):
            st.markdown(user_message)
        with st.chat_message("assistant"):
            try:
                risk_result = classify_risk(user_message)
                risk = risk_result.risk
                if risk == "crisis":
                    response = get_crisis_response("IN")
                    st.warning("Safety support information")
                    st.markdown(response)
                elif risk == "elevated":
                    response = get_elevated_response()
                    st.warning("Let's take this seriously.")
                    st.markdown(response)
                else:
                    with st.spinner("ReflectAI is reflecting..."):
                        response = get_companion_response(
                            user_message
                        )
                    st.markdown(response)
                    with st.spinner("Analyzing mood..."):
                        mood_result = extract_mood(
                            user_message
                        )
                    save_mood(
                        mood_score=mood_result.mood_score,
                        primary_emotion=mood_result.primary_emotion,
                        secondary_emotions=(
                            mood_result.secondary_emotions
                        ),
                        themes=mood_result.themes,
                        confidence=mood_result.confidence,
                    )
                    st.success(
                        f"Mood recorded: "
                        f"{mood_result.mood_score}/10 · "
                        f"{mood_result.primary_emotion}"
                    )
                    load_mood_dataframe.clear()
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )
            except Exception:
                st.error(
                    "Something went wrong while processing this entry. "
                    "Please try again."
                )
        st.rerun()
# ============================================================
# SEARCH AND ANALYSIS
# ============================================================
elif selected_page == "Search & Analysis":
    st.title("Search & Analysis")
    st.caption("Search saved mood records by emotion or theme.")
    query = st.text_input(
        "Search",
        value=st.session_state.search_query,
        placeholder="Try stress, work, happiness...",
    )
    if not df.empty and query.strip():
        searchable = df.copy()
        searchable["_search"] = (
            searchable["primary_emotion"].fillna("").astype(str)
            + " "
            + searchable["secondary_emotions"].fillna("").astype(str)
            + " "
            + searchable["themes"].fillna("").astype(str)
        )
        results = searchable[
            searchable["_search"].str.contains(
                re.escape(query.strip()),
                case=False,
                na=False,
            )
        ]
        st.write(f"Matching records: **{len(results)}**")
        st.dataframe(
            results[
                [
                    "timestamp",
                    "mood_score",
                    "primary_emotion",
                    "secondary_emotions",
                    "themes",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )
    elif df.empty:
        st.info("There are no saved mood records to search yet.")
    else:
        st.info("Enter a word to search your saved mood records.")
# ============================================================
# INSIGHTS
# ============================================================
elif selected_page == "Insights":
    st.title("Reflection Insights")
    st.caption(
        "Explore your emotional patterns and reflection history."
    )
    if df.empty:
        st.info("Write a journal entry to begin building insights.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Average Mood",
            f"{df['mood_score'].mean():.1f}/10",
        )
        col2.metric(
            "Highest Mood",
            f"{df['mood_score'].max():.0f}/10",
        )
        col3.metric(
            "Lowest Mood",
            f"{df['mood_score'].min():.0f}/10",
        )
        st.markdown("### Mood Over Time")
        fig = px.line(
            df,
            x="timestamp",
            y="mood_score",
            markers=True,
            labels={
                "timestamp": "Date",
                "mood_score": "Mood score",
            },
        )
        fig.update_yaxes(range=[1, 10], dtick=1)
        st.plotly_chart(
            chart_layout(fig, 400),
            use_container_width=True,
        )
        st.markdown("### Emotion Distribution")
        emotions = get_emotion_counts(df)
        if not emotions.empty:
            fig = px.bar(
                emotions,
                x="emotion",
                y="count",
                labels={
                    "emotion": "Emotion",
                    "count": "Frequency",
                },
            )
            st.plotly_chart(
                chart_layout(fig),
                use_container_width=True,
            )
        st.markdown("### Weekly Reflection")
        latest = df["timestamp"].max()
        weekly = df[
            df["timestamp"] >= latest - pd.Timedelta(days=7)
        ]
        if not weekly.empty:
            st.metric(
                "Recent Average Mood",
                f"{weekly['mood_score'].mean():.1f}/10",
            )
            st.write(f"Recorded entries: {len(weekly)}")
            emotion_mode = weekly["primary_emotion"].dropna().mode()
            if not emotion_mode.empty:
                st.write(
                    f"**Most frequent emotion:** {emotion_mode.iloc[0]}"
                )
            weekly_themes = get_theme_counts(weekly)
            if not weekly_themes.empty:
                st.write("**Common themes:**")
                st.write(
                    ", ".join(weekly_themes.head(5)["theme"].tolist())
                )
# ============================================================
# ANALYTICS
# ============================================================
elif selected_page == "Analytics":
    st.title("Analytics")
    st.caption("Detailed statistics from your saved mood records.")
    if df.empty:
        st.info("Analytics will appear after your first mood record.")
    else:
        min_date = df["timestamp"].min().date()
        max_date = df["timestamp"].max().date()
        start_date, end_date = st.date_input(
            "Choose a date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        ) if min_date != max_date else (min_date, max_date)
        filtered = df[
            (df["timestamp"].dt.date >= start_date)
            & (df["timestamp"].dt.date <= end_date)
        ]
        st.write(f"Records in selected range: **{len(filtered)}**")
        if not filtered.empty:
            col1, col2 = st.columns(2)
            col1.metric(
                "Average Mood",
                f"{filtered['mood_score'].mean():.1f}/10",
            )
            col2.metric(
                "Recorded Days",
                filtered["timestamp"].dt.date.nunique(),
            )
            fig = px.histogram(
                filtered,
                x="mood_score",
                nbins=10,
                labels={"mood_score": "Mood score"},
            )
            st.plotly_chart(
                chart_layout(fig),
                use_container_width=True,
            )
            csv_data = filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download filtered records (CSV)",
                data=csv_data,
                file_name="reflectai_mood_records.csv",
                mime="text/csv",
            )
# ============================================================
# TAGS AND CATEGORIES
# ============================================================
elif selected_page == "Tags & Categories":
    st.title("Tags & Categories")
    st.caption("Explore the themes extracted from your entries.")
    themes = get_theme_counts(df)
    if themes.empty:
        st.info("Themes will appear after you record journal entries.")
    else:
        st.dataframe(
            themes.rename(
                columns={
                    "theme": "Theme",
                    "count": "Occurrences",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
# ============================================================
# CALENDAR VIEW
# ============================================================
elif selected_page == "Calendar View":
    st.title("Calendar View")
    st.caption("See which dates have saved mood records.")
    today = date.today()
    selected_month = st.selectbox(
        "Month",
        list(range(1, 13)),
        index=today.month - 1,
        format_func=lambda month: calendar.month_name[month],
    )
    selected_year = st.selectbox(
        "Year",
        list(range(today.year - 5, today.year + 1)),
        index=5,
    )
    month_calendar = calendar.monthcalendar(
        selected_year,
        selected_month,
    )
    recorded_dates = set()
    if not df.empty:
        recorded_dates = {
            timestamp.date()
            for timestamp in df["timestamp"]
        }
    st.markdown(
        f"### {calendar.month_name[selected_month]} {selected_year}"
    )
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    for col, day_name in zip(cols, day_names):
        col.markdown(f"**{day_name}**")
    for week in month_calendar:
        cols = st.columns(7)
        for col, day_number in zip(cols, week):
            if day_number == 0:
                col.write(" ")
                continue
            current_date = date(
                selected_year,
                selected_month,
                day_number,
            )
            if current_date in recorded_dates:
                col.success(f"{day_number} ✓")
            else:
                col.write(str(day_number))
# ============================================================
# TEMPLATES
# ============================================================
elif selected_page == "Templates":
    st.title("Journal Templates")
    st.caption("Choose a prompt to help you begin writing.")
    templates = {
        "Daily reflection": (
            "What happened today? What went well, what was difficult, "
            "and what would I like to remember?"
        ),
        "Gratitude": (
            "What are three things I appreciate today, and why?"
        ),
        "Thought reflection": (
            "What situation is on my mind? What thoughts and feelings "
            "came up? What alternative perspective could I consider?"
        ),
        "Small wins": (
            "What small step or achievement am I proud of today?"
        ),
        "Tomorrow's intention": (
            "What matters most to me tomorrow, and what is one "
            "manageable step I can take?"
        ),
    }
    chosen_template = st.selectbox(
        "Select a template",
        list(templates.keys()),
    )
    st.text_area(
        "Template prompt",
        value=templates[chosen_template],
        height=140,
        disabled=True,
    )
    if st.button("Use this template", type="primary"):
        st.session_state.journal_draft = templates[chosen_template]
        st.session_state.selected_page = "Journal Entries"
        st.info(
            "Template selected. Copy its prompt into the journal "
            "input to begin your reflection."
        )
# ============================================================
# SHARED JOURNALS
# ============================================================
elif selected_page == "Shared Journals":
    st.title("Shared Journals")
    st.info(
        "Coming soon. This section will require an explicit sharing "
        "model, access controls, and privacy protections before "
        "journal data can be shared."
    )
# ============================================================
# SETTINGS
# ============================================================
elif selected_page == "Settings":
    st.title("Settings")
    st.caption("Review your local application configuration.")
    st.markdown("### Privacy")
    st.write(
        "Mood analysis records are stored in the local SQLite database."
    )
    st.write(
        "When you request a normal AI response or Gemini-based mood "
        "analysis, the relevant journal text is sent to Google's API."
    )
    st.markdown("### Crisis support")
    st.write(
        "The current crisis-response configuration uses India support "
        "resources. Review the helpline configuration before using "
        "the application in another country."
    )
    st.markdown("### Data management")
    st.warning(
        "Deleting local data is irreversible. Back up your database "
        "before making manual changes."
    )
    st.caption(
        "Writing-time tracking, account management, and cloud sync "
        "are not currently implemented."
    )
# ============================================================
# HELP AND SUPPORT
# ============================================================
elif selected_page == "Help & Support":
    st.title("Help & Support")
    st.markdown("### How to use ReflectAI")
    st.write(
        "1. Open Journal Entries and write about your day."
    )
    st.write(
        "2. Review the companion's response and approximate mood analysis."
    )
    st.write(
        "3. Use Insights and Analytics to explore saved mood records."
    )
    st.markdown("### Important limitations")
    st.write(
        "ReflectAI is not a therapist, medical professional, "
        "diagnostic tool, or emergency service."
    )
    st.write(
        "Its rule-based safety classifier cannot identify every "
        "possible crisis statement. If you are in immediate danger, "
        "contact local emergency services."
    )
    st.markdown("### Technical information")
    st.write("Interface: Streamlit")
    st.write("AI service: Google Gemini API")
    st.write("Local database: SQLite")
# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(
    "ReflectAI · AI-powered journaling and reflection · "
    "Mood records stored locally in SQLite · "
    "Not a substitute for professional care"
)
