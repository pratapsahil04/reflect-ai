import streamlit as st

from companion.llm import get_companion_response

from safety.classifier import classify_risk
from safety.responses import get_crisis_response
from safety.elevated import get_elevated_response

from mood.extractor import extract_mood

from database.db import (
    initialize_database,
    save_mood,
)

from dashboard.dashboard import show_dashboard


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ReflectAI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    .stApp {
        background-color: #0b1020;
    }

    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }


    /* ======================================================
       CHAT MESSAGES
       ====================================================== */

    [data-testid="stChatMessage"] {
        border-radius: 16px;
        border: 1px solid #263244;
        margin-bottom: 10px;
    }


    /* ======================================================
       CHAT INPUT
       ====================================================== */

    [data-testid="stChatInput"] {
        border-radius: 16px;
    }


    /* ======================================================
       TABS
       ====================================================== */

    button[data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 600;
    }


    /* ======================================================
       MOOD CARD
       ====================================================== */

    .mood-card {
        background-color: #111827;
        border: 1px solid #263244;
        border-radius: 14px;
        padding: 12px 16px;
        margin-top: 12px;
    }

    .mood-label {
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 1px;
    }

    .mood-score {
        color: white;
        font-size: 1.2rem;
        font-weight: 700;
    }

    .mood-emotion {
        color: #5eead4;
        font-size: 1rem;
        margin-left: 8px;
    }


    /* ======================================================
       FOOTER
       ====================================================== */

    .footer-text {
        color: #64748b;
        font-size: 0.8rem;
        text-align: center;
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
# HEADER
# ============================================================

st.title("ReflectAI 🧠")

st.caption(
    "A quiet space to write, reflect, and understand "
    "the patterns behind your thoughts and emotions."
)


# ============================================================
# PRIVACY AND SAFETY NOTICE
# ============================================================

st.info(
    "🔒 **Privacy & safety:** ReflectAI is an AI journaling "
    "companion, not a therapist or medical professional. "
    "It does not diagnose conditions or provide medical treatment."
)


# ============================================================
# TABS
# ============================================================

journal_tab, insights_tab = st.tabs(
    [
        "💬 Journal",
        "📊 Insights",
    ]
)


# ============================================================
# JOURNAL TAB
# ============================================================

with journal_tab:

    st.header("What's on your mind?")

    st.caption(
        "Write freely. ReflectAI will help you explore "
        "your thoughts without judgment."
    )


    # ========================================================
    # SESSION STATE
    # ========================================================

    if "messages" not in st.session_state:

        st.session_state.messages = []


    # ========================================================
    # DISPLAY CHAT HISTORY
    # ========================================================

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(
                message["content"]
            )


    # ========================================================
    # EMPTY STATE
    # ========================================================

    if not st.session_state.messages:

        st.info(
            "🌱 **Start with whatever is on your mind.**\n\n"
            "There is no right way to journal."
        )


    # ========================================================
    # CHAT INPUT
    # ========================================================

    user_message = st.chat_input(
        "Write about your day, your thoughts, or how you're feeling..."
    )


    # ========================================================
    # PROCESS USER MESSAGE
    # ========================================================

    if user_message:

        # ----------------------------------------------------
        # SAVE USER MESSAGE
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )


        # ----------------------------------------------------
        # DISPLAY USER MESSAGE
        # ----------------------------------------------------

        with st.chat_message("user"):

            st.markdown(
                user_message
            )


        # ----------------------------------------------------
        # ASSISTANT RESPONSE
        # ----------------------------------------------------

        with st.chat_message("assistant"):

            try:

                # ============================================
                # SAFETY CHECK
                # ============================================

                with st.spinner(
                    "Checking safety..."
                ):

                    risk_result = classify_risk(
                        user_message
                    )

                    risk = risk_result.risk


                # ============================================
                # CRISIS
                # ============================================

                if risk == "crisis":

                    response = get_crisis_response(
                        "IN"
                    )

                    st.warning(
                        "🚨 Safety support information"
                    )

                    st.markdown(
                        response
                    )


                # ============================================
                # ELEVATED RISK
                # ============================================

                elif risk == "elevated":

                    response = get_elevated_response()

                    st.warning(
                        "⚠️ Let's take this seriously."
                    )

                    st.markdown(
                        response
                    )


                # ============================================
                # NORMAL MESSAGE
                # ============================================

                else:

                    # ----------------------------------------
                    # COMPANION RESPONSE
                    # ----------------------------------------

                    with st.spinner(
                        "Reflecting on your entry..."
                    ):

                        response = get_companion_response(
                            user_message
                        )


                    st.markdown(
                        response
                    )


                    # ----------------------------------------
                    # MOOD EXTRACTION
                    # ----------------------------------------

                    with st.spinner(
                        "Understanding your mood..."
                    ):

                        mood_result = extract_mood(
                            user_message
                        )


                    # ----------------------------------------
                    # SAVE MOOD
                    # ----------------------------------------

                    save_mood(
                        mood_score=mood_result.mood_score,
                        primary_emotion=mood_result.primary_emotion,
                        secondary_emotions=(
                            mood_result.secondary_emotions
                        ),
                        themes=mood_result.themes,
                        confidence=mood_result.confidence,
                    )


                    # ----------------------------------------
                    # MOOD RESULT
                    # ----------------------------------------

                    st.success(
                        f"🌿 Mood detected: "
                        f"{mood_result.mood_score}/10 • "
                        f"{mood_result.primary_emotion}"
                    )


                # =================================================
                # SAVE ASSISTANT RESPONSE
                # =================================================

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )


            except Exception as e:

                st.error(
                    f"Something went wrong: {str(e)}"
                )


# ============================================================
# INSIGHTS TAB
# ============================================================

with insights_tab:

    show_dashboard()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "ReflectAI • AI-powered journaling and reflection • "
    "Mood data is stored locally in SQLite."
)