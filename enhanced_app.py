import os
import base64
import time
import random
import string
import tempfile
from flask import Flask, request, render_template_string, redirect, url_for, jsonify, send_file
import google.generativeai as genai
from PIL import Image
from io import BytesIO

# Initialize the Gemini API with the API key from environment variable
API_KEY = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=API_KEY)

# Create a simple Flask app for the web interface
app = Flask(__name__)

# In-memory storage for generated stories and images
stories = {}
illustration_images = {}

def encode_image(image_path):
    """Encode an image file to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_illustration_descriptions(story_text):
    """Extract illustration descriptions from the story text."""
    illustrations = []
    parts = story_text.split('[ILLUSTRATION:')
    for i in range(1, len(parts)):
        end_idx = parts[i].find(']')
        if end_idx != -1:
            description = parts[i][:end_idx].strip()
            illustrations.append(description)
    return illustrations

def generate_illustration_image(description, theme):
    """Generate an illustration image based on the description using Gemini API."""
    try:
        # Create a prompt for the image generation
        image_prompt = f"""
        Create a child-friendly illustration for a bedtime story with the theme: {theme}.
        The illustration should show: {description}
        Style: Colorful, whimsical, appropriate for children ages 4-8.
        Make it look like a professional children's book illustration.
        """
        
        # Generate the image using Gemini API
        model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")
        response = model.generate_content(
            contents=image_prompt,
            config=genai.types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            )
        )
        
        # Extract the image from the response
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
        
        return None
    except Exception as e:
        print(f"Error generating illustration: {str(e)}")
        return None

def generate_story(child_name, image_data, theme, generate_illustrations=False):
    """Generate a personalized bedtime story using the Gemini API."""
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
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
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
    """Create a sample cartoon child image for testing."""
    try:
        # Use a predefined sample image path
        sample_image_path = os.path.join(os.path.dirname(__file__), 'sample_child.jpg')
        if os.path.exists(sample_image_path):
            return sample_image_path
        else:
            return None
    except Exception as e:
        print(f"Error creating sample image: {str(e)}")
        return None

# HTML templates
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if page_title %}{{ page_title }}{% else %}Storybook Magic{% endif %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding-bottom: 50px;
        }
        .navbar {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        .navbar-brand {
            font-weight: bold;
            font-size: 1.8rem;
            color: white !important;
        }
        .hero {
            background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1512058564366-18510be2db19?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2072&q=80');
            background-size: cover;
            background-position: center;
            color: white;
            padding: 100px 0;
            margin-bottom: 40px;
            border-radius: 0 0 20px 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .card {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            margin-bottom: 30px;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .form-control, .btn {
            border-radius: 10px;
        }
        .btn-primary {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border: none;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .btn-primary:hover {
            background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
            transform: translateY(-2px);
        }
        .book {
            perspective: 1000px;
            width: 100%;
            height: 400px;
            margin: 0 auto 40px;
        }
        .book-cover {
            width: 100%;
            height: 100%;
            position: relative;
            transform-style: preserve-3d;
            transform: rotateY(-30deg);
            transition: transform 1s ease;
            box-shadow: 5px 5px 20px rgba(0,0,0,0.3);
            border-radius: 5px 10px 10px 5px;
            background: linear-gradient(90deg, #ff9a9e 0%, #fad0c4 100%);
        }
        .book:hover .book-cover {
            transform: rotateY(-10deg);
        }
        .book-spine {
            position: absolute;
            left: 0;
            top: 0;
            width: 30px;
            height: 100%;
            background: linear-gradient(90deg, #a18cd1 0%, #fbc2eb 100%);
            transform: rotateY(90deg) translateZ(15px);
            border-radius: 5px 0 0 5px;
        }
        .book-content {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            color: #333;
        }
        .book-title {
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .book-author {
            font-size: 1.2rem;
            margin-bottom: 20px;
            color: #555;
        }
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 20px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .illustration {
            background-color: #f8f9fa;
            border-left: 4px solid #6c757d;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .story-container {
            background-color: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .story-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .story-image {
            border-radius: 15px;
            overflow: hidden;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .story-image img {
            width: 100%;
            height: auto;
        }
        .story-content {
            font-size: 1.1rem;
            line-height: 1.8;
        }
        .story-meta {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            color: #6c757d;
        }
        .story-meta span {
            display: flex;
            align-items: center;
        }
        .story-meta i {
            margin-right: 5px;
        }
        .order-options {
            background-color: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-top: 30px;
        }
        .price-tag {
            font-size: 1.5rem;
            font-weight: bold;
            color: #28a745;
        }
        .form-check-input:checked {
            background-color: #764ba2;
            border-color: #764ba2;
        }
        .illustration-image {
            max-width: 100%;
            border-radius: 10px;
            margin: 15px 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        {% block extra_css %}{% endblock %}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="bi bi-book me-2"></i>Storybook Magic</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/"><i class="bi bi-house-door me-1"></i>Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/generate-sample"><i class="bi bi-magic me-1"></i>Try Sample</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#about"><i class="bi bi-info-circle me-1"></i>About</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container">
        {% block content %}{% endblock %}
    </div>

    <footer class="bg-dark text-white text-center py-4 mt-5">
        <div class="container">
            <p class="mb-0">© 2025 Storybook Magic. All rights reserved.</p>
            <p class="small text-muted">Powered by Gemini API</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
"""

HOME_TEMPLATE = """
<div class="hero text-center">
    <h1 class="display-4 fw-bold mb-4">Create Magical Bedtime Stories</h1>
    <p class="lead mb-5">Personalized stories featuring your child as the main character, <br>generated with AI and ready to print!</p>
    <a href="#create" class="btn btn-light btn-lg px-5 py-3 fw-bold">Create Your Story</a>
</div>

<div class="row mb-5">
    <div class="col-md-4">
        <div class="card h-100">
            <div class="card-body text-center p-4">
                <i class="bi bi-person-bounding-box feature-icon"></i>
                <h3>Personalized</h3>
                <p>Upload a photo of your child and they'll become the star of their very own adventure!</p>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card h-100">
            <div class="card-body text-center p-4">
                <i class="bi bi-stars feature-icon"></i>
                <h3>Magical Themes</h3>
                <p>Choose from exciting themes like space, underwater, fantasy, and more!</p>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card h-100">
            <div class="card-body text-center p-4">
                <i class="bi bi-book feature-icon"></i>
                <h3>Print Ready</h3>
                <p>Order a professionally printed hardcover or softcover book delivered to your door!</p>
            </div>
        </div>
    </div>
</div>

<div class="row align-items-center mb-5">
    <div class="col-lg-6">
        <div class="book">
            <div class="book-cover">
                <div class="book-spine"></div>
                <div class="book-content">
                    <div class="book-title">The Amazing Adventure</div>
                    <div class="book-author">Featuring Your Child</div>
                    <p>A personalized story created just for you</p>
                </div>
            </div>
        </div>
    </div>
    <div class="col-lg-6">
        <h2 class="mb-4">How It Works</h2>
        <div class="d-flex mb-4">
            <div class="me-3">
                <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">1</div>
            </div>
            <div>
                <h5>Upload a Photo</h5>
                <p>Upload a photo of your child or use our sample image</p>
            </div>
        </div>
        <div class="d-flex mb-4">
            <div class="me-3">
                <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">2</div>
            </div>
            <div>
                <h5>Enter Details</h5>
                <p>Enter your child's name and choose a story theme</p>
            </div>
        </div>
        <div class="d-flex mb-4">
            <div class="me-3">
                <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">3</div>
            </div>
            <div>
                <h5>Generate Story</h5>
                <p>Our AI creates a personalized story with illustrations</p>
            </div>
        </div>
        <div class="d-flex">
            <div class="me-3">
                <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">4</div>
            </div>
            <div>
                <h5>Order a Book</h5>
                <p>Order a printed book or save as a digital copy</p>
            </div>
        </div>
    </div>
</div>

<div class="card mb-5" id="create">
    <div class="card-body p-4">
        <h2 class="text-center mb-4">Create Your Personalized Story</h2>
        <form action="/generate" method="post" enctype="multipart/form-data">
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="childName" class="form-label">Child's Name</label>
                    <input type="text" class="form-control form-control-lg" id="childName" name="childName" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="theme" class="form-label">Story Theme</label>
                    <select class="form-select form-select-lg" id="theme" name="theme" required>
                        <option value="adventure">Adventure</option>
                        <option value="fantasy">Fantasy</option>
                        <option value="space">Space</option>
                        <option value="underwater">Underwater</option>
                        <option value="dinosaur">Dinosaur</option>
                        <option value="fairy tale">Fairy Tale</option>
                    </select>
                </div>
            </div>
            <div class="mb-3">
                <label for="childImage" class="form-label">Upload Child's Photo</label>
                <input type="file" class="form-control form-control-lg" id="childImage" name="childImage" accept="image/*">
                <div class="form-text">Upload a clear photo of your child's face for best results.</div>
            </div>
            <div class="mb-3 form-check">
                <input type="checkbox" class="form-check-input" id="generateIllustrations" name="generateIllustrations" value="true">
                <label class="form-check-label" for="generateIllustrations">Generate illustrations for the story</label>
            </div>
            <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary btn-lg py-3">Generate Story</button>
                <a href="/generate-sample" class="btn btn-outline-secondary">Try with a sample image</a>
            </div>
        </form>
    </div>
</div>

<div class="row mb-5" id="about">
    <div class="col-12">
        <div class="card">
            <div class="card-body p-4">
                <h2 class="text-center mb-4">About Storybook Magic</h2>
                <p>Storybook Magic uses advanced AI technology to create personalized bedtime stories featuring your child as the main character. Our stories are designed to be engaging, age-appropriate, and filled with positive messages.</p>
                <p>Each story is uniquely generated based on your child's photo and name, creating a truly personalized experience that they'll love. You can choose from various exciting themes to match your child's interests.</p>
                <p>After generating your story, you can order a professionally printed book that will be delivered to your door, creating a keepsake that will be treasured for years to come.</p>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-4">
        <div class="card h-100">
            <div class="card-body text-center p-4">
                <h4 class="mb-3">Digital Copy</h4>
                <p class="price-tag mb-3">Free</p>
                <ul class="list-unstyled text-start mb-4">
                    <li><i class="bi bi-check-circle-fill text-success me-2"></i>Personalized story</li>
                    <li><i class="bi bi-check-circle-fill text-success me-2"></i>Digital format</li>
                    <li><i class="bi bi-check-circle-fill text-success me-2"></i>Shareable link</li>
                    <li><i class="bi bi-x-circle-fill text-muted me-2"></i>Printed copy</li>
                </ul>
                <div class="d-grid">
                    <button class="btn btn-outline-primary">Download Free</button>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card h-100 border-primary">
            <div class="card-header bg-primary text-white text-center py-3">
                <h5 class="mb-0">Most Popular</h5>
            </div>
            <div class="card-body text-center p-4">
                <h4 class="mb-3">Softcover Book</h4>
                <p class="price-tag mb-3">$19.99</p>
                <ul class="list-unstyled text-start mb-4">
                    <li><i class="bi bi-check-circle-fill text-success me-2"></i>Personalized story</li>
                    <li><i class="bi bi-check-circle-fill text-success me-2"></i>High-quality printing</li>
                    <li><i class="bi bi-check-circle-fill text-success me-2"></i>Softcover binding</li>
                    <li><i class="bi bi-check-circle-fill text-success me-2"></i>8.5" x 8.5" size</li>
                </ul>
                <div class="d-grid">
                    <button class="btn btn-primary">Order Now</button>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card h-100">
            <div class="card-body text-center p-4">
                <h4 class="mb-3">Hardcover Book</h4>
                <p class="price-tag mb-3">$29.99</p>
                <ul class="list-unstyled text-start mb-4">
                    <li><i class="bi bi-check-circle-fill text-success me-2"></i>Personalized story</li>
                    <li><i class="bi bi-check-circle-fill text-success me-2"></i>Premium printing</li>
                    <li><i class="bi bi-check-circle-fill text-success me-2"></i>Durable hardcover</li>
                    <li><i class="bi bi-check-circle-fill text-success me-2"></i>8.5" x 8.5" size</li>
                </ul>
                <div class="d-grid">
                    <button class="btn btn-outline-primary">Order Now</button>
                </div>
            </div>
        </div>
    </div>
</div>
"""

STORY_TEMPLATE = """
<div class="row">
    <div class="col-lg-8 mx-auto">
        <div class="story-container">
            <div class="story-header">
                <h1 class="mb-4">{{ child_name }}'s {{ theme }} Adventure</h1>
                <div class="story-meta">
                    <span><i class="bi bi-person"></i> Featuring: {{ child_name }}</span>
                    <span><i class="bi bi-tag"></i> Theme: {{ theme }}</span>
                </div>
            </div>
            
            <div class="story-image mb-4">
                <img src="{{ image_path }}" alt="{{ child_name }}" class="img-fluid">
            </div>
            
            <div class="story-content">
                {{ story_html|safe }}
            </div>
            
            <div class="order-options mt-5">
                <h3 class="mb-4">Order this story as a printed book</h3>
                <div class="row">
                    <div class="col-md-6">
                        <div class="form-check mb-3">
                            <input class="form-check-input" type="radio" name="bookType" id="softcover" checked>
                            <label class="form-check-label d-flex justify-content-between" for="softcover">
                                <span>Softcover Book</span>
                                <span class="price-tag">$19.99</span>
                            </label>
                        </div>
                        <div class="form-check mb-3">
                            <input class="form-check-input" type="radio" name="bookType" id="hardcover">
                            <label class="form-check-label d-flex justify-content-between" for="hardcover">
                                <span>Hardcover Book</span>
                                <span class="price-tag">$29.99</span>
                            </label>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="d-grid">
                            <button class="btn btn-primary btn-lg">Order Printed Book</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

{% block extra_js %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Add animation to the story elements
        const storyElements = document.querySelectorAll('.story-content p');
        storyElements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            setTimeout(() => {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, 100 * index);
        });
    });
</script>
{% endblock %}
"""

@app.route('/')
def home():
    """Render the home page."""
    return render_template_string(MAIN_TEMPLATE.replace('{% block content %}{% endblock %}', HOME_TEMPLATE))

@app.route('/generate', methods=['POST'])
def generate():
    """Generate a personalized story based on the uploaded image."""
    child_name = request.form.get('childName', '')
    theme = request.form.get('theme', 'adventure')
    generate_illustrations = request.form.get('generateIllustrations') == 'true'
    
    # Check if an image was uploaded
    if 'childImage' not in request.files or request.files['childImage'].filename == '':
        return "No image uploaded", 400
    
    # Save the uploaded image to a temporary file
    image_file = request.files['childImage']
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    image_file.save(temp_file.name)
    temp_file.close()
    temp_path = temp_file.name
    
    # Encode the image to base64
    image_data = encode_image(temp_path)
    
    # Generate the story
    story = generate_story(child_name, image_data, theme, generate_illustrations)
    
    # Store the story and image path
    story_id = str(int(time.time()))
    stories[story_id] = {
        'story': story,
        'image_path': temp_path,
        'child_name': child_name,
        'theme': theme,
        'generate_illustrations': generate_illustrations
    }
    
    # Generate illustrations if requested
    if generate_illustrations:
        # Extract illustration descriptions from the story
        descriptions = extract_illustration_descriptions(story)
        
        # Generate images for each description
        illustration_images[story_id] = []
        for desc in descriptions:
            image_path = generate_illustration_image(desc, theme)
            if image_path:
                illustration_images[story_id].append({
                    'description': desc,
                    'image_path': image_path
                })
    
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
        'image_path': sample_image_path,
        'child_name': "Alex",
        'theme': "adventure",
        'generate_illustrations': False
    }
    
    return redirect(url_for('view_story', story_id=story_id))

@app.route('/story/<story_id>')
def view_story(story_id):
    """View a generated story."""
    if story_id not in stories:
        return "Story not found", 404
    
    story_data = stories[story_id]
    generate_illustrations = story_data.get('generate_illustrations', False)
    
    # Process the story to highlight illustration descriptions or replace with actual images
    story_html = story_data['story']
    
    if generate_illustrations and story_id in illustration_images:
        # Replace illustration descriptions with actual images
        for illustration in illustration_images[story_id]:
            desc = illustration['description']
            img_path = illustration['image_path']
            img_url = f"/illustration/{story_id}/{desc}"
            img_tag = f'<div class="illustration"><img src="{img_url}" alt="{desc}" class="illustration-image"><p><i class="bi bi-image me-2"></i>{desc}</p></div>'
            story_html = story_html.replace(f'[ILLUSTRATION: {desc}]', img_tag)
    else:
        # Just highlight the illustration descriptions
        story_html = story_html.replace('[ILLUSTRATION:', '<div class="illustration"><i class="bi bi-image me-2"></i>[ILLUSTRATION:')
        story_html = story_html.replace(']', ']</div>')
    
    # Fixed: Use a combined template instead of extending from base.html
    combined_template = MAIN_TEMPLATE.replace('{% block content %}{% endblock %}', STORY_TEMPLATE)
    combined_template = combined_template.replace('{% block extra_js %}{% endblock %}', 
                                                 STORY_TEMPLATE.split('{% block extra_js %}')[1].split('{% endblock %}')[0])
    combined_template = combined_template.replace('{% block extra_css %}{% endblock %}', '')
    combined_template = combined_template.replace('{% if page_title %}{{ page_title }}{% else %}Storybook Magic{% endif %}', 
                                                 f"Your Personalized Bedtime Story | Storybook Magic")
    
    # Replace variables in the template
    template_with_vars = combined_template.replace('{{ story_html|safe }}', story_html)
    template_with_vars = template_with_vars.replace('{{ image_path }}', f"/image/{story_id}")
    template_with_vars = template_with_vars.replace('{{ child_name }}', story_data['child_name'])
    template_with_vars = template_with_vars.replace('{{ theme }}', story_data['theme'])
    
    return render_template_string(template_with_vars)

@app.route('/image/<story_id>')
def get_image(story_id):
    """Serve the image associated with a story."""
    if story_id not in stories:
        return "Story not found", 404
    
    return send_file(stories[story_id]['image_path'])

@app.route('/illustration/<story_id>/<description>')
def get_illustration(story_id, description):
    """Serve an illustration image."""
    if story_id not in illustration_images:
        return "Illustration not found", 404
    
    for illustration in illustration_images[story_id]:
        if illustration['description'] == description:
            return send_file(illustration['image_path'])
    
    return "Illustration not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)
