# 🌙 Luna AI — Your Personal Learning Companion

Luna AI is a multi-agent AI academic mentor that helps students learn any subject, plan their studies, get quizzed, and explore career paths — all through a friendly chat interface.

Built for the **Google × Kaggle Vibecoding Agents Capstone Hackathon** (Deadline: July 6, 2026).

---

## 🔗 Live Deployment Link
👉 **[Luna AI Live on Streamlit Cloud](https://luna-ai-samruddhi.streamlit.app)**

---

## 🚀 Quick Start (Local Setup for Judges)

### 1. Clone the repository
```bash
git clone https://github.com/samruddhi796/luna-ai
cd luna-ai
```

### 2. Configure your API key
Create a `.env` file in the root of the project:
```text
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Get a free API key at [aistudio.google.com](https://aistudio.google.com))*

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
streamlit run app.py
```
*The app will automatically open at `http://localhost:8501` and load your API key from the `.env` file.*

---

## 🤖 How Luna Works (Multi-Agent Architecture)

Luna uses a coordinator-agent orchestration pattern built on the **Google Agent Development Kit (ADK)**:

```text
                  +--------------------------------+
                  |     Streamlit UI (app.py)      |
                  +---------------+----------------+
                                  |
                                  | (user_message, student_id)
                                  v
                  +---------------+----------------+     Synchronized Read/Write
                  |   Orchestrator Agent           | <===========================> [SQLite Database]
                  |   (agents/orchestrator.py)     |                               (luna_sessions.db)
                  +---------------+----------------+
                                  |
            +---------------------+---------------------+---------------------+
            |                     |                     |                     |
            v                     v                     v                     v
    +-------+-------+     +-------+-------+     +-------+-------+     +-------+-------+
    |ConceptExplainer|     |   QuizAgent   |     | StudyPlanner  |     |  CareerGuide  |
    | (Analogies)    |     | (Adaptive MCQs)     | (Timetables)  |     |  (Roadmaps)   |
    +-------+-------+     +-------+-------+     +-------+-------+     +-------+-------+
            |                     |
            v (Tools)             v (Tools)
     +------+------+       +------+------+
     | WebSearch   |       | SaveProgress|
     | YouTube     |       +-------------+
     +-------------+
```

### 👥 Specialized Sub-Agents

| Agent | File Path | What it does |
|---|---|---|
| **Orchestrator** | [orchestrator.py](file:///c:/Users/samruddhi/OneDrive/Desktop/luna_ai/agents/orchestrator.py) | Dynamic intent classifier that delegates queries using `AgentTool` |
| **Concept Explainer** | [concept_explainer.py](file:///c:/Users/samruddhi/OneDrive/Desktop/luna_ai/agents/concept_explainer.py) | Explains concepts using simple analogies and online reference resources |
| **Quiz Agent** | [quiz_agent.py](file:///c:/Users/samruddhi/OneDrive/Desktop/luna_ai/agents/quiz_agent.py) | Generates optionwise MCQs, evaluates student answers, and updates progress |
| **Study Planner** | [study_planner.py](file:///c:/Users/samruddhi/OneDrive/Desktop/luna_ai/agents/study_planner.py) | Builds realistic day-by-day study timetables |
| **Career Guide** | [career_guide.py](file:///c:/Users/samruddhi/OneDrive/Desktop/luna_ai/agents/career_guide.py) | Maps skills, roadmaps, and free learning pathways |

---

## 🧠 Course Concepts Applied

1. **Multi-Agent Orchestration & Routing**
   * *Concept*: Orchestrating execution across multiple specialized agents.
   * *Code Link*: Exposes sub-agents as tools using `AgentTool` under [orchestrator.py](file:///c:/Users/samruddhi/OneDrive/Desktop/luna_ai/agents/orchestrator.py#L19-L55). Uses `mode=ANY` function-calling configurations to force the coordinator agent to delegate and relay sub-agent outputs verbatim.
2. **Tool Use & Dynamic Resource Fetching**
   * *Concept*: Equipping agents with custom tools to fetch live information or log data.
   * *Code Link*: Exposes `web_search_tool` (DuckDuckGo organic scraping) and `youtube_resource_tool` (YouTube video lookup) to the `ConceptExplainer` agent in [concept_explainer.py](file:///c:/Users/samruddhi/OneDrive/Desktop/luna_ai/agents/concept_explainer.py#L17). Exposes `save_progress_tool` to log student test scores in [quiz_agent.py](file:///c:/Users/samruddhi/OneDrive/Desktop/luna_ai/agents/quiz_agent.py#L18).
3. **Long-Term Memory Persistence (SQLite Session State)**
   * *Concept*: Retaining user profile, mastery progress, and chat history across browser refreshes.
   * *Code Link*: Managed via ADK's `DatabaseSessionService` in [orchestrator.py](file:///c:/Users/samruddhi/OneDrive/Desktop/luna_ai/agents/orchestrator.py#L57-L135) and bridged via [student_memory.py](file:///c:/Users/samruddhi/OneDrive/Desktop/luna_ai/memory/student_memory.py).
4. **Guardrails & Persona Control**
   * *Concept*: Ensuring agents stay on-topic, format responses correctly, and respect language choices.
   * *Code Link*: The `QuizAgent` system prompt in [quiz_agent.py](file:///c:/Users/samruddhi/OneDrive/Desktop/luna_ai/agents/quiz_agent.py#L9-L16) prevents it from generating duplicate questions by enforcing history-aware context checks before responding to answers.

---

## 📁 Project Structure

```text
luna_ai/
├── app.py                      # Streamlit UI, State Refresh, and Layout
├── requirements.txt            # Python Dependencies
├── run_one_msg.py              # Test script for a single message
├── test_quiz_flow.py           # Automated test script for full quiz and DB logging
├── .gitignore                  # Git exclusions (ignores .env, databases, and __pycache__)
├── .env                        # Local Environment Variables (Git ignored)
├── agents/                     # ADK Agents definition
│   ├── __init__.py             # Exports
│   ├── orchestrator.py         # Coordinator Routing Agent
│   ├── concept_explainer.py    # Analogies and search reference agent
│   ├── study_planner.py        # Schedule generation agent
│   ├── quiz_agent.py           # MCQ evaluation and progress agent
│   ├── career_guide.py         # Career advice and roadmap agent
│   └── general_agent.py        # Greetings and general conversation agent
├── tools/                      # Tool declarations
│   ├── __init__.py             # Exports
│   └── study_tools.py          # Search, YouTube, and Progress logging tools
└── memory/                     # Bridged memory modules
    ├── student_memory.py       # Helper functions to query and save SQLite memory
    └── data/                   # Data Directory containing luna_sessions.db
```

---

## 🌍 Track
**Agents for Good** — Education access for students worldwide

## 👥 Team
Built with 💙 for the Google × Kaggle AI Agents Hackathon 2026.
