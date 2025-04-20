"""
Text Generation and Content Creation Example using Gemini API

This script demonstrates how to use the Gemini API for text generation and content creation.
It shows how to:
1. Generate creative content (stories, blog posts, marketing copy)
2. Create structured content with specific formats
3. Enhance and rewrite existing content
"""

from google import genai
import time

# Initialize the client with the provided API key
API_KEY = "AIzaSyD_TRW55r7Am5mhsKiQph9RHwyfml9WOH4"
client = genai.Client(api_key=API_KEY)

def generate_content(prompt):
    """Generate content using Gemini API."""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error generating content: {str(e)}"

def main():
    print("GEMINI TEXT GENERATION EXAMPLE")
    print("==============================\n")
    
    # Example 1: Creative Writing
    creative_prompt = """
    Write a short story (about 300 words) about a scientist who discovers 
    a way to communicate with plants. The story should have a surprising twist ending.
    """
    
    print("=== CREATIVE WRITING EXAMPLE ===")
    print("Generating a short story...\n")
    story = generate_content(creative_prompt)
    print(story)
    print("\n" + "-"*50 + "\n")
    
    # Allow some time between API calls
    time.sleep(2)
    
    # Example 2: Structured Content
    structured_prompt = """
    Create a blog post outline about sustainable technology. 
    The outline should include:
    - An engaging title
    - Introduction section
    - 4-5 main sections with brief descriptions
    - Conclusion section
    - 3 potential call-to-action ideas
    """
    
    print("=== STRUCTURED CONTENT EXAMPLE ===")
    print("Generating a blog post outline...\n")
    outline = generate_content(structured_prompt)
    print(outline)
    print("\n" + "-"*50 + "\n")
    
    # Allow some time between API calls
    time.sleep(2)
    
    # Example 3: Content Enhancement
    original_text = """
    AI is changing how we work. It helps with many tasks. Companies use it a lot now.
    It can be good for productivity. Some people worry about jobs. The future will be different.
    """
    
    enhancement_prompt = f"""
    Enhance and expand the following text to make it more engaging, informative, and professional.
    Add specific examples and data points where appropriate.
    
    Original text:
    {original_text}
    """
    
    print("=== CONTENT ENHANCEMENT EXAMPLE ===")
    print("Original text:")
    print(original_text)
    print("\nEnhanced version:")
    enhanced_text = generate_content(enhancement_prompt)
    print(enhanced_text)
    
    print("\nText generation examples complete!")

if __name__ == "__main__":
    main()
