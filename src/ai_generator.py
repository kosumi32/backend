import os 
import json
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()  # Fixed: Added parentheses to actually call the function
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Debug: Print to check if API key is loaded
if GOOGLE_API_KEY:
    print(f"✅ Google API Key loaded successfully (length: {len(GOOGLE_API_KEY)})")
else:
    print("❌ Google API Key not found in environment variables")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Environment variables containing 'GOOGLE': {[k for k in os.environ.keys() if 'GOOGLE' in k]}")

genai.configure(api_key=GOOGLE_API_KEY)

model= genai.GenerativeModel("gemini-2.0-flash-lite")

# prompt = "Hello world"

# response= model.generate_content(prompt)

# text must be a string, it returns a dict with key (str) and value (any)
def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Removes markdown code blocks and extracts JSON from a text string.
    """

    # Remove markdown code block syntax
    if text.startswith("```json") and text.endswith("```"):
        text = text[7:-3].strip()  # Remove the ```json and trailing ```
    try:
        # Parse the JSON content
        return json.loads(text)
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")


# Specify return Dict
def generate_challenge_with_ai(difficulty: str) -> Dict[str, Any]:
    system_prompt = """
        You are an expert trivia question creator.

        Your task is to generate a multiple-choice fact question that tests general knowledge. The question should be appropriate for the specified difficulty level.

        Difficulty Levels:
        - Easy: Common facts or well-known trivia (e.g. capital cities, popular history, famous people).
        - Medium: Lesser-known facts, moderate science, culture, or geography.
        - Hard: Obscure facts, advanced history, science, or niche cultural references.

        Return the question in the following JSON format:
        {
            "title": "The trivia question goes here",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer_id": 0,  // Index (0–3) of the correct answer
            "explanation": "A detailed explanation about why the answer is correct"
        }

        Requirements:
        - Only one correct answer.
        - Other options should be plausible but incorrect.
        - Ensure factual accuracy.
        - Keep it fun and educational.
        """
    
    try:

        # This version concatenates messages (like in a chat history)
        # You provide a list of messages, and Gemini treats them sequentially — 
        # as if a system prompt is followed by a user prompt.
        response = model.generate_content([
            system_prompt,
            f"Create a {difficulty} trivia question."
        ])

        #  Gemini’s .text output is always a plain text string, not a clean JSON object. 
        # Often, it returns the JSON inside a Markdown block:

        # ```json
        # {
        #   "title": "What is the capital of Canada?",
        #   "options": ["Toronto", "Vancouver", "Ottawa", "Montreal"],
        #   "correct_answer_id": 2,
        #   "explanation": "Ottawa is the capital city of Canada."
        # }
        # ```
        
        if not response or not response.text:
            raise ValueError("No response received from AI model.")
        
        content= response.text

        # Parse the JSON response
        question_data = extract_json_from_text(content)
        
        # Validate the structure
        required_keys = {'title', 'options', 'correct_answer_id', 'explanation'}
        for key in required_keys:
            if key not in question_data:
                raise ValueError(f"Missing required key: {key}")

        return question_data
    
    except Exception as e:
        print(e)

        # Default answer
        return {
            "title": "What is the capital of France?",
            "options": ["Berlin", "Madrid", "Paris", "Rome"],
            "correct_answer_id": 2,
            "explanation": "Paris is the capital city of France."
        }