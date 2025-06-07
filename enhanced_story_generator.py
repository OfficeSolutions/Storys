import os
import requests
import json
import base64
import re
import time
import random
import logging
import textwrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants
PERSISTENT_IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "images")
os.makedirs(PERSISTENT_IMAGE_DIR, exist_ok=True)

# Global variables to store character appearance details for consistency
child_character_description = None
child_appearance_details = {}

def extract_appearance_details(image_data, api_key):
    """Extract appearance details from the child's image."""
    global child_character_description, child_appearance_details
    
    if child_character_description and child_appearance_details:
        logger.info("Using cached appearance details")
        return child_character_description, child_appearance_details
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Prepare the prompt for appearance extraction
        prompt = """Analyze this child's image and describe their appearance in detail. 
        Focus on these specific attributes:
        1. Hair color (be specific, e.g., "light brown" not just "brown")
        2. Hair style (e.g., "short curly", "long straight", "pigtails")
        3. Eye color (be specific)
        4. Skin tone (be specific)
        5. Clothing (describe what they're wearing)
        6. Any distinctive features (glasses, freckles, etc.)
        
        Format your response as a JSON object with these keys: 
        hair_color, hair_style, eye_color, skin_tone, clothing, distinctive_features
        
        If you cannot determine any attribute, use "unknown" as the value.
        """
        
        data = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            content = response_data["choices"][0]["message"]["content"]
            
            # Extract JSON from the response
            json_match = re.search(r'({.*})', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                appearance = json.loads(json_str)
                
                # Create a detailed description
                description_parts = []
                
                if appearance.get("hair_color", "unknown") != "unknown":
                    description_parts.append(f"{appearance.get('hair_color')} hair")
                
                if appearance.get("hair_style", "unknown") != "unknown":
                    description_parts.append(f"{appearance.get('hair_style')} hairstyle")
                
                if appearance.get("eye_color", "unknown") != "unknown":
                    description_parts.append(f"{appearance.get('eye_color')} eyes")
                
                if appearance.get("skin_tone", "unknown") != "unknown":
                    description_parts.append(f"{appearance.get('skin_tone')} skin tone")
                
                if appearance.get("clothing", "unknown") != "unknown":
                    description_parts.append(f"wearing {appearance.get('clothing')}")
                
                if appearance.get("distinctive_features", "unknown") != "unknown" and appearance.get("distinctive_features") != "none":
                    description_parts.append(f"with {appearance.get('distinctive_features')}")
                
                description = "a child with " + ", ".join(description_parts)
                
                # Cache the results
                child_character_description = description
                child_appearance_details = appearance
                
                logger.info(f"Extracted appearance details: {appearance}")
                return description, appearance
            else:
                logger.warning("Could not extract JSON from appearance analysis response")
                return "a young child", {"hair_color": "unknown", "hair_style": "unknown", "eye_color": "unknown", "skin_tone": "unknown", "clothing": "unknown", "distinctive_features": "unknown"}
        else:
            logger.error(f"Error analyzing appearance: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return "a young child", {"hair_color": "unknown", "hair_style": "unknown", "eye_color": "unknown", "skin_tone": "unknown", "clothing": "unknown", "distinctive_features": "unknown"}
    
    except Exception as e:
        logger.error(f"Error extracting appearance details: {str(e)}")
        return "a young child", {"hair_color": "unknown", "hair_style": "unknown", "eye_color": "unknown", "skin_tone": "unknown", "clothing": "unknown", "distinctive_features": "unknown"}

def generate_story(child_name, image_data, theme, age_range, generate_illustrations=True, rhyming=False):
    """Generate a personalized story based on the child's image and preferences."""
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Extract appearance details from the image
        character_desc, appearance_details = extract_appearance_details(image_data, api_key)
        
        # Prepare the prompt
        system_prompt = f"""You are a children's book author who creates personalized stories for young children.
        Write a short, engaging story for a {age_range} year old child named {child_name}.
        
        The story should:
        - Be about {theme}
        - Feature {child_name} as the main character, described as: {character_desc}
        - Be appropriate for a {age_range} year old
        - Be 300-500 words long
        - Have a clear beginning, middle, and end
        - Include a positive message or lesson
        - Use simple language appropriate for the age range
        - Start with a title formatted as "# [Title]"
        - Include ONE marker [STORY_SCENE: detailed visual description] at a point in the story that would make a great illustration
        """
        
        if rhyming:
            system_prompt += "- Use rhyming text throughout the story\n"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": "gpt-4-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please write a personalized story for {child_name} about {theme}."}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            story_text = response_data["choices"][0]["message"]["content"]
            
            logger.info(f"Generated story: {len(story_text)} characters")
            
            return story_text
        else:
            logger.error(f"Error generating story: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return "Error generating story. Please try again."
    
    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        return f"Error generating story: {str(e)}"

def _create_placeholder_image(message, error=False):
    """Create a placeholder image with text."""
    width, height = 800, 600
    color = (200, 50, 50) if error else (50, 50, 200)
    
    img = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # Wrap text
    lines = textwrap.wrap(message, width=40)
    y_position = height // 2 - len(lines) * 15
    
    for line in lines:
        line_width = draw.textlength(line, font=font)
        position = ((width - line_width) // 2, y_position)
        draw.text(position, line, font=font, fill=(255, 255, 255))
        y_position += 30
    
    # Save to a temporary file
    temp_path = os.path.join(PERSISTENT_IMAGE_DIR, f"placeholder_{int(time.time())}.jpg")
    img.save(temp_path)
    
    return temp_path

def generate_story_image(story_text, api_key):
    """Generate a single high-quality image for the story with text overlay."""
    try:
        logger.info("Generating story image")
        
        # Extract scene description from story text
        scene_match = re.search(r'\[STORY_SCENE:(.*?)\]', story_text, re.DOTALL)
        if scene_match:
            scene_description = scene_match.group(1).strip()
        else:
            # If no scene marker found, extract a description from the story
            logger.warning("No [STORY_SCENE] marker found, extracting description from story")
            
            # Get the middle part of the story for the scene
            lines = story_text.split('\n')
            content_lines = [line for line in lines if line.strip() and not line.startswith('#')]
            if content_lines:
                middle_index = len(content_lines) // 2
                scene_description = content_lines[middle_index]
            else:
                scene_description = "A magical scene from a children's story"
        
        logger.info(f"Using scene description: {scene_description}")
        
        # Set up API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Retry parameters
        max_retries = 5
        base_delay = 1  # seconds
        
        # Try multiple times with exponential backoff
        for attempt in range(max_retries):
            try:
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
                                # Open the original image
                                image = Image.open(BytesIO(image_bytes))
                                logger.info(f"Successfully downloaded image: {image.format}, {image.size}, {image.mode}")
                                
                                # Save the original image for debugging
                                timestamp = str(int(time.time()))
                                original_filename = f"story_image_original_{timestamp}.jpg"
                                original_path = os.path.join(PERSISTENT_IMAGE_DIR, original_filename)
                                image.save(original_path, quality=95)
                                logger.info(f"Saved original image to: {original_path}")
                                
                                # Add story text overlay
                                logger.info("Adding text overlay to image")
                                image_with_text = add_full_story_overlay(image, story_text)
                                
                                # Save to persistent directory with unique filename and timestamp to prevent caching
                                desc_str = str(scene_description) if scene_description else ""
                                story_str = str(story_text) if story_text else ""
                                unique_hash = hash(desc_str + story_str + timestamp)
                                filename = f"story_image_with_text_{timestamp}_{unique_hash}.jpg"
                                image_path = os.path.join(PERSISTENT_IMAGE_DIR, filename)
                                
                                # Ensure we're saving as RGB (not RGBA) for JPG format
                                if image_with_text.mode == 'RGBA':
                                    logger.info("Converting RGBA image to RGB for saving as JPG")
                                    image_with_text = image_with_text.convert('RGB')
                                
                                # Save with high quality
                                image_with_text.save(image_path, quality=95)
                                logger.info(f"Successfully saved image with text overlay to: {image_path}")
                                
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
        
        # Ensure the image is in RGBA mode for alpha compositing
        if img_with_text.mode != 'RGBA':
            logger.info(f"Converting image from {img_with_text.mode} to RGBA for overlay")
            img_with_text = img_with_text.convert('RGBA')
        
        draw = ImageDraw.Draw(img_with_text)
        
        # Get image dimensions
        width, height = img_with_text.size
        logger.info(f"Image dimensions: {width}x{height}")
        
        # Attempt to load fonts, fallback to default if not found
        try:
            title_font_size = 48
            body_font_size = 24
            
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", title_font_size)
            body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", body_font_size)
            logger.info("Successfully loaded fonts")
        except IOError as font_err:
            logger.error(f"Error loading fonts: {font_err}, using default")
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
        
        logger.info(f"Extracted title: '{title}'")
        logger.info(f"Body text length: {len(body)} characters")
        
        # Clean up the story text - remove the scene description marker
        body = re.sub(r'\[STORY_SCENE:.*?\]', '', body)
        
        # Create semi-transparent gradient overlay for the entire image
        logger.info("Creating gradient overlay")
        gradient = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw_gradient = ImageDraw.Draw(gradient)
        
        # Draw a gradient from transparent to semi-transparent black
        for y in range(height):
            # Calculate alpha based on position
            # More transparent at the top, more opaque at the bottom
            alpha = int(180 * (y / height))
            draw_gradient.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
        
        # Apply the gradient overlay
        logger.info("Applying gradient overlay")
        img_with_text = Image.alpha_composite(img_with_text, gradient)
        draw = ImageDraw.Draw(img_with_text)
        
        # Draw title at the top
        if title:
            logger.info(f"Drawing title: '{title}'")
            # Wrap title text
            title_max_width = width - 100  # 50px padding on each side
            wrapped_title = textwrap.fill(title, width=40)
            
            # Calculate title position (centered horizontally, at the top with padding)
            title_bbox = draw.textbbox((0, 0), wrapped_title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
            title_position = ((width - title_width) // 2, 30)
            
            logger.info(f"Title position: {title_position}, width: {title_width}, height: {title_height}")
            
            # Draw title with subtle shadow for better readability
            draw.text((title_position[0]+2, title_position[1]+2), wrapped_title, fill=(0, 0, 0, 200), font=title_font)
            draw.text(title_position, wrapped_title, fill=(255, 255, 255), font=title_font)
        
        # Prepare body text
        logger.info("Drawing body text")
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
        
        logger.info(f"Drawing {len(lines)} lines of body text starting at y={body_y_position}")
        
        for i, line in enumerate(lines):
            y_pos = body_y_position + (i * line_height)
            # Draw text with subtle shadow for better readability
            draw.text((52, y_pos+2), line, fill=(0, 0, 0, 200), font=body_font)
            draw.text((50, y_pos), line, fill=(255, 255, 255), font=body_font)
        
        logger.info("Successfully added full story text overlay")
        
        # Save a debug copy of the overlay image
        debug_path = os.path.join(PERSISTENT_IMAGE_DIR, f"debug_overlay_{int(time.time())}.jpg")
        img_with_text_rgb = img_with_text.convert('RGB')
        img_with_text_rgb.save(debug_path, quality=95)
        logger.info(f"Saved debug overlay image to: {debug_path}")
        
        return img_with_text
        
    except Exception as e:
        logger.error(f"Error adding full story text overlay: {str(e)}")
        # Return the original image if overlay fails
        return image
