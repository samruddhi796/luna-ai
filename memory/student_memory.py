import os
import json
import sqlite3
import asyncio
import nest_asyncio
from datetime import datetime

# Path to the SQLite database managed by ADK
DB_PATH = "memory/data/luna_sessions.db"

def load_memory(student_id: str) -> dict:
    """Load student memory from the ADK SQLite session database."""
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
        print(f"Error loading memory from SQLite: {e}")
    return {}

def save_memory(student_id: str, data: dict):
    """Save student memory to the ADK SQLite session database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Import session service from orchestrator to initialize session if it doesn't exist
    from agents.orchestrator import session_service
    
    # Check synchronously if the session already exists in SQLite
    session_exists = False
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT count(*) FROM sessions WHERE app_name='luna' AND user_id=? AND id=?",
                (student_id, student_id)
            )
            session_exists = cursor.fetchone()[0] > 0
            conn.close()
        except Exception:
            session_exists = False

    if session_exists:
        # Session exists: Update SQLite database directly to persist immediately (fully sync)
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            state_json = json.dumps(data)
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
        except Exception as ex:
            print(f"Error in direct SQLite save_memory: {ex}")
    else:
        # Session does not exist: Create it via ADK session service (async)
        async def create_session_async():
            await session_service.create_session(
                app_name="luna",
                user_id=student_id,
                session_id=student_id,
                state=data
            )

        nest_asyncio.apply()
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(create_session_async())
        except Exception as e:
            print(f"Error creating session async: {e}")

def update_topics(student_id: str, topic: str):
    """Add a topic to the student's covered list in the database."""
    mem = load_memory(student_id)
    if not mem:
        return
    topics = mem.get("topics_covered", [])
    if topic not in topics:
        topics.append(topic)
    mem["topics_covered"] = topics[-20:]
    save_memory(student_id, mem)

def update_weak_areas(student_id: str, area: str):
    """Mark an area as needing more work in the database."""
    mem = load_memory(student_id)
    if not mem:
        return
    weak = mem.get("weak_areas", [])
    if area not in weak:
        weak.append(area)
    mem["weak_areas"] = weak[-10:]
    save_memory(student_id, mem)

def get_summary(student_id: str) -> str:
    """Return a human-readable memory summary."""
    mem = load_memory(student_id)
    if not mem:
        return "No memory found for this student."
    lines = [
        f"Name: {mem.get('name', 'Unknown')}",
        f"Level: {mem.get('grade', 'Unknown')}",
        f"Subject: {mem.get('subject', 'Unknown')}",
        f"Topics covered: {', '.join(mem.get('topics_covered', [])) or 'None yet'}",
        f"Weak areas: {', '.join(mem.get('weak_areas', [])) or 'None identified'}",
        f"Mastered topics: {', '.join(mem.get('mastered_topics', [])) or 'None'}",
        f"Last active: {mem.get('last_active', 'Unknown')}"
    ]
    return "\n".join(lines)
