"""
Image Analysis Example using Gemini API - Updated

This script demonstrates how to use the Gemini API for image analysis and description.
It shows how to:
1. Create a simple test image
2. Get detailed descriptions
3. Ask specific questions about image content
"""

from google import genai
import base64
import os
from PIL import Image, ImageDraw
import io

# Initialize the client with the provided API key
API_KEY = "AIzaSyD_TRW55r7Am5mhsKiQph9RHwyfml9WOH4"
client = genai.Client(api_key=API_KEY)

def create_test_image():
    """Create a simple test image with shapes."""
    try:
        # Create a blank image with white background
        img = Image.new('RGB', (500, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw some shapes
        draw.rectangle([(50, 50), (200, 200)], fill='blue', outline='black')
        draw.ellipse([(250, 50), (450, 200)], fill='red', outline='black')
        draw.polygon([(50, 250), (200, 250), (125, 280)], fill='green', outline='black')
        
        # Save the image
        local_path = "test_shapes.jpg"
        img.save(local_path)
        
        print(f"Created test image at {local_path}")
        return local_path
    except Exception as e:
        print(f"Error creating test image: {str(e)}")
        return None

def encode_local_image(image_path):
    """Encode a local image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
    except Exception as e:
        print(f"Error encoding local image: {str(e)}")
        return None

def analyze_image(image_data, prompt):
    """Analyze an image using Gemini API."""
    if not image_data:
        return "No valid image data to analyze."
    
    try:
        # Create a multipart message with both text and image
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                {"role": "user", "parts": [
                    {"text": prompt},
                    {"inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_data
                    }}
                ]}
            ]
        )
        return response.text
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def main():
    print("GEMINI IMAGE ANALYSIS EXAMPLE")
    print("=============================\n")
    
    # Create a simple test image
    local_image_path = create_test_image()
    
    if not local_image_path:
        print("Failed to create test image. Exiting.")
        return
    
    print(f"Using local image: {local_image_path}")
    encoded_image = encode_local_image(local_image_path)
    
    if not encoded_image:
        print("Failed to encode image. Exiting.")
        return
    
    # Get a detailed description
    description_prompt = "Provide a detailed description of this image. What do you see?"
    description = analyze_image(encoded_image, description_prompt)
    
    print("\n=== DETAILED DESCRIPTION ===")
    print(description)
    
    # Ask specific questions about the image
    questions = [
        "What shapes are in this image?",
        "What colors are used in this image?",
        "Describe the spatial arrangement of the shapes.",
        "What might this image be used for?"
    ]
    
    print("\n=== SPECIFIC QUESTIONS ===")
    for question in questions:
        answer = analyze_image(encoded_image, question)
        print(f"\nQ: {question}")
        print(f"A: {answer}")
    
    print("\nImage analysis complete!")

if __name__ == "__main__":
    main()
