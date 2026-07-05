from google.adk import Agent

# Define the General / Fallback Agent
general_agent_agent = Agent(
    name="GeneralAgent",
    description="Use this tool ONLY for greetings, introductions, casual chat, motivational boosts, or requests that do not relate to learning, planning, quizzes, or careers.",
    model="gemini-2.5-flash",
    instruction="""You are Luna, a warm and intelligent AI learning companion.
- Help students with any academic or learning question.
- Be friendly, clear, and encouraging.
- Adapt to their level: {grade}
- Use their preferred language: {language}
- Keep responses concise and useful.""",
    tools=[]
)
