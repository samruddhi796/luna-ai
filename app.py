import streamlit as st
import json
import os
from datetime import datetime
import dotenv
from memory.student_memory import load_memory, save_memory
from agents.orchestrator import orchestrate

# Load API Key from environment or .env file
dotenv.load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY", "")

# Helper to render styled agent badges
def get_agent_badge_html(agent_name: str) -> str:
    agent_class_map = {
        "Quiz Agent": "badge-quiz",
        "Concept Explainer": "badge-concept",
        "Career Guide": "badge-career",
        "Study Planner": "badge-study",
        "Luna": "badge-luna"
    }
    cls = agent_class_map.get(agent_name, "badge-luna")
    return f'<div class="agent-badge {cls}">🤖 {agent_name}</div>'

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Luna AI",
    page_icon="🌙",
    layout="centered",
)

# ── CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* App background and text */
[data-testid="stAppViewContainer"] {
    background-color: #0d0a1a !important;
    color: #e8e0ff !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #120d24 !important;
    border-right: 1px solid #2d2052 !important;
}
section[data-testid="stSidebar"] > div {
    background-color: #120d24 !important;
}

/* Header */
.luna-header {
    text-align: center;
    padding: 2rem 0 1rem;
}
.luna-header h1 {
    font-size: 2.4rem;
    font-weight: 600;
    color: #e8e0ff !important;
    margin: 0;
    letter-spacing: -0.5px;
}
.luna-header p {
    color: #7c6faa !important;
    margin-top: 0.4rem;
    font-size: 1rem;
}
.moon {
    font-size: 2rem;
    filter: drop-shadow(0 0 12px #a78bfa88);
}

/* Memory Card */
.memory-card {
    background-color: #16112b !important;
    border: 1px solid #2d2052 !important;
    border-left: 3px solid #7c3aed !important;
    color: #e8e0ff !important;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    font-size: 0.85rem;
}
.memory-card b {
    color: #a78bfa !important;
}

/* Base agent badge */
.agent-badge {
    display: inline-block;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.75rem;
    font-weight: 500;
    margin-bottom: 6px;
    border: 1px solid #2d2052;
}

/* Badges by type */
.badge-quiz {
    background-color: #1a0d2e !important;
    color: #c084fc !important;
}
.badge-concept {
    background-color: #0d1f3c !important;
    color: #60a5fa !important;
}
.badge-career {
    background-color: #0d2018 !important;
    color: #4ade80 !important;
}
.badge-study {
    background-color: #1f1508 !important;
    color: #fb923c !important;
}
.badge-luna {
    background-color: #16112b !important;
    color: #a78bfa !important;
}

/* Chat bubble overrides */
[data-testid="stChatMessage"] {
    background-color: #16112b !important;
    border: 1px solid #2d2052 !important;
    border-radius: 12px;
    color: #e8e0ff !important;
}

/* Text Input & Text Area */
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
    background-color: #16112b !important;
    color: #e8e0ff !important;
    border: 1px solid #2d2052 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 1px solid #2d2052 !important;
}
.stTabs [data-baseweb="tab"] {
    color: #7c6faa !important;
}
.stTabs [aria-selected="true"] {
    color: #a78bfa !important;
    border-bottom-color: #7c3aed !important;
}

/* Progress bar override */
.stProgress > div > div > div > div {
    background: linear-gradient(to right, #7c3aed, #a855f7) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────
st.markdown("""
<div class="luna-header">
    <div class="moon">🌙</div>
    <h1>Luna AI</h1>
    <p>Your personal learning companion — available 24/7</p>
</div>
""", unsafe_allow_html=True)

# ── API Key input ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Setup")
    api_key_input = st.text_input("Gemini API Key", type="password",
                                  value=api_key,
                                  help="Get your free key at aistudio.google.com")
    if api_key_input:
        api_key = api_key_input
        os.environ["GEMINI_API_KEY"] = api_key_input
        
    st.markdown("---")
    st.markdown("### 🧠 What Luna can do")
    st.markdown("""
- 📚 Explain any concept simply
- 📅 Build your study plan
- ✅ Quiz you on topics
- 🎯 Guide your career path
- 🌍 Works in any language
    """)
    st.markdown("---")
    st.markdown("### 👤 Your Profile")

    # Show memory in sidebar
    if "student_id" in st.session_state:
        mem = load_memory(st.session_state.student_id)
        if mem.get("name"):
            st.markdown(f"**Name:** {mem['name']}")
        if mem.get("topics_covered"):
            st.markdown(f"**Topics covered:** {', '.join(mem['topics_covered'][-5:])}")
        if mem.get("mastered_topics"):
            st.markdown(f"**Mastered:** {', '.join(mem['mastered_topics'])}")
        if mem.get("weak_areas"):
            st.markdown(f"**Needs work:** {', '.join(mem['weak_areas'])}")

# ── Student onboarding ──────────────────────────────────────────
if "student_id" not in st.session_state:
    st.markdown("### 👋 Welcome! Let's set up your profile")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your name")
        grade = st.selectbox("Your level", [
            "School (6-8)", "School (9-10)", "School (11-12)",
            "College Year 1", "College Year 2", "College Year 3", "College Year 4",
            "Self-learner"
        ])
    with col2:
        subject = st.text_input("Main subject / goal (e.g. Python, Physics, DSA)")
        lang = st.selectbox("Preferred language", ["English", "Hindi", "Hinglish", "Other"])

    if st.button("🌙 Start Learning with Luna", use_container_width=True):
        if name and subject:
            sid = f"student_{name.lower().replace(' ','_')}"
            st.session_state.student_id = sid
            st.session_state.messages = []
            mem = {
                "name": name,
                "grade": grade,
                "subject": subject,
                "language": lang,
                "topics_covered": [],
                "weak_areas": [],
                "mastered_topics": [],
                "quiz_scores": [],
                "last_active": str(datetime.now().date())
            }
            save_memory(sid, mem)
            st.rerun()
        else:
            st.warning("Please enter your name and subject!")
    st.stop()

# ── Chat interface ──────────────────────────────────────────────
if not api_key:
    st.info("👈 Enter your Gemini API key in the sidebar to start chatting with Luna!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Load student memory
mem = load_memory(st.session_state.student_id)

# Create layout tabs
tab_chat, tab_progress = st.tabs(["💬 Chat with Luna", "📈 Progress"])

with tab_progress:
    st.markdown("### 📈 Your Learning Progress")
    mastered = mem.get("mastered_topics", [])
    weak = mem.get("weak_areas", [])
    
    total = len(mastered) + len(weak)
    mastery_pct = int((len(mastered) / total) * 100) if total > 0 else 0
    
    st.metric("Subject Mastery Level", f"{mastery_pct}%")
    st.progress(mastery_pct / 100.0)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ✅ Mastered Topics")
        if mastered:
            for topic in mastered:
                st.markdown(f"- {topic}")
        else:
            st.info("No topics mastered yet. Keep learning and take quizzes!")
            
    with col2:
        st.markdown("#### ⚠️ Weak Areas")
        if weak:
            for topic in weak:
                st.markdown(f"- {topic}")
        else:
            st.success("No weak areas identified! Excellent job.")

with tab_chat:
    # Show memory context card if returning student
    if mem.get("topics_covered"):
        last = mem["topics_covered"][-1] if mem["topics_covered"] else "nothing yet"
        st.markdown(f"""
        <div class="memory-card">
            🧠 <b>Luna remembers:</b> You last studied <b>{last}</b>.
            Weak areas: <b>{', '.join(mem.get('weak_areas', ['none identified yet']))}</b>
        </div>
        """, unsafe_allow_html=True)

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("agent"):
                st.markdown(get_agent_badge_html(msg["agent"]), unsafe_allow_html=True)
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input(f"Ask Luna anything, {mem.get('name', 'there')}..."):
        # Show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get Luna's response
        with st.chat_message("assistant"):
            with st.spinner("🌙 Luna is thinking..."):
                response, agent_used = orchestrate(
                    user_message=prompt,
                    student_id=st.session_state.student_id,
                    api_key=api_key,
                    state_delta=None
                )
            if agent_used:
                st.markdown(get_agent_badge_html(agent_used), unsafe_allow_html=True)
            st.markdown(response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "agent": agent_used
        })

        # Refresh memory from DB before saving (avoids overwriting tool updates)
        mem = load_memory(st.session_state.student_id)
        mem["last_active"] = str(datetime.now().date())
        save_memory(st.session_state.student_id, mem)
        st.rerun()
