import os
import requests
import json
import tempfile
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import logging
import textwrap

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Create a persistent directory for storing images
PERSISTENT_IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "images")
os.makedirs(PERSISTENT_IMAGE_DIR, exist_ok=True)
logger.info(f"Using persistent image directory: {PERSISTENT_IMAGE_DIR}")

def _create_placeholder_image(text, error=False):
    """Helper function to create a placeholder image with text."""
    try:
        # Use persistent directory instead of temp directory
        filename = f"placeholder_{hash(text)}.jpg"
        placeholder_path = os.path.join(PERSISTENT_IMAGE_DIR, filename)
        
        img = Image.new("RGB", (1024, 1024), color=(240, 240, 240) if not error else (255, 200, 200))
        d = ImageDraw.Draw(img)

        # Attempt to load a font, fallback to default if not found
        try:
            # Using a common font path, adjust if needed
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except IOError:
            font = ImageFont.load_default()

        # Wrap text
        wrapped_text = textwrap.fill(text, width=40)

        # Calculate text position (centered)
        text_bbox = d.textbbox((0, 0), wrapped_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((1024 - text_width) / 2, (1024 - text_height) / 2)

        # Draw the text
        d.text(position, wrapped_text, fill=(0, 0, 0), font=font)
        img.save(placeholder_path)
        logger.info(f"Created placeholder image: {placeholder_path}")
        return placeholder_path
    except Exception as e:
        logger.error(f"Failed to create placeholder image: {str(e)}")
        # Return a path to a minimal fallback if even placeholder creation fails
        return None # Or path to a static error image asset

def generate_story(child_name, image_data, theme, age_range="4-6", generate_illustrations=False, rhyming=False):
    """Generate a personalized story based on the child's name, image, and theme using OpenAI."""
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            raise ValueError("OPENAI_API_KEY environment variable not set")

        if age_range == "2-4":
            complexity = "extremely simple with very short sentences (3-5 words), basic everyday vocabulary (e.g., common nouns and verbs), and a very straightforward, linear plot with minimal characters. Focus on repetition and clear actions. Length should be around 300-500 words."
            reading_level = "toddlers and preschoolers (2-4 years old)"
        elif age_range == "4-6":
            complexity = "simple and engaging, with clear, concise sentences (5-8 words), common vocabulary suitable for young children, and a straightforward plot. Focus on clear actions and a positive message. Length should be around 500-800 words."
            reading_level = "kindergarteners (4-6 years old)"
        elif age_range == "6-8":
            complexity = "moderately complex with varied sentence structures, richer vocabulary, and a more developed plot. Length should be around 800-1200 words."
            reading_level = "early elementary school children (6-8 years old)"
        else:  # 8-10
            complexity = "more complex with longer paragraphs, advanced vocabulary, and a multi-layered plot. Length should be around 1200-1500 words."
            reading_level = "older elementary school children (8-10 years old)"

        child_description = analyze_image(image_data, api_key)
        logger.info(f"Child description: {child_description[:100]}...")

        rhyming_instruction = "The story should be written in rhyming verse, with a consistent rhythm and rhyme scheme appropriate for a bedtime story." if rhyming else ""
        illustration_instruction = "Include 4-6 places in the story where illustrations would be appropriate. Mark these with [ILLUSTRATION: brief description of the illustration]. Make the illustrations descriptions detailed and specific to the story, and include the child's visual characteristics in each illustration description." if generate_illustrations else ""

        prompt = f"""
        Create a personalized bedtime story for a child named {child_name}.
        The story should be in the {theme} theme and should be appropriate for {reading_level}.
        The story should be {complexity}
        {rhyming_instruction}
        Make the child the main character of the story. The child looks like this: {child_description}
        Incorporate these visual details about the child throughout the story to make it more personalized.
        The story should have a clear beginning, middle, and end, with a positive message or lesson.
        {illustration_instruction}
        Make the story engaging, imaginative, and appropriate for the age range.
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        data = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a creative children's story writer specializing in stories for {reading_level}. Create engaging, age-appropriate stories that feature the child as the main character. Incorporate details from the child's appearance in the image. {rhyming_instruction}"
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                }
            ],
            "max_tokens": 4000
        }

        logger.info(f"Sending story generation request to OpenAI API")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=120
        )

        if response.status_code == 200:
            response_data = response.json()
            story = response_data["choices"][0]["message"]["content"]
            logger.info(f"Successfully generated story of length {len(story)}")
            return story
        else:
            logger.error(f"Error generating story: {response.status_code}")
            logger.error(f"Response: {response.text}")
            raise Exception(f"Error generating story: {response.status_code}")

    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        # Fallback story generation logic remains the same...
        if age_range == "2-4": story_length = "short"
        elif age_range == "4-6": story_length = "medium-length"
        elif age_range == "6-8": story_length = "longer"
        else: story_length = "elaborate"
        fallback_illustrations = []
        if generate_illustrations:
            fallback_illustrations.append("[ILLUSTRATION: A child with features similar to the uploaded photo, standing in front of a magical glowing door that leads to a " + theme + " world]")
            fallback_illustrations.append("[ILLUSTRATION: " + child_name + " meeting colorful, friendly creatures in a fantastical " + theme + " landscape with amazing details]")
            fallback_illustrations.append("[ILLUSTRATION: An overhead view of " + child_name + " traveling through a varied landscape with mountains, valleys, and a mysterious forest]")
            fallback_illustrations.append("[ILLUSTRATION: " + child_name + " standing bravely with new friends, facing a challenge together in the " + theme + " world]")
            fallback_illustrations.append("[ILLUSTRATION: " + child_name + " back at home, excitedly telling their story to family members who listen with wonder]")
        fallback_story = f"""
        # {child_name}'s {theme.title()} Adventure
        Once upon a time, there was a child named {child_name} who loved {theme} adventures.
        One day, {child_name} discovered a magical door that led to a world of {theme}.
        {fallback_illustrations[0] if len(fallback_illustrations) > 0 else ''}
        In this world, {child_name} met friendly creatures who became their guides.
        {fallback_illustrations[1] if len(fallback_illustrations) > 1 else ''}
        {child_name} embarked on a {story_length} journey through mountains, valleys, and mysterious forests.
        {fallback_illustrations[2] if len(fallback_illustrations) > 2 else ''}
        After many exciting adventures, {child_name} learned the importance of courage and friendship.
        {fallback_illustrations[3] if len(fallback_illustrations) > 3 else ''}
        When {child_name} returned home, they couldn't wait to share their amazing story with everyone.
        {fallback_illustrations[4] if len(fallback_illustrations) > 4 else ''}
        The End.
        """
        return fallback_story

def analyze_image(image_data, api_key):
    """Analyze the image to extract details about the child."""
    try:
        logger.info("Analyzing uploaded image")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an assistant that analyzes images of children to provide detailed descriptions for story personalization. Focus on visual details like hair color, hair style, eye color, clothing, and any distinctive features. Be specific but respectful and appropriate."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Please describe this child in detail for a personalized story. Include hair color, hair style, eye color, clothing colors, and any distinctive features. Be specific but appropriate."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                }
            ]
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        if response.status_code == 200:
            response_data = response.json()
            description = response_data["choices"][0]["message"]["content"]
            logger.info("Successfully analyzed image")
            return description
        else:
            logger.error(f"Error analyzing image: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return "a young child with a bright smile"
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return "a young child with a bright smile"

def generate_ghibli_style_image(image_data, api_key):
    """Generate a Studio Ghibli style image based on the uploaded photo."""
    try:
        logger.info("Generating Ghibli-style main image")
        child_description = analyze_image(image_data, api_key)
        prompt = f"A heartwarming Studio Ghibli style illustration suitable for a children's book cover. The scene features a child character inspired by the following description: {child_description}. Emphasize a magical, whimsical atmosphere with soft colors, enchanting details, and a sense of gentle wonder. Ensure the depiction is innocent and universally appealing."
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": "gpt-image-1", # Using the specific model as requested
            "prompt": prompt,
            "n": 1,
            "quality": "low", # Using low quality as requested
            "size": "1024x1024"
        }
        logger.info("Sending Ghibli image generation request to OpenAI API (gpt-image-1)")
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        if response.status_code == 200:
            response_data = response.json()
            logger.info(f"Ghibli image generation API response: {json.dumps(response_data)}")
            if "data" in response_data and len(response_data["data"]) > 0:
                image_info = response_data["data"][0]
                image_bytes = None
                if "b64_json" in image_info:
                    logger.info("Decoding Ghibli image from base64 data.")
                    try:
                        image_bytes = base64.b64decode(image_info["b64_json"])
                    except Exception as decode_err:
                        logger.error(f"Error decoding base64 image: {decode_err}")
                        return _create_placeholder_image("Failed to decode Ghibli-style image data.", error=True)
                elif "url" in image_info: # Fallback if API changes
                    image_url = image_info["url"]
                    logger.info(f"Downloading Ghibli image from URL: {image_url}")
                    img_response = requests.get(image_url)
                    if img_response.status_code == 200:
                        image_bytes = img_response.content
                    else:
                        logger.error(f"Error downloading Ghibli image: {img_response.status_code}")
                        return _create_placeholder_image("Failed to download Ghibli-style image.", error=True)

                if image_bytes:
                    try:
                        image = Image.open(BytesIO(image_bytes))
                        # Save to persistent directory instead of temp file
                        filename = f"ghibli_{hash(prompt)}.jpg"
                        image_path = os.path.join(PERSISTENT_IMAGE_DIR, filename)
                        image.save(image_path)
                        logger.info(f"Successfully generated Ghibli-style image: {image_path}")
                        return image_path
                    except Exception as save_err:
                        logger.error(f"Error saving generated Ghibli image: {save_err}")
                        return _create_placeholder_image("Failed to save generated Ghibli-style image.", error=True)
                else:
                    logger.error("No image URL or base64 data found in the response item.")
                    return _create_placeholder_image("Ghibli-style image generation failed (No data). Check logs.", error=True)
            else:
                logger.error("No data found in the image generation response")
                if response_data.get("error"):
                     logger.error(f"API Error in response: {response_data['error']}")
                return _create_placeholder_image("Ghibli-style image generation failed (No data/URL). Check logs.", error=True)
        else:
            logger.error(f"Error generating Ghibli image: {response.status_code}")
            logger.error(f"Response: {response.text}")
            placeholder_text = f"Ghibli-style image generation failed (HTTP {response.status_code}). The original image will be used."
            try:
                response_data = response.json()
                error_message_from_api = response_data.get("error", {}).get("message", "")
                if "safety system" in error_message_from_api.lower():
                    logger.warning(f"Ghibli image rejected by safety system: {error_message_from_api}")
                    placeholder_text = "The Ghibli-style image was not created due to content safety guidelines. The original image will be used instead."
            except json.JSONDecodeError:
                logger.warning("Could not parse JSON from error response for Ghibli image.")
            return _create_placeholder_image(placeholder_text, error=True)
    except Exception as e:
        logger.error(f"Error generating Ghibli image: {str(e)}")
        return _create_placeholder_image(f"Error generating Ghibli-style image: {str(e)}", error=True)

def extract_illustration_descriptions(story_text):
    """Extract illustration descriptions from the story text."""
    try:
        logger.info("Extracting illustration descriptions from story")
        illustration_markers = story_text.split("[ILLUSTRATION:")
        descriptions = []
        for i, marker in enumerate(illustration_markers):
            if i == 0:  # Skip the first part (before any illustration marker)
                continue
            try:
                description = marker.split("]")[0].strip()
                descriptions.append(description)
            except IndexError:
                logger.warning(f"Malformed illustration marker: {marker[:50]}...")
        logger.info(f"Extracted {len(descriptions)} illustration descriptions")
        return descriptions
    except Exception as e:
        logger.error(f"Error extracting illustration descriptions: {str(e)}")
        return []

def generate_illustration(description, api_key):
    """Generate an illustration based on the description."""
    try:
        logger.info(f"Generating illustration for: {description[:50]}...")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Enhance the prompt for better results
        enhanced_prompt = f"A children's book illustration showing {description}. The style is colorful, whimsical, and appealing to children. The illustration is clear, detailed, and appropriate for a bedtime story."
        
        data = {
            "model": "gpt-image-1", # Using the specific model as requested
            "prompt": enhanced_prompt,
            "n": 1,
            "quality": "low", # Using low quality as requested
            "size": "1024x1024"
        }
        
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if "data" in response_data and len(response_data["data"]) > 0:
                image_info = response_data["data"][0]
                image_bytes = None
                
                if "b64_json" in image_info:
                    try:
                        image_bytes = base64.b64decode(image_info["b64_json"])
                    except Exception as decode_err:
                        logger.error(f"Error decoding base64 image: {decode_err}")
                        return None
                elif "url" in image_info:
                    image_url = image_info["url"]
                    img_response = requests.get(image_url)
                    if img_response.status_code == 200:
                        image_bytes = img_response.content
                    else:
                        logger.error(f"Error downloading illustration: {img_response.status_code}")
                        return None
                
                if image_bytes:
                    try:
                        image = Image.open(BytesIO(image_bytes))
                        # Save to persistent directory instead of temp file
                        filename = f"illustration_{hash(description)}.jpg"
                        image_path = os.path.join(PERSISTENT_IMAGE_DIR, filename)
                        image.save(image_path)
                        logger.info(f"Successfully generated illustration: {image_path}")
                        return image_path
                    except Exception as save_err:
                        logger.error(f"Error saving generated illustration: {save_err}")
                        return None
                else:
                    logger.error("No image data found in the response")
                    return None
            else:
                logger.error("No data found in the image generation response")
                return None
        else:
            logger.error(f"Error generating illustration: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error generating illustration: {str(e)}")
        return None
