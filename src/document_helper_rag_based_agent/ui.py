from typing import Dict, Any, List
from pathlib import Path

import streamlit as st

from document_helper_rag_based_agent.backend.core import run_llm


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "r3f-logo.png"


# ============================================================
# Helper Functions
# ============================================================

def _format_sources(context_docs: List[Any]) -> List[str]:
    return [
        doc.metadata.get("source", "Unknown")
        for doc in (context_docs or [])
        if getattr(doc, "metadata", None)
    ]


def _bubble_class(role: str) -> str:
    return "assistant-bubble" if role == "assistant" else "user-bubble"


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="R3F Documentation Helper",
    page_icon=str(LOGO_PATH),
    layout="centered",
)


# ============================================================
# Global Styling
# ============================================================

st.html(
    """
    <style>

    /* ========================================================
       COLOR PALETTE
       ======================================================== */

    :root {
        --bg-dark: #0c0121;
        --bg-dark-2: #13052f;
        --bg-dark-3: #1b0a3d;
        --bg-dark-4: #24104d;
        --bg-darkest: #05000d;

        --light-purple: #f5e4f7;
        --soft-purple: #ead3ee;

        --accent: #c9a7ff;
        --accent-2: #9d7bea;
        --accent-ai: #b9a3ff;
        --accent-user: #e29cf0;

        --text-main: #f5eaff;
        --text-muted: #b9a9ca;
    }


    /* ========================================================
       STREAMLIT APP BACKGROUND
       ======================================================== */

    html,
    body,
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(
            180deg,
            var(--bg-dark) 0%,
            var(--bg-darkest) 100%
        ) !important;
        background-attachment: fixed !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        background: transparent !important;
    }

    [data-testid="stMainBlockContainer"] {
        background: transparent !important;
    }


    /* ========================================================
       STREAMLIT TOP HEADER
       ======================================================== */

    [data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }

    [data-testid="stToolbar"] {
        background: transparent !important;
    }


    /* ========================================================
       STREAMLIT BOTTOM AREA
       ======================================================== */

    [data-testid="stBottom"] {
        background: transparent !important;
        box-shadow: none !important;
    }

    [data-testid="stBottom"] > div {
        background: transparent !important;
    }

    [data-testid="stBottomBlockContainer"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    footer {
        visibility: hidden;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background: var(--bg-dark-2) !important;
        border-right: 1px solid rgba(201, 167, 255, 0.12);
    }

    [data-testid="stSidebar"] > div {
        background: var(--bg-dark-2) !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: var(--text-main) !important;
    }


    /* ========================================================
       SIDEBAR SECTIONS
       ======================================================== */

    .sidebar-title {
        color: var(--text-main);

        font-size: 15px;
        font-weight: 700;

        margin-top: 8px;
        margin-bottom: 8px;
    }


    .sidebar-description {
        color: var(--text-muted);

        font-size: 13px;

        line-height: 1.6;

        margin-bottom: 18px;
    }


    .stack-item {
        display: flex;
        align-items: center;

        gap: 9px;

        padding: 8px 10px;

        margin: 5px 0;

        background: var(--bg-dark-3);

        border: 1px solid rgba(201, 167, 255, 0.10);

        border-radius: 9px;

        color: var(--soft-purple);

        font-size: 13px;
    }


    .stack-icon {
        color: var(--accent);

        font-size: 14px;
    }


    /* ========================================================
       SIDEBAR BUTTON
       ======================================================== */

    [data-testid="stSidebar"] button {
        background: var(--bg-dark-3) !important;

        color: var(--text-main) !important;

        border: 1px solid rgba(201, 167, 255, 0.15) !important;

        border-radius: 10px !important;
    }

    [data-testid="stSidebar"] button:hover {
        border-color: rgba(201, 167, 255, 0.4) !important;

        background: var(--bg-dark-4) !important;
    }


    /* ========================================================
       MAIN HEADER
       ======================================================== */

    .r3f-header {
        display: flex;
        align-items: center;

        gap: 16px;

        padding: 22px 24px;

        margin-bottom: 24px;

        background: linear-gradient(
            135deg,
            var(--bg-dark-2),
            var(--bg-dark-3)
        );

        border: 1px solid rgba(201, 167, 255, 0.16);

        border-radius: 18px;

        box-shadow:
            0 8px 30px rgba(0, 0, 0, 0.25);
    }


    .r3f-logo {
        width: 52px;
        height: 52px;

        display: flex;
        align-items: center;
        justify-content: center;

        border-radius: 14px;

        background: var(--bg-dark-4);

        border: 1px solid rgba(201, 167, 255, 0.25);

        color: var(--accent);

        font-size: 27px;
        font-weight: 700;

        box-shadow:
            0 0 25px rgba(157, 123, 234, 0.18);
    }


    .r3f-title {
        font-size: 25px;
        font-weight: 700;

        color: var(--text-main);

        line-height: 1.2;
    }


    .r3f-subtitle {
        margin-top: 5px;

        font-size: 14px;

        color: var(--text-muted);
    }


    /* ========================================================
       RETRIEVAL STATUS
       ======================================================== */

    .retrieval-status {
        display: flex;
        align-items: center;

        width: 100%;

        min-height: 38px;

        margin: 2px 0 12px 0;

        color: var(--text-muted);

        font-size: 13px;

        white-space: nowrap;
    }


    /* --------------------------------------------------------
       Retrieval text
       -------------------------------------------------------- */

    .retrieval-text {
        display: inline-block;

        flex-shrink: 0;
    }


    /* --------------------------------------------------------
       Animated dots
       -------------------------------------------------------- */

    .retrieval-dots {
        display: inline-flex;

        width: 30px;

        margin-left: 3px;

        margin-right: 8px;

        align-items: center;
    }


    .retrieval-dots span {
        display: inline-block;

        width: 3px;
        height: 3px;

        margin: 0 2px;

        border-radius: 50%;

        background: var(--accent);

        opacity: 0.25;

        animation: retrieval-dot-animation 1.4s infinite ease-in-out;
    }


    .retrieval-dots span:nth-child(1) {
        animation-delay: 0s;
    }


    .retrieval-dots span:nth-child(2) {
        animation-delay: 0.18s;
    }


    .retrieval-dots span:nth-child(3) {
        animation-delay: 0.36s;
    }


    @keyframes retrieval-dot-animation {

        0%,
        60%,
        100% {
            opacity: 0.2;

            transform: scale(0.75);
        }

        30% {
            opacity: 1;

            transform: scale(1.15);
        }
    }


    /* --------------------------------------------------------
       Cat movement area
       -------------------------------------------------------- */

    .retrieval-cat-track {
        position: relative;

        flex: 1;

        height: 34px;

        min-width: 70px;

        overflow: hidden;
    }


    /*
       Mouse
       -----
       The mouse leads the chase. It travels the FULL width
       of the track, right -> left, and is always positioned
       further left (closer to escaping) than the cat at
       every point in the loop.
    */

    .retrieval-mouse {
        position: absolute;

        left: 0;

        top: 8px;

        display: inline-block;

        font-size: 14px;

        line-height: 1;

        z-index: 2;

        filter:
            drop-shadow(
                0 0 5px rgba(201, 167, 255, 0.35)
            );

        animation:
            mouse-run
            6.5s
            linear
            infinite;
    }


    /*
       Cat
       ---
       The cat chases from behind. It shares the SAME loop
       duration as the mouse (so the two never drift out of
       sync/invert), but covers a smaller percentage of the
       track in that time - making it genuinely slower and
       causing the gap to widen naturally over each lap
       before the loop resets.
    */

    .retrieval-cat {
        position: absolute;

        left: calc(100% - 2px);

        top: 2px;

        display: inline-block;

        font-size: 26px;

        line-height: 1;

        z-index: 1;

        filter:
            drop-shadow(
                0 0 6px rgba(201, 167, 255, 0.45)
            );

        transform-origin: center bottom;

        animation:
            cat-chase
            6.5s
            linear
            infinite;
    }


    /*
       Mouse movement:
       RIGHT -> LEFT, full track width.

       left(k) = (100 - k)% - 18px
       (18px is subtracted at every step so the mouse always
       sits 18px+ ahead of the cat's own margin - see cat-chase)
    */

    @keyframes mouse-run {

        0% {
            left: calc(100% - 18px);
            transform: translateY(0px) rotate(0deg);
        }

        10% {
            left: calc(90% - 18px);
            transform: translateY(-1px) rotate(-2deg);
        }

        20% {
            left: calc(80% - 18px);
            transform: translateY(0px) rotate(0deg);
        }

        30% {
            left: calc(70% - 18px);
            transform: translateY(-1px) rotate(-2deg);
        }

        40% {
            left: calc(60% - 18px);
            transform: translateY(0px) rotate(0deg);
        }

        50% {
            left: calc(50% - 18px);
            transform: translateY(-1px) rotate(-2deg);
        }

        60% {
            left: calc(40% - 18px);
            transform: translateY(0px) rotate(0deg);
        }

        70% {
            left: calc(30% - 18px);
            transform: translateY(-1px) rotate(-2deg);
        }

        80% {
            left: calc(20% - 18px);
            transform: translateY(0px) rotate(0deg);
        }

        90% {
            left: calc(10% - 18px);
            transform: translateY(-1px) rotate(-2deg);
        }

        100% {
            left: calc(0% - 18px);
            transform: translateY(0px) rotate(0deg);
        }
    }


    /*
       Cat movement:
       RIGHT -> LEFT, but only 62% of the track width in the
       SAME 6.5s duration as the mouse - genuinely slower,
       never overtakes, and always trails to the right of
       the mouse.

       left(k) = (100 - 0.62*k)% - 2px
    */

    @keyframes cat-chase {

        0% {
            left: calc(100% - 2px);
            transform: translateY(0px) rotate(4deg);
        }

        10% {
            left: calc(93.8% - 2px);
            transform: translateY(-2px) rotate(-3deg);
        }

        20% {
            left: calc(87.6% - 2px);
            transform: translateY(0px) rotate(4deg);
        }

        30% {
            left: calc(81.4% - 2px);
            transform: translateY(-2px) rotate(-3deg);
        }

        40% {
            left: calc(75.2% - 2px);
            transform: translateY(0px) rotate(4deg);
        }

        50% {
            left: calc(69% - 2px);
            transform: translateY(-2px) rotate(-3deg);
        }

        60% {
            left: calc(62.8% - 2px);
            transform: translateY(0px) rotate(4deg);
        }

        70% {
            left: calc(56.6% - 2px);
            transform: translateY(-2px) rotate(-3deg);
        }

        80% {
            left: calc(50.4% - 2px);
            transform: translateY(0px) rotate(4deg);
        }

        90% {
            left: calc(44.2% - 2px);
            transform: translateY(-2px) rotate(-3deg);
        }

        100% {
            left: calc(38% - 2px);
            transform: translateY(0px) rotate(4deg);
        }
    }


    /* ========================================================
       CHAT MESSAGES
       ======================================================== */

    [data-testid="stChatMessage"] {
        background: transparent !important;
    }

    [data-testid="stChatMessage"] p {
        color: var(--text-main);
    }


    /* ========================================================
       CHAT BUBBLES
       ======================================================== */

    .assistant-bubble {
        background: linear-gradient(
            135deg,
            #170a35,
            #1f0f47
        );

        border: 1px solid rgba(185, 163, 255, 0.20);
        border-left: 3px solid var(--accent-ai);

        border-radius: 4px 16px 16px 16px;

        padding: 15px 18px;

        margin: 4px 0 14px 0;

        box-shadow:
            0 5px 18px rgba(0, 0, 0, 0.22);
    }

    .assistant-bubble p:last-child {
        margin-bottom: 0;
    }


    .user-bubble {
        background: linear-gradient(
            135deg,
            #2b0f3f,
            #3a1250
        );

        border: 1px solid rgba(226, 156, 240, 0.22);
        border-left: 3px solid var(--accent-user);

        border-radius: 4px 16px 16px 16px;

        padding: 15px 18px;

        margin: 4px 0 14px 0;

        box-shadow:
            0 5px 18px rgba(0, 0, 0, 0.26);
    }

    .user-bubble p:last-child {
        margin-bottom: 0;
    }


    /* ========================================================
       SOURCES
       ======================================================== */

    .source-card {
        margin: 8px 0;

        padding: 12px 14px;

        background: var(--bg-dark-3);

        border: 1px solid rgba(201, 167, 255, 0.14);

        border-radius: 12px;

        font-size: 13px;

        color: var(--soft-purple);

        word-break: break-word;
    }


    .source-label {
        color: var(--accent);

        font-weight: 600;

        margin-bottom: 4px;
    }


    /* ========================================================
       EXPANDER
       ======================================================== */

    [data-testid="stExpander"] {
        background: var(--bg-dark-2) !important;

        border: 1px solid rgba(201, 167, 255, 0.12) !important;

        border-radius: 12px !important;
    }


    [data-testid="stExpander"] summary {
        color: var(--text-main) !important;
    }


    /* ========================================================
       GENERAL TEXT
       ======================================================== */

    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
        color: var(--text-main) !important;
    }

    </style>
    """
)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # Session
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-title">Session</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "Clear Chat",
        use_container_width=True,
        icon=":material/delete_sweep:",
    ):
        st.session_state.pop("messages", None)
        st.rerun()


    st.divider()


    # --------------------------------------------------------
    # About
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-title">About</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-description">
            An AI-powered documentation assistant for
            <b>React Three Fiber</b>.
            <br><br>
            Ask questions and get answers grounded in
            the official R3F documentation using
            retrieval-augmented generation.
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.divider()


    # --------------------------------------------------------
    # Stack
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-title">Stack</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="stack-item">
            <span class="stack-icon">◈</span>
            Gemini
        </div>

        <div class="stack-item">
            <span class="stack-icon">◈</span>
            Pinecone
        </div>

        <div class="stack-item">
            <span class="stack-icon">◈</span>
            Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# Main Header
# ============================================================

st.html(
    """
    <div class="r3f-header">

        <div class="r3f-logo">
            ◈
        </div>

        <div>

            <div class="r3f-title">
                R3F Documentation Helper
            </div>

            <div class="r3f-subtitle">
                Ask questions about React Three Fiber and get
                answers grounded in the official documentation.
            </div>

        </div>

    </div>
    """
)


# ============================================================
# Initialize Chat History
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "assistant",

            "content": (
                "I am R3F documentation helper. "
                "Ask me your queries. "
                "I'll strictly stick to the official docs "
                "to help you with that!"
            ),

            "sources": [],
        }
    ]


# ============================================================
# Display Chat History
# ============================================================

for msg in st.session_state.messages:

    role = msg["role"]

    with st.chat_message(
        role,
        avatar=(
            ":material/smart_toy:"
            if role == "assistant"
            else ":material/person:"
        ),
    ):

        st.markdown(
            f'<div class="{_bubble_class(role)}">\n\n{msg["content"]}\n\n</div>',
            unsafe_allow_html=True,
        )


        # ----------------------------------------------------
        # Sources
        # ----------------------------------------------------

        if msg.get("sources"):

            with st.expander(
                "Sources",
                icon=":material/menu_book:",
            ):

                for source in msg["sources"]:

                    st.html(
                        f"""
                        <div class="source-card">

                            <div class="source-label">
                                Source
                            </div>

                            <div>
                                {source}
                            </div>

                        </div>
                        """
                    )


# ============================================================
# Chat Input
# ============================================================

prompt = st.chat_input(
    "Ask me about React Three Fiber..."
)


# ============================================================
# Process User Query
# ============================================================

if prompt:

    # --------------------------------------------------------
    # Add user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
            "sources": [],
        }
    )


    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    with st.chat_message(
        "user",
        avatar=":material/person:",
    ):

        st.markdown(
            f'<div class="{_bubble_class("user")}">\n\n{prompt}\n\n</div>',
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # Generate assistant response
    # --------------------------------------------------------

    with st.chat_message(
        "assistant",
        avatar=":material/smart_toy:",
    ):

        try:

            # ------------------------------------------------
            # Retrieval / Generation Animation
            # ------------------------------------------------

            status_placeholder = st.empty()

            try:

                status_placeholder.html(
                    """
                    <div class="retrieval-status">

                        <span class="retrieval-text">
                            Retrieving docs and generating answer
                        </span>

                        <span class="retrieval-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </span>

                        <span class="retrieval-cat-track">

                            <span class="retrieval-mouse">
                                🐁
                            </span>

                            <span class="retrieval-cat">
                                🐈
                            </span>

                        </span>

                    </div>
                    """
                )


                # ------------------------------------------------
                # Run the actual RAG agent
                # ------------------------------------------------

                result: Dict[str, Any] = run_llm(prompt)


            finally:

                # ------------------------------------------------
                # Remove animation when agent finishes
                # ------------------------------------------------

                status_placeholder.empty()


            # ------------------------------------------------
            # Extract answer
            # ------------------------------------------------

            answer = str(
                result.get("answer", "")
            ).strip()


            if not answer:
                answer = "(No answer returned.)"


            # ------------------------------------------------
            # Extract sources
            # ------------------------------------------------

            sources = _format_sources(
                result.get("context", [])
            )


            # ------------------------------------------------
            # Display answer
            # ------------------------------------------------

            st.markdown(
                f'<div class="{_bubble_class("assistant")}">\n\n{answer}\n\n</div>',
                unsafe_allow_html=True,
            )


            # ------------------------------------------------
            # Display sources
            # ------------------------------------------------

            if sources:

                with st.expander(
                    "Sources",
                    icon=":material/menu_book:",
                ):

                    for source in sources:

                        st.html(
                            f"""
                            <div class="source-card">

                                <div class="source-label">
                                    Source
                                </div>

                                <div>
                                    {source}
                                </div>

                            </div>
                            """
                        )


            # ------------------------------------------------
            # Save assistant response
            # ------------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                }
            )


        except Exception as e:

            st.error(
                "Failed to generate a response."
            )

            st.exception(e)