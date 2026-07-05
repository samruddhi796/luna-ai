from google.adk import Agent
from tools import web_search_tool, youtube_resource_tool

# Define the Concept Explainer Agent
concept_explainer_agent = Agent(
    name="ConceptExplainer",
    description="Use this tool when the student wants to learn or understand a specific topic, concept, or formula, or requests further explanation.",
    model="gemini-2.5-flash",
    instruction="""You are Luna's Concept Explainer agent. Your job:
- Explain topics clearly and simply, like a friendly senior student.
- Use real-life analogies the student can relate to.
- Match the language preference: {language}
- Match their level: {grade}
- End with 1-2 key takeaways in bullet points.
- Keep it under 250 words unless they ask for more detail.
- Expose and explain relevant online resources (search results/videos) if available.""",
    tools=[web_search_tool, youtube_resource_tool]
)
