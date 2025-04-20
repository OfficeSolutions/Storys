"""
Personalized Bedtime Story Generator - Prototype Implementation

This script demonstrates a prototype of a personalized bedtime story generator
that uses the Gemini API to create stories based on a child's name and image.
"""

from google import genai
import base64
import os
from PIL import Image, ImageDraw
import io
import time
from flask import Flask, request, render_template_string, redirect, url_for
import tempfile

# Initialize the client with the provided API key
API_KEY = "AIzaSyD_TRW55r7Am5mhsKiQph9RHwyfml9WOH4"
client = genai.Client(api_key=API_KEY)

# Create a simple Flask app for the web interface
app = Flask(__name__)

# Store generated stories temporarily
stories = {}

def encode_image(image_path):
    """Encode an image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
    except Exception as e:
        print(f"Error encoding image: {str(e)}")
        return None

def generate_story(child_name, image_data, theme="adventure"):
    """Generate a personalized bedtime story using Gemini API."""
    if not image_data:
        return "No valid image data to analyze."
    
    try:
        # Create a prompt for the story generation
        story_prompt = f"""
        Create a personalized bedtime story for a child named {child_name}. 
        The story should be appropriate for a young child (ages 4-8) and should be about 500 words long.
        The child in the story should be the main character and should go on a {theme} adventure.
        
        Use details from the provided image to personalize the story (like hair color, clothing, etc.).
        
        The story should:
        1. Have a clear beginning, middle, and end
        2. Include 4-5 key scenes that could be illustrated
        3. Have a positive message or lesson
        4. End with the child falling asleep peacefully
        
        Also provide 4-5 brief descriptions for illustrations that would accompany the story.
        Format the illustration descriptions as: [ILLUSTRATION: description]
        """
        
        # Generate the story using Gemini API
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                {"role": "user", "parts": [
                    {"text": story_prompt},
                    {"inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_data
                    }}
                ]}
            ]
        )
        
        return response.text
    except Exception as e:
        return f"Error generating story: {str(e)}"

def create_sample_child_image():
    """Create a simple cartoon-like image of a child for testing."""
    try:
        # Create a blank image with white background
        img = Image.new('RGB', (400, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw a simple cartoon child
        # Head
        draw.ellipse([(150, 100), (250, 200)], fill='#FFE0BD', outline='black')
        
        # Eyes
        draw.ellipse([(175, 130), (185, 140)], fill='white', outline='black')
        draw.ellipse([(215, 130), (225, 140)], fill='white', outline='black')
        draw.ellipse([(178, 133), (182, 137)], fill='black')
        draw.ellipse([(218, 133), (222, 137)], fill='black')
        
        # Smile
        draw.arc([(175, 140), (225, 170)], 0, 180, fill='black', width=2)
        
        # Hair
        draw.rectangle([(150, 100), (250, 120)], fill='brown')
        
        # Body
        draw.rectangle([(175, 200), (225, 350)], fill='blue', outline='black')
        
        # Arms
        draw.rectangle([(125, 220), (175, 240)], fill='blue', outline='black')
        draw.rectangle([(225, 220), (275, 240)], fill='blue', outline='black')
        
        # Legs
        draw.rectangle([(175, 350), (195, 450)], fill='#FFE0BD', outline='black')
        draw.rectangle([(205, 350), (225, 450)], fill='#FFE0BD', outline='black')
        
        # Shoes
        draw.ellipse([(165, 440), (205, 460)], fill='red', outline='black')
        draw.ellipse([(195, 440), (235, 460)], fill='red', outline='black')
        
        # Save the image
        local_path = "sample_child.jpg"
        img.save(local_path)
        
        print(f"Created sample child image at {local_path}")
        return local_path
    except Exception as e:
        print(f"Error creating sample image: {str(e)}")
        return None

# HTML template for the upload page
UPLOAD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Personalized Bedtime Story Generator</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .container {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], select {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        input[type="file"] {
            border: 1px solid #ddd;
            padding: 8px;
            width: 100%;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #2980b9;
        }
        .sample-option {
            margin-top: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>Personalized Bedtime Story Generator</h1>
    <div class="container">
        <form action="/generate" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label for="child_name">Child's Name:</label>
                <input type="text" id="child_name" name="child_name" required>
            </div>
            <div class="form-group">
                <label for="child_image">Upload a Photo:</label>
                <input type="file" id="child_image" name="child_image" accept="image/*">
            </div>
            <div class="form-group">
                <label for="theme">Story Theme:</label>
                <select id="theme" name="theme">
                    <option value="adventure">Adventure</option>
                    <option value="fantasy">Fantasy</option>
                    <option value="space">Space</option>
                    <option value="underwater">Underwater</option>
                    <option value="magical forest">Magical Forest</option>
                </select>
            </div>
            <button type="submit">Generate Story</button>
        </form>
        <div class="sample-option">
            <p>Don't have an image? <a href="/generate-sample">Try with a sample image</a></p>
        </div>
    </div>
</body>
</html>
"""

# HTML template for the story display page
STORY_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Your Personalized Bedtime Story</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .container {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .story {
            white-space: pre-line;
            font-size: 18px;
        }
        .illustration {
            background-color: #e8f4fc;
            padding: 10px;
            border-radius: 5px;
            margin: 15px 0;
            font-style: italic;
        }
        .buttons {
            margin-top: 20px;
            text-align: center;
        }
        .btn {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            text-decoration: none;
            display: inline-block;
            margin: 0 10px;
        }
        .btn:hover {
            background-color: #2980b9;
        }
        .btn-order {
            background-color: #27ae60;
        }
        .btn-order:hover {
            background-color: #219955;
        }
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1>Your Personalized Bedtime Story</h1>
    <div class="container">
        <img src="{{ image_path }}" alt="Child's image">
        <div class="story">
            {{ story_html|safe }}
        </div>
        <div class="buttons">
            <a href="/" class="btn">Create Another Story</a>
            <a href="#" class="btn btn-order">Order Printed Book</a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Render the upload page."""
    return render_template_string(UPLOAD_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    """Generate a story based on the uploaded image and child's name."""
    child_name = request.form.get('child_name', 'Child')
    theme = request.form.get('theme', 'adventure')
    
    # Check if an image was uploaded
    if 'child_image' not in request.files:
        return "No image uploaded", 400
    
    file = request.files['child_image']
    
    # If no file was selected
    if file.filename == '':
        return "No image selected", 400
    
    # Save the uploaded file temporarily
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, "uploaded_image.jpg")
    file.save(temp_path)
    
    # Process the image and generate a story
    image_data = encode_image(temp_path)
    story = generate_story(child_name, image_data, theme)
    
    # Store the story and image path
    story_id = str(int(time.time()))
    stories[story_id] = {
        'story': story,
        'image_path': temp_path
    }
    
    return redirect(url_for('view_story', story_id=story_id))

@app.route('/generate-sample')
def generate_sample():
    """Generate a story using a sample image."""
    # Create a sample child image
    sample_image_path = create_sample_child_image()
    
    if not sample_image_path:
        return "Failed to create sample image", 500
    
    # Generate a story using the sample image
    image_data = encode_image(sample_image_path)
    story = generate_story("Alex", image_data, "adventure")
    
    # Store the story and image path
    story_id = str(int(time.time()))
    stories[story_id] = {
        'story': story,
        'image_path': sample_image_path
    }
    
    return redirect(url_for('view_story', story_id=story_id))

@app.route('/story/<story_id>')
def view_story(story_id):
    """View a generated story."""
    if story_id not in stories:
        return "Story not found", 404
    
    story_data = stories[story_id]
    
    # Process the story to highlight illustration descriptions
    story_html = story_data['story'].replace('[ILLUSTRATION:', '<div class="illustration">[ILLUSTRATION:')
    story_html = story_html.replace(']', ']</div>')
    
    return render_template_string(
        STORY_TEMPLATE, 
        story_html=story_html,
        image_path=f"/image/{story_id}"
    )

@app.route('/image/<story_id>')
def get_image(story_id):
    """Serve the image associated with a story."""
    if story_id not in stories:
        return "Image not found", 404
    
    image_path = stories[story_id]['image_path']
    
    # Read the image and return it
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    return image_data, 200, {'Content-Type': 'image/jpeg'}

def main():
    """Run the Flask app."""
    print("Starting Personalized Bedtime Story Generator...")
    app.run(host='0.0.0.0', port=8080, debug=True)

if __name__ == "__main__":
    main()
