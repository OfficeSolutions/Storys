from google import genai

# Initialize the client with the provided API key
API_KEY = "AIzaSyD_TRW55r7Am5mhsKiQph9RHwyfml9WOH4"
client = genai.Client(api_key=API_KEY)

def text_generation_example():
    """Demonstrates basic text generation with Gemini"""
    print("\n=== TEXT GENERATION EXAMPLE ===")
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Write a short poem about artificial intelligence."
        )
        print("Generated poem:")
        print(response.text)
    except Exception as e:
        print(f"Error in text generation: {str(e)}")

def simple_chat_example():
    """Demonstrates a simple chat with Gemini using separate requests"""
    print("\n=== SIMPLE CHAT EXAMPLE ===")
    try:
        # First message
        print("User: Hello, I'd like to learn about Mars.")
        response1 = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Hello, I'd like to learn about Mars."
        )
        print(f"Gemini: {response1.text}\n")
        
        # Follow-up question (including context from previous exchange)
        print("User: What about its moons?")
        response2 = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="I asked about Mars. You provided information about Mars. Now tell me about Mars' moons."
        )
        print(f"Gemini: {response2.text}")
    except Exception as e:
        print(f"Error in chat example: {str(e)}")

def error_handling_example():
    """Demonstrates error handling with invalid requests"""
    print("\n=== ERROR HANDLING EXAMPLE ===")
    try:
        # Intentionally use an invalid model name
        response = client.models.generate_content(
            model="non-existent-model",
            contents="This should fail with a model not found error."
        )
        print("This should not be reached")
    except Exception as e:
        print(f"Expected error caught: {str(e)}")
        print("Error handling successful!")

if __name__ == "__main__":
    print("FINAL GEMINI API EXAMPLES")
    print("=========================")
    
    # Run examples
    text_generation_example()
    simple_chat_example()
    error_handling_example()
    
    print("\nAll examples completed!")
