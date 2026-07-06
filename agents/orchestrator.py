import os
import json
import sqlite3
import asyncio
import nest_asyncio
from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.runners import Runner
from google.adk.sessions.database_session_service import DatabaseSessionService
from google.genai import types

# Import the specialized sub-agents
from agents.concept_explainer import concept_explainer_agent
from agents.study_planner import study_planner_agent
from agents.quiz_agent import quiz_agent_agent
from agents.career_guide import career_guide_agent
from agents.general_agent import general_agent_agent

# Wrap specialist agents as tools for the Orchestrator
concept_explainer_tool = AgentTool(agent=concept_explainer_agent)
study_planner_tool = AgentTool(agent=study_planner_agent)
quiz_agent_tool = AgentTool(agent=quiz_agent_agent)
career_guide_tool = AgentTool(agent=career_guide_agent)
general_agent_tool = AgentTool(agent=general_agent_agent)

# Define the master coordinator agent
orchestrator_agent = Agent(
    name="Orchestrator",
    model="gemini-2.5-flash",
    description="Main entry point that delegates student messages to specialized sub-agents.",
    instruction="""You are Luna, a friendly and intelligent AI learning companion.
Your job is to coordinate the learning experience. For general greetings, casual chat, motivational boosts, or general questions, you should answer the student directly.
However, for specialized requests, you MUST delegate to one of these specialist tools:
- Use 'ConceptExplainer' if the student wants to learn, understand, define, or explain a concept, topic, or formula.
- Use 'StudyPlanner' if the student wants a study plan, timeline, schedule, or revision schedule.
- Use 'QuizAgent' if the student wants to take a test, quiz, practice MCQs, check quiz answers, or is currently answering quiz questions.
- Use 'CareerGuide' if the student asks about jobs, careers, skills, roadmaps, certifications, or internships.
- Use 'GeneralAgent' for greetings and casual chat if you prefer not to answer directly.

When you call a tool, your final response MUST be exactly the text returned by that tool, with absolutely no edits or conversational filler of your own.""",
    tools=[
        concept_explainer_tool,
        study_planner_tool,
        quiz_agent_tool,
        career_guide_tool,
        general_agent_tool
    ]
)

# SQLite session database path
DB_DIR = "memory/data"
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "luna_sessions.db")
DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Global session service
session_service = DatabaseSessionService(db_url=DB_URL)

def get_session_state(student_id: str) -> dict:
    """Helper to retrieve the current session state dict for a student synchronously via SQLite."""
    if not os.path.exists(DB_PATH):
        return {}
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT state FROM sessions WHERE app_name='luna' AND user_id=? AND id=?",
            (student_id, student_id)
        )
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return json.loads(row[0])
    except Exception as e:
        print(f"Error fetching session state via SQLite: {e}")
    return {}

def orchestrate(user_message: str, student_id: str, api_key: str, state_delta: dict = None) -> tuple[str, str]:
    """
    Main orchestrator entry point:
    1. Sets the API key in the environment for ADK.
    2. Loads/creates the student's session.
    3. Runs the ADK Runner to delegate the query.
    4. Detects which sub-agent was invoked via event tracking.
    """
    # 1. Set GEMINI_API_KEY for ADK/google-genai Client
    os.environ["GEMINI_API_KEY"] = api_key

    # Initialize / update session via async coroutines run synchronously
    async def setup_session():
        try:
            session = await session_service.get_session(
                app_name="luna",
                user_id=student_id,
                session_id=student_id
            )
        except Exception:
            session = None

        if not session:
            # Create a new session with initial state
            initial_state = state_delta or {}
            session = await session_service.create_session(
                app_name="luna",
                user_id=student_id,
                session_id=student_id,
                state=initial_state
            )
        elif state_delta:
            # Update session state with any new profile details (merge) and update SQLite
            session.state.update(state_delta)
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            state_json = json.dumps(session.state)
            cursor.execute(
                "UPDATE sessions SET state=? WHERE app_name='luna' AND user_id=? AND id=?",
                (state_json, student_id, student_id)
            )
            cursor.execute(
                "UPDATE user_states SET state=? WHERE app_name='luna' AND user_id=?",
                (state_json, student_id)
            )
            conn.commit()
            conn.close()
        return session

    # Run the setup_session coroutine synchronously using nest_asyncio
    nest_asyncio.apply()
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(setup_session())

    # 2. Create Runner
    runner = Runner(
        agent=orchestrator_agent,
        app_name="luna",
        session_service=session_service
    )

    # 3. Create content object for message
    new_msg = types.Content(
        role="user",
        parts=[types.Part(text=user_message)]
    )

    # 4. Run the runner and trace execution events to capture response and active sub-agent
    response_text = ""
    agent_used = "Luna"

    agent_display_names = {
        "ConceptExplainer": "Concept Explainer",
        "StudyPlanner": "Study Planner",
        "QuizAgent": "Quiz Agent",
        "CareerGuide": "Career Guide",
        "GeneralAgent": "Luna"
    }

    # Run the generator synchronously
    for event in runner.run(
        user_id=student_id,
        session_id=student_id,
        new_message=new_msg
    ):
        # 1. Capture tool calls (sub-agents)
        for call in event.get_function_calls():
            if call.name in agent_display_names:
                agent_used = agent_display_names[call.name]

        # 2. Capture node name
        if event.node_name in agent_display_names:
            agent_used = agent_display_names[event.node_name]

        # Accumulate final response text
        if event.is_final_response() and event.content and event.content.parts:
            response_text = event.content.parts[0].text

    if not response_text:
        response_text = "Sorry, I couldn't process that query."

    return response_text, agent_used
