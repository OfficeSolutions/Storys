import os
import requests
import json
import tempfile
import base64
from io import BytesIO
from PIL import Image

def generate_story(child_name, image_data, theme, generate_illustrations=False):
    """Generate a personalized story based on the child's name, image, and theme using OpenAI."""
    try:
        # Get API key from environment variable
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Create a prompt for the story
        prompt = f"""
        Create a personalized bedtime story for a child named {child_name}. 
        The story should be in the {theme} theme and should be appropriate for a young child.
        The story should be about 500-800 words long and should be divided into paragraphs.
        
        Make the child the main character of the story.
        
        The story should have a clear beginning, middle, and end, with a positive message or lesson.
        
        {"Include 3-5 places in the story where illustrations would be appropriate. Mark these with [ILLUSTRATION: brief description of the illustration]." if generate_illustrations else ""}
        """
        
        # Set up the headers for the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Set up the data for the API request
        data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a creative children's story writer. Create engaging, age-appropriate stories that feature the child as the main character."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]
        }
        
        # Make the API request
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=60
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            story = response_data["choices"][0]["message"]["content"]
            return story
        else:
            print(f"Error generating story: {response.status_code}")
            print(response.text)
            raise Exception(f"Error generating story: {response.status_code}")
            
    except Exception as e:
        # Fallback to a simple story if the API fails
        print(f"Error generating story: {str(e)}")
        return f"""
        # {child_name}'s {theme.title()} Adventure

        Once upon a time, there was a child named {child_name} who loved {theme} adventures.
        
        One day, {child_name} discovered a magical door that led to a world of {theme}.
        
        {"[ILLUSTRATION: A child standing in front of a magical glowing door]" if generate_illustrations else ""}
        
        In this world, {child_name} met friendly creatures who became their guides.
        
        {"[ILLUSTRATION: The child meeting magical creatures in a fantastical landscape]" if generate_illustrations else ""}
        
        After many exciting adventures, {child_name} learned the importance of courage and friendship.
        
        {"[ILLUSTRATION: The child waving goodbye to their new friends as they return home]" if generate_illustrations else ""}
        
        When {child_name} returned home, they couldn't wait to share their amazing story with everyone.
        
        The End.
        """

def generate_illustration(description, theme):
    """Generate an illustration based on the description using OpenAI's gpt-image-1 model in low quality mode."""
    try:
        # Get API key from environment variable
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Create a prompt for the illustration
        prompt = f"A children's book illustration of {description}. Theme: {theme}. Style: colorful, whimsical, appropriate for children ages 4-8."
        
        # Set up the headers for the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Set up the data for the API request
        data = {
            "model": "gpt-image-1",
            "prompt": prompt,
            "n": 1,
            "quality": "low",
            "size": "1024x1024"
        }
        
        # Make the API request
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            
            # Get the image URL
            if "data" in response_data and len(response_data["data"]) > 0 and "url" in response_data["data"][0]:
                image_url = response_data["data"][0]["url"]
                
                # Download the image
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    # Save the image to a temporary file
                    image = Image.open(BytesIO(img_response.content))
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                    image.save(temp_file.name)
                    temp_file.close()
                    
                    return temp_file.name
                else:
                    print(f"Error downloading image: {img_response.status_code}")
            else:
                print("No image URL found in the response")
        else:
            print(f"Error generating illustration: {response.status_code}")
            print(response.text)
            
        return None
    except Exception as e:
        print(f"Error generating illustration: {str(e)}")
        return None

def extract_illustration_descriptions(story):
    """Extract illustration descriptions from the story."""
    import re
    
    # Find all illustration descriptions in the story
    pattern = r'\[ILLUSTRATION: (.*?)\]'
    matches = re.findall(pattern, story)
    
    return matches
