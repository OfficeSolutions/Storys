"""
Advanced Gemini API Example
This script demonstrates various capabilities of the Gemini API including:
- Text generation
- Structured output
- Parameter control
- Error handling
"""

from google import genai
import json

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

def structured_output_example():
    """Demonstrates getting structured JSON output from Gemini"""
    print("\n=== STRUCTURED OUTPUT EXAMPLE ===")
    try:
        # Request structured data about three planets
        prompt = """
        Return information about Mercury, Venus, and Earth as a JSON array.
        For each planet include: name, diameter (km), distance from sun (million km),
        and two interesting facts.
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            generation_config={
                "response_mime_type": "application/json"
            }
        )
        
        # Parse and display the JSON response
        planets_data = json.loads(response.text)
        print("Structured data received:")
        print(json.dumps(planets_data, indent=2))
    except Exception as e:
        print(f"Error in structured output: {str(e)}")

def parameter_control_example():
    """Demonstrates controlling generation parameters"""
    print("\n=== PARAMETER CONTROL EXAMPLE ===")
    try:
        # Generate with different temperature settings
        prompt = "List 5 creative uses for artificial intelligence in healthcare."
        
        print("With low temperature (more focused):")
        response_low_temp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 200
            }
        )
        print(response_low_temp.text)
        
        print("\nWith high temperature (more creative):")
        response_high_temp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            generation_config={
                "temperature": 0.9,
                "max_output_tokens": 200
            }
        )
        print(response_high_temp.text)
    except Exception as e:
        print(f"Error in parameter control: {str(e)}")

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

def list_available_models():
    """Lists all available Gemini models"""
    print("\n=== AVAILABLE MODELS ===")
    try:
        models = client.list_models()
        gemini_models = [model for model in models if "gemini" in model.name.lower()]
        
        print(f"Found {len(gemini_models)} Gemini models:")
        for model in gemini_models:
            print(f"- {model.name}")
    except Exception as e:
        print(f"Error listing models: {str(e)}")

if __name__ == "__main__":
    print("ADVANCED GEMINI API EXAMPLES")
    print("============================")
    
    # Run all examples
    list_available_models()
    text_generation_example()
    structured_output_example()
    parameter_control_example()
    error_handling_example()
    
    print("\nAll examples completed!")
