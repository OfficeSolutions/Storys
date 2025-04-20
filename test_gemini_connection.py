from google import genai

# Initialize the client with the provided API key
API_KEY = "AIzaSyD_TRW55r7Am5mhsKiQph9RHwyfml9WOH4"
client = genai.Client(api_key=API_KEY)

# Simple test to verify connection
try:
    # Make a simple request to test the connection
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents="Hello, can you confirm this connection is working?"
    )
    print("Connection successful!")
    print("Response from Gemini API:")
    print(response.text)
except Exception as e:
    print("Connection failed with error:")
    print(str(e))
