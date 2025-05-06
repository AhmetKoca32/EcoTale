import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the Gemini API with your API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=api_key)

# Define the model to use
model = genai.GenerativeModel('gemini-1.5-pro')

def generate_story(topic, age_range="4-10"):
    """Generate a sustainability story based on the selected topic"""
    prompt = f"""
    Create an engaging and educational children's story (for ages {age_range}) about sustainability 
    focused on the topic: {topic}.
    
    The story should:
    - Be appropriate for young children (simple language, short paragraphs)
    - Include relatable characters (can be children, animals, or fantasy creatures)
    - Have a clear beginning, middle, and end
    - Teach a lesson about sustainability and environmental responsibility
    - Be positive and hopeful
    - End with a simple call to action or takeaway message
    - Be between 300-500 words
    - Be written in Turkish language
    
    Write only the story text with no additional notes or commentary.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating story with Gemini API: {e}")
        return "Hikaye oluşturulamadı. Lütfen daha sonra tekrar deneyin."

# Test the function
if __name__ == "__main__":
    topic = "Temiz Su ve Sanitasyon"
    print(f"Generating story about: {topic}")
    story = generate_story(topic)
    print("\nGenerated Story:\n")
    print(story) 