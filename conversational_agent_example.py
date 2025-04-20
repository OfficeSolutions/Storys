"""
Conversational Agent Example using Gemini API

This script demonstrates how to use the Gemini API to create a conversational agent.
It shows how to:
1. Maintain conversation context
2. Create a specialized assistant with a specific persona
3. Handle multi-turn conversations
"""

from google import genai
import time

# Initialize the client with the provided API key
API_KEY = "AIzaSyD_TRW55r7Am5mhsKiQph9RHwyfml9WOH4"
client = genai.Client(api_key=API_KEY)

class ConversationalAgent:
    def __init__(self, persona):
        """Initialize a conversational agent with a specific persona."""
        self.model = "gemini-2.0-flash"
        self.persona = persona
        self.conversation_history = []
        self.initialize_conversation()
    
    def initialize_conversation(self):
        """Set up the initial conversation with the agent's persona."""
        self.conversation_history = [
            {"role": "system", "parts": [{"text": self.persona}]}
        ]
    
    def send_message(self, message):
        """Send a message to the agent and get a response."""
        # Add user message to conversation history
        self.conversation_history.append(
            {"role": "user", "parts": [{"text": message}]}
        )
        
        try:
            # Create a list of messages for the API call
            messages = []
            for msg in self.conversation_history:
                if msg["role"] == "system":
                    # Skip system messages as they're handled differently
                    continue
                messages.append({"role": msg["role"], "parts": msg["parts"]})
            
            # Add the system message (persona) as a prefix to the first user message
            if len(messages) > 0 and messages[0]["role"] == "user":
                system_instruction = f"{self.persona}\n\nUser message: "
                messages[0]["parts"][0]["text"] = system_instruction + messages[0]["parts"][0]["text"]
            
            # Generate response
            response = client.models.generate_content(
                model=self.model,
                contents=messages
            )
            
            # Add assistant response to conversation history
            assistant_response = response.text
            self.conversation_history.append(
                {"role": "assistant", "parts": [{"text": assistant_response}]}
            )
            
            return assistant_response
        
        except Exception as e:
            error_message = f"Error in conversation: {str(e)}"
            print(error_message)
            return error_message
    
    def get_conversation_history(self):
        """Return the conversation history in a readable format."""
        readable_history = []
        for msg in self.conversation_history:
            if msg["role"] != "system":  # Skip system messages
                role = "User" if msg["role"] == "user" else "Assistant"
                text = msg["parts"][0]["text"]
                readable_history.append(f"{role}: {text}")
        
        return "\n\n".join(readable_history)
    
    def reset_conversation(self):
        """Reset the conversation while maintaining the persona."""
        self.initialize_conversation()
        return "Conversation has been reset."

def main():
    print("GEMINI CONVERSATIONAL AGENT EXAMPLE")
    print("===================================\n")
    
    # Example 1: Travel Advisor Agent
    travel_persona = """
    You are a helpful travel advisor with expertise in international destinations.
    Your role is to provide personalized travel recommendations, tips about local customs,
    information about attractions, and help with planning itineraries.
    Be friendly, informative, and considerate of the traveler's preferences and constraints.
    """
    
    travel_agent = ConversationalAgent(travel_persona)
    
    print("=== TRAVEL ADVISOR AGENT ===")
    print("Starting conversation with a travel advisor...\n")
    
    # First user message
    user_message1 = "I'm planning a trip to Japan for 10 days in the spring. What regions should I visit?"
    print(f"User: {user_message1}")
    response1 = travel_agent.send_message(user_message1)
    print(f"Travel Advisor: {response1}\n")
    
    time.sleep(2)
    
    # Follow-up question
    user_message2 = "That sounds great! I'm particularly interested in experiencing traditional culture. What specific activities would you recommend?"
    print(f"User: {user_message2}")
    response2 = travel_agent.send_message(user_message2)
    print(f"Travel Advisor: {response2}\n")
    
    time.sleep(2)
    
    # Another follow-up
    user_message3 = "What about food? I want to try authentic Japanese cuisine but I'm vegetarian."
    print(f"User: {user_message3}")
    response3 = travel_agent.send_message(user_message3)
    print(f"Travel Advisor: {response3}\n")
    
    print("\n=== CONVERSATION HISTORY ===")
    print(travel_agent.get_conversation_history())
    
    # Example 2: Technical Support Agent
    print("\n\n=== TECHNICAL SUPPORT AGENT ===")
    tech_persona = """
    You are a technical support specialist for a software company that makes productivity tools.
    Your role is to help users troubleshoot issues, explain features, and provide step-by-step guidance.
    Be patient, clear, and thorough in your explanations, avoiding technical jargon when possible.
    """
    
    tech_agent = ConversationalAgent(tech_persona)
    print("Starting conversation with a technical support agent...\n")
    
    # First user message
    tech_message1 = "I'm having trouble with the export feature in your app. The PDF files are coming out with formatting issues."
    print(f"User: {tech_message1}")
    tech_response1 = tech_agent.send_message(tech_message1)
    print(f"Tech Support: {tech_response1}\n")
    
    time.sleep(2)
    
    # Follow-up
    tech_message2 = "I tried that but I'm still having issues. The tables in my document are split across pages."
    print(f"User: {tech_message2}")
    tech_response2 = tech_agent.send_message(tech_message2)
    print(f"Tech Support: {tech_response2}\n")
    
    print("\nConversational agent examples complete!")

if __name__ == "__main__":
    main()
