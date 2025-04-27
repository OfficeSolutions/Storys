import os
import requests
import json
import tempfile
import base64
from io import BytesIO
from PIL import Image

def generate_story(child_name, image_data, theme, age_range="4-6", generate_illustrations=False):
    """Generate a personalized story based on the child's name, image, and theme using OpenAI."""
    try:
        # Get API key from environment variable
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Determine story complexity based on age range
        if age_range == "2-4":
            complexity = "very simple with short sentences, basic vocabulary, and a straightforward plot. Length should be around 800-1000 words."
            reading_level = "toddlers and preschoolers (2-4 years old)"
        elif age_range == "4-6":
            complexity = "simple but engaging with slightly longer sentences and a clear plot. Length should be around 1000-1500 words."
            reading_level = "kindergarteners (4-6 years old)"
        elif age_range == "6-8":
            complexity = "moderately complex with varied sentence structures, richer vocabulary, and a more developed plot. Length should be around 1500-2000 words."
            reading_level = "early elementary school children (6-8 years old)"
        else:  # 8-10
            complexity = "more complex with longer paragraphs, advanced vocabulary, and a multi-layered plot. Length should be around 2000-2500 words."
            reading_level = "older elementary school children (8-10 years old)"
        
        # Analyze the image to extract details about the child
        child_description = analyze_image(image_data, api_key)
        
        # Create a prompt for the story
        prompt = f"""
        Create a personalized bedtime story for a child named {child_name}. 
        The story should be in the {theme} theme and should be appropriate for {reading_level}.
        
        The story should be {complexity}
        
        Make the child the main character of the story. The child looks like this: {child_description}
        Incorporate these visual details about the child throughout the story to make it more personalized.
        
        The story should have a clear beginning, middle, and end, with a positive message or lesson.
        
        {"Include 4-6 places in the story where illustrations would be appropriate. Mark these with [ILLUSTRATION: brief description of the illustration]. Make the illustrations descriptions detailed and specific to the story, and include the child's visual characteristics in each illustration description." if generate_illustrations else ""}
        
        Make the story engaging, imaginative, and appropriate for the age range.
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
                    "content": f"You are a creative children's story writer specializing in stories for {reading_level}. Create engaging, age-appropriate stories that feature the child as the main character. Incorporate details from the child's appearance in the image."
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
            ],
            "max_tokens": 4000
        }
        
        # Make the API request
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=120  # Increased timeout for longer stories
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
        
        # Adjust fallback story length based on age range
        if age_range == "2-4":
            story_length = "short"
        elif age_range == "4-6":
            story_length = "medium-length"
        elif age_range == "6-8":
            story_length = "longer"
        else:  # 8-10
            story_length = "elaborate"
            
        return f"""
        # {child_name}'s {theme.title()} Adventure

        Once upon a time, there was a child named {child_name} who loved {theme} adventures.
        
        One day, {child_name} discovered a magical door that led to a world of {theme}.
        
        {"[ILLUSTRATION: A child with features similar to the uploaded photo, standing in front of a magical glowing door that leads to a " + theme + " world]" if generate_illustrations else ""}
        
        In this world, {child_name} met friendly creatures who became their guides.
        
        {"[ILLUSTRATION: " + child_name + " meeting colorful, friendly creatures in a fantastical " + theme + " landscape with amazing details]" if generate_illustrations else ""}
        
        {child_name} embarked on a {story_length} journey through mountains, valleys, and mysterious forests.
        
        {"[ILLUSTRATION: An overhead view of " + child_name + " traveling through a varied landscape with mountains, valleys, and a mysterious forest]" if generate_illustrations else ""}
        
        After many exciting adventures, {child_name} learned the importance of courage and friendship.
        
        {"[ILLUSTRATION: " + child_name + " standing bravely with new friends, facing a challenge together in the " + theme + " world]" if generate_illustrations else ""}
        
        When {child_name} returned home, they couldn't wait to share their amazing story with everyone.
        
        {"[ILLUSTRATION: " + child_name + " back at home, excitedly telling their story to family members who listen with wonder]" if generate_illustrations else ""}
        
        The End.
        """

def analyze_image(image_data, api_key):
    """Analyze the image to extract details about the child."""
    try:
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
                    "content": "You are an assistant that analyzes images of children to provide detailed descriptions for story personalization. Focus on visual details like hair color, hair style, eye color, clothing, and any distinctive features. Be specific but respectful and appropriate."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please describe this child in detail for a personalized story. Include hair color, hair style, eye color, clothing colors, and any distinctive features. Be specific but appropriate."
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
            timeout=30
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            description = response_data["choices"][0]["message"]["content"]
            return description
        else:
            print(f"Error analyzing image: {response.status_code}")
            print(response.text)
            return "a young child with a bright smile"
            
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return "a young child with a bright smile"

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
            
            # Try with DALL-E 2 as a fallback
            try:
                # Set up the data for the API request with DALL-E 2
                data = {
                    "model": "dall-e-2",
                    "prompt": prompt,
                    "n": 1,
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
                    print(f"Error generating illustration with DALL-E 2: {response.status_code}")
                    print(response.text)
            except Exception as e:
                print(f"Error with DALL-E 2 fallback: {str(e)}")
            
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
