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

def multi_turn_conversation():
    """Demonstrates a multi-turn conversation with Gemini"""
    print("\n=== MULTI-TURN CONVERSATION EXAMPLE ===")
    try:
        # Start a conversation
        conversation = client.models.start_conversation(
            model="gemini-2.0-flash"
        )
        
        # First message
        response = conversation.send_message("Hello, I'd like to learn about Mars.")
        print("User: Hello, I'd like to learn about Mars.")
        print(f"Gemini: {response.text}\n")
        
        # Follow-up question
        response = conversation.send_message("What about its moons?")
        print("User: What about its moons?")
        print(f"Gemini: {response.text}\n")
        
        # Another follow-up
        response = conversation.send_message("How do they compare to Earth's moon?")
        print("User: How do they compare to Earth's moon?")
        print(f"Gemini: {response.text}")
    except Exception as e:
        print(f"Error in conversation: {str(e)}")

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
    print("UPDATED GEMINI API EXAMPLES")
    print("===========================")
    
    # Run examples
    text_generation_example()
    multi_turn_conversation()
    error_handling_example()
    
    print("\nAll examples completed!")
