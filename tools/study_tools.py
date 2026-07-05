import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re
from datetime import datetime
from google.adk.agents.context import Context

def web_search_tool(query: str) -> str:
    """
    Searches the web for study resources, guides, and explanations.
    Use this tool when the student asks for explanations, reference materials, or wants to read further.
    
    Args:
        query: The search query.
        
    Returns:
        A markdown-formatted list of organic search results with links and summaries.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Scrape result divs
        for body in soup.find_all('div', class_='result__body')[:5]:
            title_a = body.find('a', class_='result__a')
            snippet_div = body.find('a', class_='result__snippet')
            if title_a:
                title = title_a.get_text(strip=True)
                link = title_a['href']
                
                # Filter out tracking, redirect, and advertisement URLs
                if "y.js" in link or "ad_domain" in link or "duckduckgo.com/y.js" in link:
                    continue
                
                snippet = snippet_div.get_text(strip=True) if snippet_div else ""
                results.append(f"- **[{title}]({link})**\n  {snippet}")
                if len(results) >= 3: # limit to top 3 organic results
                    break
                    
        if not results:
            return f"No organic web results found for: '{query}'."
        return "\n".join(results)
    except Exception as e:
        return f"Could not fetch live search results. You can check here: [DuckDuckGo Search for '{query}'](https://duckduckgo.com/?q={urllib.parse.quote(query)})"

def youtube_resource_tool(topic: str) -> str:
    """
    Searches YouTube for high-quality educational video tutorials.
    Use this tool when the student wants to watch videos or needs visual/audio resources for a topic.
    
    Args:
        topic: The topic or concept to find tutorials for.
        
    Returns:
        A markdown-formatted list of relevant YouTube video links and titles.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(topic + " tutorial educational")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8')
            
        # Parse out video renderers
        video_ids = re.findall(r'"videoId":"([^"]+)"', html)
        titles = re.findall(r'"title":{"runs":\[{"text":"([^"]+)"\}\]', html)
        
        results = []
        seen = set()
        for vid, title in zip(video_ids, titles):
            if vid not in seen:
                seen.add(vid)
                try:
                    clean_title = title.encode().decode('unicode-escape', errors='ignore')
                except Exception:
                    clean_title = title
                results.append(f"- **[{clean_title}](https://www.youtube.com/watch?v={vid})**")
                if len(results) >= 2: # Top 2 videos
                    break
                    
        if not results:
            return f"Could not find specific videos. Try searching directly on YouTube: [YouTube Search for '{topic}'](https://www.youtube.com/results?search_query={urllib.parse.quote(topic)})"
            
        return "\n".join(results)
    except Exception:
        # Fallback to avoid crashing as requested by the user
        return f"Check out these YouTube tutorials: [YouTube Search for '{topic}'](https://www.youtube.com/results?search_query={urllib.parse.quote(topic)})"

def save_progress_tool(context: Context, topic: str, score: int, max_score: int = 5) -> str:
    """
    Saves a student's quiz score and dynamically updates their mastery/weak areas.
    Use this tool ONLY after the student completes a quiz to log their score.
    
    Args:
        context: The ADK agent execution context (injected automatically).
        topic: The topic of the quiz.
        score: The score the student achieved.
        max_score: The maximum possible score on the quiz (defaults to 5).
        
    Returns:
        A confirmation message summarizing progress and current mastery status.
    """
    state = context.state
    
    # Initialize state fields if not present
    if "quiz_scores" not in state:
        state["quiz_scores"] = []
    if "topics_covered" not in state:
        state["topics_covered"] = []
    if "weak_areas" not in state:
        state["weak_areas"] = []
    if "mastered_topics" not in state:
        state["mastered_topics"] = []
        
    # Standardize topic casing
    topic_key = topic.strip().lower()
    
    # Write structured progress log
    score_entry = {
        "topic": topic.strip(),
        "date": str(datetime.now().date()),
        "score": score,
        "max_score": max_score,
        "mastery_level": "mastered" if (score / max_score) >= 0.8 else "weak"
    }
    state["quiz_scores"].append(score_entry)
    
    # Track topic coverage
    display_topic = topic.strip()
    if display_topic not in state["topics_covered"]:
        state["topics_covered"].append(display_topic)
        
    # Analyze mastery status on this specific topic
    # Find all quizzes taken on this topic (case insensitive)
    topic_quizzes = [q for q in state["quiz_scores"] if q["topic"].strip().lower() == topic_key]
    high_scores_count = sum(1 for q in topic_quizzes if (q["score"] / q["max_score"]) >= 0.8)
    
    # Determine mastery: 3 quizzes >= 80%
    is_mastered = high_scores_count >= 3
    
    # Normalize lists (case insensitive lists display clean casing)
    # Check if currently in weak_areas
    weak_matching = [w for w in state["weak_areas"] if w.strip().lower() == topic_key]
    mastered_matching = [m for m in state["mastered_topics"] if m.strip().lower() == topic_key]
    
    if is_mastered:
        # Move to mastered_topics
        if not mastered_matching:
            state["mastered_topics"].append(display_topic)
        # Remove from weak_areas
        for w in weak_matching:
            if w in state["weak_areas"]:
                state["weak_areas"].remove(w)
        status_msg = f"🏆 Mastery achieved! You have scored >= 80% on {high_scores_count} quizzes on this topic."
    else:
        # If last score is low, or they haven't reached 3 high scores yet
        pct = (score / max_score) * 100
        if pct < 80.0:
            if not weak_matching:
                state["weak_areas"].append(display_topic)
            for m in mastered_matching:
                if m in state["mastered_topics"]:
                    state["mastered_topics"].remove(m)
            status_msg = f"⚠️ Added to weak areas. Score is {pct:.1f}% (need >= 80% to count towards mastery)."
        else:
            status_msg = f"📈 Great job! You scored {pct:.1f}%. You need {3 - high_scores_count} more quizzes with >= 80% score to master this topic."
            
    return f"Logged quiz score: {score}/{max_score} for '{display_topic}'. {status_msg}"
