import os
import requests
import json
import tempfile
import base64
import time
import random
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

# Global variables to store child description and appearance details for consistent illustrations
child_character_description = None
child_appearance_details = {}

def _create_placeholder_image(text, error=False):
    """Helper function to create a placeholder image with text."""
    try:
        # Use persistent directory instead of temp directory
        # Ensure text is converted to string before hashing
        filename = f"placeholder_{hash(str(text))}.jpg"
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
        wrapped_text = textwrap.fill(str(text), width=40)

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
    global child_character_description, child_appearance_details
    
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
        
        # Store the child description globally for consistent illustrations
        child_character_description = child_description
        
        # Extract and store specific appearance details for stronger consistency
        extract_appearance_details(child_description)

        rhyming_instruction = "The story should be written in rhyming verse, with a consistent rhythm and rhyme scheme appropriate for a bedtime story." if rhyming else ""
        
        # Modified to create a single scene description for the story image
        illustration_instruction = "Include ONE vivid scene description that captures the essence of the story. Mark this with [STORY_SCENE: detailed description of the scene]. This scene should include the child character and represent the main theme or climax of the story." if generate_illustrations else ""

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
        
        # Modified to include a single scene description
        scene_description = f"[STORY_SCENE: {child_name} standing in a magical {theme} landscape with glowing lights, surrounded by friendly creatures. The scene captures the wonder in {child_name}'s eyes as they discover the magic of this new world.]"
        
        fallback_story = f"""
        # {child_name}'s {theme.title()} Adventure
        
        Once upon a time, there was a child named {child_name} who loved {theme} adventures.
        One day, {child_name} discovered a magical door that led to a world of {theme}.
        
        In this world, {child_name} met friendly creatures who became their guides.
        {child_name} embarked on a {story_length} journey through mountains, valleys, and mysterious forests.
        
        After many exciting adventures, {child_name} learned the importance of courage and friendship.
        When {child_name} returned home, they couldn't wait to share their amazing story with everyone.
        
        {scene_description}
        
        The End.
        """
        return fallback_story

def extract_appearance_details(description):
    """Extract specific appearance details from the child description for stronger consistency."""
    global child_appearance_details
    
    try:
        logger.info("Extracting specific appearance details for consistency")
        
        # Reset appearance details
        child_appearance_details = {
            "hair_color": "unknown",
            "hair_style": "unknown",
            "eye_color": "unknown",
            "skin_tone": "unknown",
            "clothing": "unknown",
            "distinctive_features": "unknown"
        }
        
        # Extract hair color
        hair_color_patterns = [
            r"(blonde|blond|brown|black|red|auburn|ginger|gray|white) hair",
            r"hair is (blonde|blond|brown|black|red|auburn|ginger|gray|white)",
            r"(blonde|blond|brown|black|red|auburn|ginger|gray|white)-haired"
        ]
        
        for pattern in hair_color_patterns:
            import re
            match = re.search(pattern, description.lower())
            if match:
                child_appearance_details["hair_color"] = match.group(1)
                break
        
        # Extract hair style
        hair_style_patterns = [
            r"(curly|wavy|straight|short|long|medium-length|braided|ponytail|pigtails) hair",
            r"hair is (curly|wavy|straight|short|long|medium-length|braided|in a ponytail|in pigtails)"
        ]
        
        for pattern in hair_style_patterns:
            match = re.search(pattern, description.lower())
            if match:
                child_appearance_details["hair_style"] = match.group(1)
                break
        
        # Extract eye color
        eye_color_patterns = [
            r"(blue|green|brown|hazel|gray|amber) eyes",
            r"eyes are (blue|green|brown|hazel|gray|amber)"
        ]
        
        for pattern in eye_color_patterns:
            match = re.search(pattern, description.lower())
            if match:
                child_appearance_details["eye_color"] = match.group(1)
                break
        
        # Extract skin tone
        skin_tone_patterns = [
            r"(fair|light|pale|tan|medium|olive|brown|dark) skin",
            r"skin is (fair|light|pale|tan|medium|olive|brown|dark)"
        ]
        
        for pattern in skin_tone_patterns:
            match = re.search(pattern, description.lower())
            if match:
                child_appearance_details["skin_tone"] = match.group(1)
                break
        
        # Extract clothing (more complex, just look for clothing-related sentences)
        clothing_patterns = [
            r"wearing ([^\.]+)",
            r"dressed in ([^\.]+)"
        ]
        
        for pattern in clothing_patterns:
            match = re.search(pattern, description.lower())
            if match:
                child_appearance_details["clothing"] = match.group(1)
                break
        
        # Log the extracted details
        logger.info(f"Extracted appearance details: {json.dumps(child_appearance_details)}")
        
    except Exception as e:
        logger.error(f"Error extracting appearance details: {str(e)}")
        # Keep default values if extraction fails

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

def extract_story_scene(story_text):
    """Extract the story scene description from the story text."""
    try:
        logger.info("Extracting story scene description")
        scene_marker = story_text.split("[STORY_SCENE:")
        
        if len(scene_marker) > 1:
            # Split the marker into description and remaining text
            parts = scene_marker[1].split("]", 1)
            if len(parts) > 0:
                description = parts[0].strip()
                logger.info(f"Extracted story scene description: {description[:50]}...")
                return description
        
        # If no scene marker found, create a generic description
        logger.warning("No story scene marker found, using generic description")
        return "A magical scene from the story with the child as the main character"
    except Exception as e:
        logger.error(f"Error extracting story scene: {str(e)}")
        return "A magical scene from the story with the child as the main character"

def generate_story_image(story_text, api_key):
    """Generate a single high-quality image for the entire story with text overlay."""
    global child_character_description, child_appearance_details
    
    try:
        logger.info("Generating single high-quality story image")
        
        # Extract the scene description from the story
        scene_description = extract_story_scene(story_text)
        
        # Implement exponential backoff for rate limiting
        max_retries = 5
        base_delay = 2  # Start with a 2-second delay
        
        for attempt in range(max_retries):
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                
                # Use the global child description for consistency
                character_desc = child_character_description or "a young child"
                
                # Build a detailed appearance specification for absolute consistency
                appearance_spec = ""
                if child_appearance_details:
                    appearance_items = []
                    for key, value in child_appearance_details.items():
                        if value != "unknown":
                            if key == "hair_color":
                                appearance_items.append(f"EXACTLY {value} hair color")
                            elif key == "hair_style":
                                appearance_items.append(f"EXACTLY {value} hair style")
                            elif key == "eye_color":
                                appearance_items.append(f"EXACTLY {value} eye color")
                            elif key == "skin_tone":
                                appearance_items.append(f"EXACTLY {value} skin tone")
                            elif key == "clothing":
                                appearance_items.append(f"EXACTLY the same clothing: {value}")
                            elif key == "distinctive_features" and value != "unknown":
                                appearance_items.append(f"EXACTLY the same distinctive features: {value}")
                    
                    if appearance_items:
                        appearance_spec = "CRITICAL CHARACTER CONSISTENCY REQUIREMENTS:\n" + "\n".join(appearance_items)
                
                # Enhanced prompt for high-quality story image
                enhanced_prompt = f"""A high-quality children's book illustration showing: {scene_description}

Full character description: {character_desc}

{appearance_spec}

The illustration style MUST be:
- Colorful and whimsical
- Child-friendly with soft edges and warm colors
- Clear, detailed, and appropriate for a bedtime story
- In the style of classic children's book illustrations with modern aesthetics
- High quality with good composition and lighting
- Suitable for text overlay

Create a beautiful, engaging scene that captures the essence of the story.
"""
                
                data = {
                    "model": "gpt-image-1",
                    "prompt": enhanced_prompt,
                    "n": 1,
                    "quality": "high",  # Using high quality for the single story image
                    "size": "1536x1024"  # Using a supported wide format for better text overlay
                }
                
                # Add delay between requests to avoid rate limiting
                if attempt > 0:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Rate limit retry {attempt+1}/{max_retries}, waiting {delay:.2f} seconds")
                    time.sleep(delay)
                else:
                    # Small delay even on first attempt to space out requests
                    time.sleep(base_delay)
                
                logger.info("Sending story image generation request to OpenAI API")
                response = requests.post(
                    "https://api.openai.com/v1/images/generations",
                    headers=headers,
                    data=json.dumps(data),
                    timeout=60
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
                                continue  # Try again
                        elif "url" in image_info:
                            image_url = image_info["url"]
                            img_response = requests.get(image_url)
                            if img_response.status_code == 200:
                                image_bytes = img_response.content
                            else:
                                logger.error(f"Error downloading story image: {img_response.status_code}")
                                continue  # Try again
                        
                        if image_bytes:
                            try:
                                image = Image.open(BytesIO(image_bytes))
                                
                                # Add story text overlay
                                image_with_text = add_full_story_overlay(image, story_text)
                                
                                # Save to persistent directory with unique filename
                                timestamp = str(time.time())
                                unique_hash = hash(str(scene_description) + timestamp)
                                filename = f"story_image_{unique_hash}.jpg"
                                image_path = os.path.join(PERSISTENT_IMAGE_DIR, filename)
                                image_with_text.save(image_path, quality=95)  # High quality save
                                
                                logger.info(f"Successfully generated story image: {image_path}")
                                return image_path
                            except Exception as save_err:
                                logger.error(f"Error saving generated story image: {save_err}")
                                continue  # Try again
                        else:
                            logger.error("No image data found in the response")
                            continue  # Try again
                    else:
                        logger.error("No data found in the image generation response")
                        continue  # Try again
                
                elif response.status_code == 429:  # Rate limit error
                    response_data = response.json()
                    error_message = response_data.get("error", {}).get("message", "Rate limit exceeded")
                    logger.warning(f"Rate limit error: {error_message}")
                    
                    # Extract wait time if available in the error message
                    import re
                    wait_time_match = re.search(r"after (\d+\.?\d*) seconds", error_message)
                    if wait_time_match:
                        wait_time = float(wait_time_match.group(1)) + 1  # Add a buffer second
                        logger.info(f"Rate limit retry {attempt+1}/{max_retries}, waiting {wait_time} seconds")
                        time.sleep(wait_time)
                    
                    continue  # Try again after waiting
                
                else:
                    logger.error(f"Error generating story image: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    
                    # If it's not a rate limit error, don't retry
                    if response.status_code != 429:
                        break
            
            except Exception as request_err:
                logger.error(f"Request error on attempt {attempt+1}: {str(request_err)}")
                time.sleep(base_delay * (2 ** attempt))  # Exponential backoff
        
        # If we've exhausted all retries or encountered a non-retryable error
        logger.error(f"Failed to generate story image after {max_retries} attempts")
        return _create_placeholder_image("Failed to generate story image. Please try again later.", error=True)
        
    except Exception as e:
        logger.error(f"Error generating story image: {str(e)}")
        return _create_placeholder_image(f"Error generating story image: {str(e)}", error=True)

def add_full_story_overlay(image, story_text):
    """Add full story text overlay to the image."""
    try:
        logger.info("Adding full story text overlay")
        
        # Create a copy of the image to avoid modifying the original
        img_with_text = image.copy()
        draw = ImageDraw.Draw(img_with_text)
        
        # Get image dimensions
        width, height = img_with_text.size
        
        # Attempt to load fonts, fallback to default if not found
        try:
            title_font_size = 48
            body_font_size = 24
            
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", title_font_size)
            body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", body_font_size)
        except IOError:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
        
        # Extract title and body from story text
        title = ""
        body = story_text
        
        # Look for markdown title format
        lines = story_text.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('# '):
                title = line.replace('# ', '')
                body = '\n'.join(lines[i+1:])
                break
        
        # If no markdown title found, try to extract first line as title
        if not title and lines:
            title = lines[0]
            body = '\n'.join(lines[1:])
        
        # Clean up the story text - remove the scene description marker
        body = re.sub(r'\[STORY_SCENE:.*?\]', '', body)
        
        # Create semi-transparent gradient overlay for the entire image
        gradient = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw_gradient = ImageDraw.Draw(gradient)
        
        # Draw a gradient from transparent to semi-transparent black
        for y in range(height):
            # Calculate alpha based on position
            # More transparent at the top, more opaque at the bottom
            alpha = int(180 * (y / height))
            draw_gradient.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
        
        # Apply the gradient overlay
        img_with_text = Image.alpha_composite(img_with_text.convert('RGBA'), gradient)
        draw = ImageDraw.Draw(img_with_text)
        
        # Draw title at the top
        if title:
            # Wrap title text
            title_max_width = width - 100  # 50px padding on each side
            wrapped_title = textwrap.fill(title, width=40)
            
            # Calculate title position (centered horizontally, at the top with padding)
            title_bbox = draw.textbbox((0, 0), wrapped_title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
            title_position = ((width - title_width) // 2, 30)
            
            # Draw title with subtle shadow for better readability
            draw.text((title_position[0]+2, title_position[1]+2), wrapped_title, fill=(0, 0, 0, 200), font=title_font)
            draw.text(title_position, wrapped_title, fill=(255, 255, 255), font=title_font)
        
        # Prepare body text
        # Wrap body text
        body_max_width = width - 100  # 50px padding on each side
        wrapped_body = textwrap.fill(body, width=80)
        
        # Calculate body text position
        body_y_position = height // 2  # Start in the middle of the image
        
        # Draw body text with scrollable effect
        lines = wrapped_body.split('\n')
        line_height = body_font_size + 8  # Add some line spacing
        
        # Limit the number of lines to fit in the image
        max_lines = (height - body_y_position - 50) // line_height
        if len(lines) > max_lines:
            lines = lines[:max_lines-1] + ["... (Story continues)"]
        
        for i, line in enumerate(lines):
            y_pos = body_y_position + (i * line_height)
            # Draw text with subtle shadow for better readability
            draw.text((52, y_pos+2), line, fill=(0, 0, 0, 200), font=body_font)
            draw.text((50, y_pos), line, fill=(255, 255, 255), font=body_font)
        
        logger.info("Successfully added full story text overlay")
        return img_with_text.convert('RGB')  # Convert back to RGB for saving as JPG
        
    except Exception as e:
        logger.error(f"Error adding full story text overlay: {str(e)}")
        # Return the original image if overlay fails
        return image
