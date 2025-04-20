"""
Personalized Bedtime Story Generator - Improved Version with Modern UI

This script demonstrates a prototype of a personalized bedtime story generator
that uses the Gemini API to create stories based on a child's name and image.
The UI has been modernized with Bootstrap 5 components.
"""

from google import genai
import base64
import os
from PIL import Image, ImageDraw
import io
import time
import tempfile
from flask import Flask, request, render_template_string, redirect, url_for, jsonify, send_file

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

# Modern HTML template with Bootstrap 5
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Storybook Magic{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        :root {
            --primary-color: #6a11cb;
            --secondary-color: #2575fc;
            --accent-color: #ff7eb3;
            --light-color: #f8f9fa;
            --dark-color: #343a40;
        }
        
        body {
            font-family: 'Nunito', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        
        .navbar-brand {
            font-weight: 800;
            font-size: 1.8rem;
        }
        
        .navbar {
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        }
        
        .hero-section {
            background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('https://images.unsplash.com/photo-1512106374998-c4c9a41bae85');
            background-size: cover;
            background-position: center;
            color: white;
            padding: 6rem 0;
            border-radius: 0.5rem;
            margin-bottom: 2rem;
        }
        
        .card {
            border-radius: 1rem;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .btn-primary {
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            border: none;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
        }
        
        .btn-outline-primary {
            border-color: var(--primary-color);
            color: var(--primary-color);
        }
        
        .btn-outline-primary:hover {
            background-color: var(--primary-color);
            color: white;
        }
        
        .form-control {
            padding: 0.75rem;
            border-radius: 0.5rem;
        }
        
        .story-container {
            background-color: white;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .illustration {
            background-color: #f0f7ff;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1.5rem 0;
            font-style: italic;
            border-left: 4px solid var(--secondary-color);
        }
        
        .child-image {
            max-width: 100%;
            border-radius: 1rem;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(255, 255, 255, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            flex-direction: column;
        }
        
        .spinner-border {
            width: 3rem;
            height: 3rem;
        }
        
        footer {
            background-color: var(--dark-color);
            color: white;
            padding: 2rem 0;
            margin-top: 3rem;
        }
        
        .book-preview {
            perspective: 1000px;
            margin: 2rem auto;
            width: 300px;
            height: 400px;
        }
        
        .book {
            position: relative;
            width: 100%;
            height: 100%;
            transform-style: preserve-3d;
            transform: rotateY(-30deg);
            transition: transform 1s ease;
        }
        
        .book:hover {
            transform: rotateY(0deg);
        }
        
        .book-cover {
            position: absolute;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%);
            border-radius: 5px;
            box-shadow: 5px 5px 20px rgba(0, 0, 0, 0.3);
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            color: white;
            padding: 20px;
            text-align: center;
            backface-visibility: hidden;
        }
        
        .book-title {
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        
        .book-author {
            font-size: 1.2rem;
            font-style: italic;
        }
        
        .book-spine {
            position: absolute;
            width: 40px;
            height: 100%;
            left: -40px;
            background: linear-gradient(45deg, #5a0cb9 0%, #1565fc 100%);
            transform: rotateY(90deg) translateZ(20px);
            transform-origin: right;
            box-shadow: -2px 0 5px rgba(0, 0, 0, 0.2);
        }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="bi bi-book me-2"></i> Storybook Magic
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">How It Works</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">Examples</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">Contact</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container">
        {% block content %}{% endblock %}
    </div>

    <footer class="mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-4">
                    <h5>Storybook Magic</h5>
                    <p>Creating personalized bedtime stories for children using the power of AI.</p>
                </div>
                <div class="col-md-4">
                    <h5>Quick Links</h5>
                    <ul class="list-unstyled">
                        <li><a href="#" class="text-white">Home</a></li>
                        <li><a href="#" class="text-white">How It Works</a></li>
                        <li><a href="#" class="text-white">Examples</a></li>
                        <li><a href="#" class="text-white">Contact</a></li>
                    </ul>
                </div>
                <div class="col-md-4">
                    <h5>Connect With Us</h5>
                    <div class="d-flex gap-3 fs-4">
                        <a href="#" class="text-white"><i class="bi bi-facebook"></i></a>
                        <a href="#" class="text-white"><i class="bi bi-twitter"></i></a>
                        <a href="#" class="text-white"><i class="bi bi-instagram"></i></a>
                        <a href="#" class="text-white"><i class="bi bi-linkedin"></i></a>
                    </div>
                </div>
            </div>
            <hr class="my-4 bg-light">
            <div class="text-center">
                <p class="mb-0">© 2025 Storybook Magic. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
"""

# HTML template for the upload page
UPLOAD_TEMPLATE = """
{% extends "base.html" %}

{% block title %}Create Your Personalized Bedtime Story | Storybook Magic{% endblock %}

{% block content %}
<div class="hero-section text-center mb-5">
    <div class="container">
        <h1 class="display-4 fw-bold mb-3">Create Magical Bedtime Stories</h1>
        <p class="lead mb-4">Upload a photo of your child and we'll create a personalized bedtime story featuring them as the main character!</p>
        <a href="#create-story" class="btn btn-light btn-lg px-4 me-md-2">Get Started</a>
    </div>
</div>

<div class="row align-items-center mb-5">
    <div class="col-md-6">
        <h2 class="fw-bold mb-3">How It Works</h2>
        <div class="d-flex mb-3">
            <div class="me-3 fs-3 text-primary">
                <i class="bi bi-1-circle-fill"></i>
            </div>
            <div>
                <h5>Upload a Photo</h5>
                <p>Upload a clear photo of your child that shows their face and features.</p>
            </div>
        </div>
        <div class="d-flex mb-3">
            <div class="me-3 fs-3 text-primary">
                <i class="bi bi-2-circle-fill"></i>
            </div>
            <div>
                <h5>Enter Their Name</h5>
                <p>Tell us your child's name so we can make them the star of the story.</p>
            </div>
        </div>
        <div class="d-flex mb-3">
            <div class="me-3 fs-3 text-primary">
                <i class="bi bi-3-circle-fill"></i>
            </div>
            <div>
                <h5>Choose a Theme</h5>
                <p>Select an adventure theme that your child will love.</p>
            </div>
        </div>
        <div class="d-flex">
            <div class="me-3 fs-3 text-primary">
                <i class="bi bi-4-circle-fill"></i>
            </div>
            <div>
                <h5>Get Your Story</h5>
                <p>Our AI will create a unique story featuring your child that you can read together or order as a printed book.</p>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="book-preview">
            <div class="book">
                <div class="book-spine"></div>
                <div class="book-cover">
                    <div class="book-title">Emma's Magical Adventure</div>
                    <div class="book-author">A personalized story</div>
                    <div class="mt-4">
                        <i class="bi bi-stars fs-1"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row" id="create-story">
    <div class="col-lg-8 mx-auto">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h3 class="mb-0">Create Your Story</h3>
            </div>
            <div class="card-body">
                <form action="/generate" method="post" enctype="multipart/form-data" id="storyForm">
                    <div class="mb-4">
                        <label for="child_name" class="form-label fw-bold">Child's Name</label>
                        <input type="text" class="form-control form-control-lg" id="child_name" name="child_name" required placeholder="Enter your child's name">
                    </div>
                    
                    <div class="mb-4">
                        <label for="child_image" class="form-label fw-bold">Upload a Photo</label>
                        <input type="file" class="form-control form-control-lg" id="child_image" name="child_image" accept="image/*">
                        <div class="form-text">Upload a clear photo of your child's face for the best results.</div>
                    </div>
                    
                    <div class="mb-4">
                        <label for="theme" class="form-label fw-bold">Story Theme</label>
                        <select class="form-select form-select-lg" id="theme" name="theme">
                            <option value="adventure">Adventure</option>
                            <option value="fantasy">Fantasy</option>
                            <option value="space">Space Exploration</option>
                            <option value="underwater">Underwater Journey</option>
                            <option value="magical forest">Magical Forest</option>
                            <option value="dinosaur">Dinosaur Discovery</option>
                            <option value="superhero">Superhero Mission</option>
                        </select>
                    </div>
                    
                    <div class="d-grid gap-2">
                        <button type="submit" class="btn btn-primary btn-lg" id="generateBtn">
                            <i class="bi bi-magic me-2"></i> Generate Story
                        </button>
                        <a href="/generate-sample" class="btn btn-outline-primary">Try with a sample image</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<div class="row mt-5">
    <div class="col-12 text-center">
        <h2 class="fw-bold mb-4">Why Choose Storybook Magic?</h2>
    </div>
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <div class="card-body text-center p-4">
                <i class="bi bi-stars text-primary fs-1 mb-3"></i>
                <h4>Unique Stories</h4>
                <p>Every story is completely unique and personalized to your child, making bedtime reading extra special.</p>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <div class="card-body text-center p-4">
                <i class="bi bi-book text-primary fs-1 mb-3"></i>
                <h4>Beautiful Books</h4>
                <p>Turn your digital story into a professionally printed hardcover book that will become a cherished keepsake.</p>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <div class="card-body text-center p-4">
                <i class="bi bi-shield-check text-primary fs-1 mb-3"></i>
                <h4>Safe & Secure</h4>
                <p>Your child's photos and information are kept secure and are only used to create their story.</p>
            </div>
        </div>
    </div>
</div>

<div id="loadingOverlay" class="loading-overlay d-none">
    <div class="spinner-border text-primary mb-3" role="status">
        <span class="visually-hidden">Loading...</span>
    </div>
    <h4>Creating your magical story...</h4>
    <p>This may take a minute or two</p>
</div>
{% endblock %}

{% block extra_js %}
<script>
    document.getElementById('storyForm').addEventListener('submit', function() {
        document.getElementById('loadingOverlay').classList.remove('d-none');
    });
</script>
{% endblock %}
"""

# HTML template for the story display page
STORY_TEMPLATE = """
{% extends "base.html" %}

{% block title %}Your Personalized Bedtime Story | Storybook Magic{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-12">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/">Home</a></li>
                <li class="breadcrumb-item active">Your Story</li>
            </ol>
        </nav>
    </div>
</div>

<div class="row">
    <div class="col-lg-10 mx-auto">
        <div class="card mb-4">
            <div class="card-header bg-primary text-white">
                <h2 class="mb-0">{{ child_name }}'s Magical Story</h2>
            </div>
            <div class="card-body story-container">
                <div class="text-center mb-4">
                    <img src="{{ image_path }}" alt="{{ child_name }}" class="child-image mb-3" style="max-height: 300px;">
                    <div class="badge bg-primary text-white p-2 fs-6">{{ theme }} Adventure</div>
                </div>
                
                <div class="story">
                    {{ story_html|safe }}
                </div>
                
                <div class="d-flex justify-content-between mt-5">
                    <a href="/" class="btn btn-outline-primary btn-lg">
                        <i class="bi bi-arrow-left me-2"></i> Create Another Story
                    </a>
                    <button type="button" class="btn btn-primary btn-lg" data-bs-toggle="modal" data-bs-target="#orderModal">
                        <i class="bi bi-book me-2"></i> Order Printed Book
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Order Modal -->
<div class="modal fade" id="orderModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title">Order Your Printed Book</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="row align-items-center">
                    <div class="col-md-6">
                        <h4>Your book includes:</h4>
                        <ul class="list-group list-group-flush mb-4">
                            <li class="list-group-item d-flex align-items-center">
                                <i class="bi bi-check-circle-fill text-success me-2"></i>
                                Hardcover, full-color printing
                            </li>
                            <li class="list-group-item d-flex align-items-center">
                                <i class="bi bi-check-circle-fill text-success me-2"></i>
                                Professional illustrations
                            </li>
                            <li class="list-group-item d-flex align-items-center">
                                <i class="bi bi-check-circle-fill text-success me-2"></i>
                                High-quality paper
                            </li>
                            <li class="list-group-item d-flex align-items-center">
                                <i class="bi bi-check-circle-fill text-success me-2"></i>
                                Personalized dedication page
                            </li>
                            <li class="list-group-item d-flex align-items-center">
                                <i class="bi bi-check-circle-fill text-success me-2"></i>
                                Free shipping
                            </li>
                        </ul>
                        <div class="alert alert-primary">
                            <i class="bi bi-info-circle me-2"></i>
                            Your book will be printed and shipped within 5-7 business days.
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Order Summary</h5>
                                <div class="d-flex justify-content-between mb-2">
                                    <span>Hardcover Book:</span>
                                    <span>$29.99</span>
                                </div>
                                <div class="d-flex justify-content-between mb-2">
                                    <span>Shipping:</span>
                                    <span>FREE</span>
                                </div>
                                <hr>
                                <div class="d-flex justify-content-between fw-bold">
                                    <span>Total:</span>
                                    <span>$29.99</span>
                                </div>
                                <div class="d-grid gap-2 mt-4">
                                    <a href="https://www.blurb.com/print-api-software" target="_blank" class="btn btn-primary">
                                        Proceed to Checkout
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

@app.route('/')
def index():
    """Render the upload page."""
    return render_template_string(UPLOAD_TEMPLATE, base=BASE_TEMPLATE)

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
        'image_path': temp_path,
        'child_name': child_name,
        'theme': theme
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
        'image_path': sample_image_path,
        'child_name': "Alex",
        'theme': "adventure"
    }
    
    return redirect(url_for('view_story', story_id=story_id))

@app.route('/story/<story_id>')
def view_story(story_id):
    """View a generated story."""
    if story_id not in stories:
        return "Story not found", 404
    
    story_data = stories[story_id]
    
    # Process the story to highlight illustration descriptions
    story_html = story_data['story'].replace('[ILLUSTRATION:', '<div class="illustration"><i class="bi bi-image me-2"></i>[ILLUSTRATION:')
    story_html = story_html.replace(']', ']</div>')
    
    return render_template_string(
        STORY_TEMPLATE, 
        base=BASE_TEMPLATE,
        story_html=story_html,
        image_path=f"/image/{story_id}",
        child_name=story_data['child_name'],
        theme=story_data['theme']
    )

@app.route('/image/<story_id>')
def get_image(story_id):
    """Serve the image associated with a story."""
    if story_id not in stories:
        return "Image not found", 404
    
    image_path = stories[story_id]['image_path']
    
    # Read the image and return it
    return send_file(image_path, mimetype='image/jpeg')

def main():
    """Run the Flask app."""
    print("Starting Improved Personalized Bedtime Story Generator...")
    app.run(host='0.0.0.0', port=8080, debug=True)

if __name__ == "__main__":
    main()
