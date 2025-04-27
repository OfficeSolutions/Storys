import os
import requests
import json
import tempfile
import base64
from PIL import Image
from io import BytesIO

def generate_illustration_with_openai(prompt, theme, api_key):
    """Generate an illustration using OpenAI's image generation API.
    
    Args:
        prompt: The description of the illustration to generate
        theme: The theme of the story (used to enhance the prompt)
        api_key: The OpenAI API key
        
    Returns:
        Path to the generated image file, or None if generation failed
    """
    try:
        # Enhance the prompt with the theme
        enhanced_prompt = f"A children's book illustration of {prompt}. Style: {theme}, colorful, whimsical, appropriate for children ages 4-8."
        
        # Set up the headers and data for the request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Try with gpt-image-1 first (requires verified organization)
        data = {
            "model": "gpt-image-1",
            "prompt": enhanced_prompt,
            "n": 1,
            "size": "1024x1024"
        }
        
        # Make the request to the OpenAI API
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        
        # If gpt-image-1 fails, try with dall-e-2 which has fewer restrictions
        if response.status_code != 200:
            print(f"gpt-image-1 failed with status {response.status_code}, trying dall-e-2")
            data["model"] = "dall-e-2"
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
                img_response = requests.get(image_url, timeout=30)
                if img_response.status_code == 200:
                    # Create a temporary file to store the image
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                    temp_file.write(img_response.content)
                    temp_file.close()
                    
                    return temp_file.name
        
        print(f"OpenAI image generation failed with status {response.status_code}: {response.text}")
        return None
            
    except Exception as e:
        print(f"Error generating image with OpenAI: {str(e)}")
        return None

def generate_illustration_with_gemini(prompt, theme, api_key):
    """Generate an illustration using Google's Gemini API.
    
    Args:
        prompt: The description of the illustration to generate
        theme: The theme of the story (used to enhance the prompt)
        api_key: The Gemini API key
        
    Returns:
        Path to the generated image file, or None if generation failed
    """
    try:
        import google.generativeai as genai
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Enhance the prompt with the theme
        enhanced_prompt = f"A children's book illustration of {prompt}. Style: {theme}, colorful, whimsical, appropriate for children ages 4-8."
        
        # Try different Gemini models for image generation
        models_to_try = [
            "gemini-2.0-flash-exp-image-generation",
            "gemini-1.5-flash"
        ]
        
        for model_name in models_to_try:
            try:
                # Generate the image using Gemini API
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(enhanced_prompt)
                
                # Check if image was generated
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data is not None:
                        # Save the image to a temporary file
                        image_data = base64.b64decode(part.inline_data.data)
                        image = Image.open(BytesIO(image_data))
                        
                        # Create a temporary file to store the image
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                        image.save(temp_file.name)
                        temp_file.close()
                        
                        return temp_file.name
                
                # If we got a response but no image, try the next model
                print(f"Model {model_name} returned a response but no image")
                
            except Exception as model_error:
                print(f"Error with model {model_name}: {str(model_error)}")
                continue
        
        print("All Gemini models failed to generate an image")
        return None
            
    except Exception as e:
        print(f"Error generating image with Gemini: {str(e)}")
        return None

def generate_illustration_image(prompt, theme, openai_api_key=None, gemini_api_key=None):
    """Generate an illustration image using available APIs.
    
    This function tries multiple image generation services in sequence,
    falling back to the next one if the previous fails.
    
    Args:
        prompt: The description of the illustration to generate
        theme: The theme of the story
        openai_api_key: Optional OpenAI API key
        gemini_api_key: Optional Gemini API key
        
    Returns:
        Path to the generated image file, or None if all generation attempts failed
    """
    # Try OpenAI first if API key is provided
    if openai_api_key:
        print(f"Attempting to generate illustration with OpenAI: {prompt}")
        image_path = generate_illustration_with_openai(prompt, theme, openai_api_key)
        if image_path:
            return image_path
    
    # Fall back to Gemini if API key is provided
    if gemini_api_key:
        print(f"Attempting to generate illustration with Gemini: {prompt}")
        image_path = generate_illustration_with_gemini(prompt, theme, gemini_api_key)
        if image_path:
            return image_path
    
    # If all attempts fail, return None
    print(f"Failed to generate illustration for: {prompt}")
    return None
