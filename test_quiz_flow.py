import os
import json
import sqlite3
import time
import dotenv
from agents.orchestrator import orchestrate, DB_PATH
from memory.student_memory import load_memory

def main():
    dotenv.load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    # 1. Reset / Delete existing SQLite database for a clean test
    if os.path.exists(DB_PATH):
        try:
            # Try to delete tables instead of deleting the file if it is locked
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS sessions")
            cursor.execute("DROP TABLE IF EXISTS user_states")
            conn.commit()
            conn.close()
            print("Reset sessions table successfully.")
        except Exception as e:
            print(f"Could not reset tables: {e}")

    student_id = "test_student_sam_unique_99"
    state_delta = {
        "name": "Sam",
        "grade": "School (11-12)",
        "subject": "Python Programming",
        "language": "English",
        "topics_covered": [],
        "weak_areas": [],
        "mastered_topics": [],
        "quiz_scores": []
    }

    print("\n=== STEP 1: Starting Quiz ===")
    print("Sending: 'Quiz me on Python lists'")
    
    # Run first turn
    resp1, agent1 = orchestrate(
        user_message="Quiz me on Python lists",
        student_id=student_id,
        api_key=api_key,
        state_delta=state_delta
    )
    print(f"Agent badge: {agent1}")
    print(f"Response:\n{resp1}\n")

    # Sleep 30 seconds to respect API rate limits
    print("Waiting 30 seconds before submitting answers to prevent rate limiting...")
    time.sleep(30)

    print("=== STEP 2: Submitting Answers ===")
    # Simulate student replying with answers
    student_answers = "Here are my answers: 1) A, 2) B, 3) C, 4) D"
    print(f"Sending: '{student_answers}'")

    resp2, agent2 = orchestrate(
        user_message=student_answers,
        student_id=student_id,
        api_key=api_key
    )
    print(f"Agent badge: {agent2}")
    print(f"Response:\n{resp2}\n")

    print("=== STEP 3: Verifying Database (Bug 2) ===")
    mem = load_memory(student_id)
    print(f"Current Memory State:")
    print(f"  - Topics Covered: {mem.get('topics_covered')}")
    print(f"  - Weak Areas: {mem.get('weak_areas')}")
    print(f"  - Mastered Topics: {mem.get('mastered_topics')}")
    print(f"  - Quiz Scores: {mem.get('quiz_scores')}")

    if mem.get("quiz_scores"):
        print("\nSUCCESS: Quiz score was logged successfully!")
    else:
        print("\nFAILURE: Quiz score was not found in DB.")

if __name__ == "__main__":
    main()
