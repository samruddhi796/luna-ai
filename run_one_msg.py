import os
import sys
import dotenv
from google.adk.runners import Runner
from google.genai import types
from agents.orchestrator import orchestrate, orchestrator_agent, session_service

def main():
    dotenv.load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    os.environ["GEMINI_API_KEY"] = api_key
    if not api_key:
        if len(sys.argv) > 1:
            api_key = sys.argv[1]
        else:
            print("Error: Please set the GEMINI_API_KEY environment variable or pass it as an argument:")
            print("  python run_one_msg.py YOUR_API_KEY")
            sys.exit(1)
            
    student_id = "student_samruddhi"
    
    # Pre-populate student state for the test
    state_delta = {
        "name": "Samruddhi",
        "grade": "College Year 3",
        "subject": "Computer Science",
        "language": "English",
        "topics_covered": [],
        "weak_areas": [],
        "mastered_topics": [],
        "quiz_scores": []
    }
    
    print("Sending message: 'Explain what is recursion'...")
    try:
        runner = Runner(
            agent=orchestrator_agent,
            app_name="luna",
            session_service=session_service
        )
        new_msg = types.Content(
            role="user",
            parts=[types.Part(text="Explain what is recursion")]
        )
        response_text = ""
        agent_used = "Luna"
        
        agent_display_names = {
            "ConceptExplainer": "Concept Explainer",
            "StudyPlanner": "Study Planner",
            "QuizAgent": "Quiz Agent",
            "CareerGuide": "Career Guide",
            "GeneralAgent": "Luna"
        }
        
        for event in runner.run(
            user_id=student_id,
            session_id=student_id,
            new_message=new_msg
        ):
            print(f"DEBUG: node_name={event.node_name}, author={event.author}, is_final={event.is_final_response()}")
            if event.actions:
                print(f"  Actions: {event.actions}")
            if event.node_name in agent_display_names:
                agent_used = agent_display_names[event.node_name]
            if event.is_final_response() and event.content and event.content.parts:
                response_text = event.content.parts[0].text

        print("\n--- Response Received ---")
        print(f"Agent Used: {agent_used}")
        print(response_text)
        print("-------------------------\n")
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
