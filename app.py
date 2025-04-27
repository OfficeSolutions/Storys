import os
import tempfile
import time
import base64
import uuid
import urllib.parse
import logging
from flask import Flask, render_template_string, request, redirect, url_for, send_file, abort
from werkzeug.utils import secure_filename
from debug_enhanced_story_generator import (
    generate_story, 
    generate_illustration, 
    extract_illustration_descriptions,
    generate_ghibli_style_image
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# In-memory storage for stories and images
stories = {}
illustration_images = {}

def encode_image(image_path):
    """Encode an image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# HTML template for the main layout
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title|default('Storybook Magic') }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        :root {
            --primary-color: #3a86ff;
            --secondary-color: #8338ec;
            --accent-color: #ff006e;
            --light-color: #ffffff;
            --dark-color: #212529;
            --background-color: #f8f9fa;
        }
        
        body {
            font-family: 'Nunito', sans-serif;
            background-color: var(--background-color);
            color: var(--dark-color);
            line-height: 1.6;
        }
        
        .navbar {
            background-color: var(--light-color);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .navbar-brand {
            font-weight: bold;
            color: var(--primary-color) !important;
        }
        
        .hero-section {
            padding: 4rem 0;
            background-color: var(--light-color);
            border-radius: 0.5rem;
            margin: 2rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        .card {
            border: none;
            border-radius: 0.5rem;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            height: 100%;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        .card-img-top {
            height: 200px;
            object-fit: cover;
        }
        
        .form-container {
            background-color: var(--light-color);
            border-radius: 0.5rem;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        .btn-primary {
            background-color: var(--primary-color);
            border: none;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .btn-primary:hover {
            background-color: var(--secondary-color);
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
        }
        
        .btn-outline-primary {
            color: var(--primary-color);
            border-color: var(--primary-color);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .btn-outline-primary:hover {
            background-color: var(--primary-color);
            color: var(--light-color);
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
        }
        
        footer {
            background-color: var(--light-color);
            padding: 2rem 0;
            margin-top: 3rem;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
        }
        
        .story-container {
            background-color: var(--light-color);
            border-radius: 0.5rem;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        .child-image {
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 100%;
            height: auto;
        }
        
        .illustration {
            background-color: var(--background-color);
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1.5rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            text-align: center;
        }
        
        .illustration-image {
            max-width: 100%;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
            display: block;
            margin: 0 auto 1rem auto;
        }
        
        /* 3D Book Styles */
        .book-container {
            perspective: 1000px;
            width: 100%;
            height: 500px;
            margin: 2rem auto;
            position: relative;
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
        
        .book-front, .book-back, .book-spine, .book-top, .book-bottom, .book-right {
            position: absolute;
            background-color: var(--light-color);
            border-radius: 2px;
            box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
        }
        
        .book-front, .book-back {
            width: 100%;
            height: 100%;
        }
        
        .book-front {
            transform: translateZ(20px);
            background-color: var(--primary-color);
            color: var(--light-color);
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            border-radius: 5px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
        }
        
        .book-back {
            transform: translateZ(-20px) rotateY(180deg);
            background-color: var(--secondary-color);
            border-radius: 5px;
        }
        
        .book-spine {
            width: 40px;
            height: 100%;
            transform: rotateY(90deg) translateZ(-20px);
            background-color: var(--accent-color);
        }
        
        .book-top {
            width: 100%;
            height: 40px;
            transform: rotateX(90deg) translateZ(-20px);
            background-color: var(--light-color);
        }
        
        .book-bottom {
            width: 100%;
            height: 40px;
            transform: rotateX(-90deg) translateZ(460px);
            background-color: var(--light-color);
        }
        
        .book-right {
            width: 40px;
            height: 100%;
            transform: rotateY(-90deg) translateZ(calc(100% - 20px));
            background-color: var(--background-color);
        }
        
        .book-content {
            max-height: 400px;
            overflow-y: auto;
            padding: 20px;
        }
        
        .book-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .book-author {
            font-size: 16px;
            margin-bottom: 20px;
        }
        
        .book-cover-image {
            max-width: 150px;
            border-radius: 5px;
            margin: 20px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        .story-content {
            margin-top: 2rem;
            font-size: 1.1rem;
            line-height: 1.8;
        }
        
        @media (max-width: 768px) {
            .hero-section {
                padding: 3rem 0;
            }
            
            .book-container {
                height: 400px;
            }
            
            .book-bottom {
                transform: rotateX(-90deg) translateZ(360px);
            }
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center" href="/">
                <i class="bi bi-book me-2 fs-3"></i>
                <span class="fs-4">Storybook Magic</span>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">How It Works</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container">
        {{ content|safe }}
    </div>

    <footer class="mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <h5>Storybook Magic</h5>
                    <p>Creating personalized bedtime stories for children using the power of AI.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <p class="mb-0">© 2025 Storybook Magic. All rights reserved.</p>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# HTML template for the upload page
UPLOAD_TEMPLATE = """
{% block content %}
<div class="hero-section text-center mb-5">
    <div class="container">
        <h1 class="display-4 fw-bold mb-3">Create Magical Bedtime Stories</h1>
        <p class="lead mb-4">Upload a photo of your child and we'll create a personalized bedtime story featuring them as the main character!</p>
        <a href="#create-story" class="btn btn-primary btn-lg px-4">Get Started</a>
    </div>
</div>

<div class="row mb-5">
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <img src="https://images.unsplash.com/photo-1519340241574-2cec6aef0c01?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80" class="card-img-top" alt="Adventure">
            <div class="card-body">
                <h5 class="card-title">Adventure Stories</h5>
                <p class="card-text">Exciting journeys to magical lands where your child becomes the hero of their own adventure.</p>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <img src="https://images.unsplash.com/photo-1518826778770-a729fb53327c?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80" class="card-img-top" alt="Fantasy">
            <div class="card-body">
                <h5 class="card-title">Fantasy Tales</h5>
                <p class="card-text">Enchanted worlds with dragons, wizards, and magical creatures where imagination knows no bounds.</p>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <img src="https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80" class="card-img-top" alt="Space">
            <div class="card-body">
                <h5 class="card-title">Space Odysseys</h5>
                <p class="card-text">Interstellar journeys through the cosmos where your child explores distant planets and meets aliens.</p>
            </div>
        </div>
    </div>
</div>

<div class="form-container" id="create-story">
    <h2 class="text-center mb-4">Create Your Personalized Story</h2>
    <form action="/generate" method="post" enctype="multipart/form-data">
        <div class="mb-3">
            <label for="child_name" class="form-label">Child's Name</label>
            <input type="text" class="form-control" id="child_name" name="child_name" required>
        </div>
        <div class="mb-3">
            <label for="child_image" class="form-label">Upload a Photo</label>
            <input type="file" class="form-control" id="child_image" name="child_image" accept="image/*" required>
            <div class="form-text">We'll use this photo to personalize the story.</div>
        </div>
        <div class="mb-3">
            <label for="age_range" class="form-label">Age Range</label>
            <select class="form-select" id="age_range" name="age_range" required>
                <option value="2-4">2-4 years</option>
                <option value="4-6" selected>4-6 years</option>
                <option value="6-8">6-8 years</option>
                <option value="8-10">8-10 years</option>
            </select>
        </div>
        <div class="mb-3">
            <label for="theme" class="form-label">Story Theme</label>
            <select class="form-select" id="theme" name="theme" required>
                <option value="adventure">Adventure</option>
                <option value="fantasy">Fantasy</option>
                <option value="space">Space</option>
                <option value="underwater">Underwater</option>
                <option value="jungle">Jungle</option>
                <option value="superhero">Superhero</option>
            </select>
        </div>
        <div class="mb-3 form-check">
            <input type="checkbox" class="form-check-input" id="generate_illustrations" name="generate_illustrations" value="true" checked>
            <label class="form-check-label" for="generate_illustrations">Generate illustrations for the story</label>
        </div>
        <div class="mb-3 form-check">
            <input type="checkbox" class="form-check-input" id="rhyming" name="rhyming" value="true">
            <label class="form-check-label" for="rhyming">Create a rhyming bedtime story</label>
        </div>
        <div class="text-center">
            <button type="submit" class="btn btn-primary btn-lg px-4">Create Story</button>
        </div>
    </form>
</div>

<div class="row mb-5">
    <div class="col-md-12">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">How It Works</h5>
                <div class="row">
                    <div class="col-md-4 text-center mb-3">
                        <i class="bi bi-upload fs-1 text-primary"></i>
                        <h6 class="mt-2">1. Upload a Photo</h6>
                        <p class="text-muted">Upload a photo of your child and enter their name.</p>
                    </div>
                    <div class="col-md-4 text-center mb-3">
                        <i class="bi bi-magic fs-1 text-primary"></i>
                        <h6 class="mt-2">2. AI Magic Happens</h6>
                        <p class="text-muted">Our AI creates a personalized story featuring your child.</p>
                    </div>
                    <div class="col-md-4 text-center mb-3">
                        <i class="bi bi-book fs-1 text-primary"></i>
                        <h6 class="mt-2">3. Enjoy Your Story</h6>
                        <p class="text-muted">Read the unique story with your child at bedtime.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    // Form validation
    document.addEventListener('DOMContentLoaded', function() {
        const form = document.querySelector('form');
        form.addEventListener('submit', function(event) {
            const childName = document.getElementById('child_name').value;
            const childImage = document.getElementById('child_image').files[0];
            
            if (!childName || !childImage) {
                event.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
</script>
{% endblock %}
"""

# HTML template for the story page with 3D book
STORY_TEMPLATE = """
{% block content %}
<div class="story-container">
    <div class="row mb-4">
        <div class="col-md-8">
            <h1 class="mb-3">{{ child_name }}'s {{ theme|title }} Story</h1>
            <div class="d-flex gap-2 mb-4">
                <span class="badge bg-primary">{{ theme|title }}</span>
                <span class="badge bg-secondary">Age: {{ age_range }}</span>
                <span class="badge bg-info">AI-Generated</span>
                {% if rhyming %}
                <span class="badge bg-success">Rhyming</span>
                {% endif %}
            </div>
        </div>
        <div class="col-md-4 text-end">
            <a href="/" class="btn btn-outline-primary"><i class="bi bi-plus-circle me-2"></i>Create New Story</a>
        </div>
    </div>
    
    <div class="row">
        <div class="col-md-4 mb-4">
            <img src="{{ image_path }}" alt="{{ child_name }}" class="child-image img-fluid mb-3">
            <div class="d-grid gap-2">
                <a href="#" class="btn btn-primary print-story"><i class="bi bi-printer me-2"></i>Print Story</a>
                <a href="#" class="btn btn-outline-primary share-story"><i class="bi bi-share me-2"></i>Share Story</a>
            </div>
        </div>
        <div class="col-md-8">
            <!-- 3D Book Preview -->
            <div class="book-container">
                <div class="book">
                    <div class="book-front">
                        <div class="book-title">{{ child_name }}'s {{ theme|title }} Adventure</div>
                        <div class="book-author">A Personalized Story for Ages {{ age_range }}</div>
                        <img src="{{ image_path }}" alt="{{ child_name }}" class="book-cover-image">
                        <p>Hover to open the book</p>
                    </div>
                    <div class="book-back"></div>
                    <div class="book-spine"></div>
                    <div class="book-top"></div>
                    <div class="book-bottom"></div>
                    <div class="book-right"></div>
                </div>
            </div>
            
            <div class="story-content">
                {{ story_html|safe }}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Print functionality
        const printBtn = document.querySelector('.print-story');
        printBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
        
        // Share functionality (placeholder)
        const shareBtn = document.querySelector('.share-story');
        shareBtn.addEventListener('click', function(e) {
            e.preventDefault();
            alert('Sharing functionality coming soon!');
        });
        
        // 3D Book animation
        const book = document.querySelector('.book');
        let rotationY = -30;
        let rotationX = 0;
        
        // Automatic gentle rotation
        setInterval(() => {
            rotationY = -30 + Math.sin(Date.now() / 2000) * 10;
            rotationX = Math.sin(Date.now() / 3000) * 5;
            book.style.transform = `rotateY(${rotationY}deg) rotateX(${rotationX}deg)`;
        }, 50);
        
        // Reset rotation on hover
        book.addEventListener('mouseenter', function() {
            book.style.transform = 'rotateY(0deg) rotateX(0deg)';
        });
        
        book.addEventListener('mouseleave', function() {
            // Resume automatic rotation
        });
        
        // Ensure all images are loaded
        const images = document.querySelectorAll('.illustration-image');
        images.forEach(img => {
            img.addEventListener('error', function() {
                this.src = '/static/placeholder.jpg';
                this.alt = 'Image could not be loaded';
            });
        });
    });
</script>
{% endblock %}
"""

@app.route('/')
def home():
    """Render the home page."""
    # Use a simpler approach to render templates
    template = render_template_string(UPLOAD_TEMPLATE, page_title="Create Your Story | Storybook Magic")
    return render_template_string(MAIN_TEMPLATE, content=template)

@app.route('/generate', methods=['POST'])
def generate():
    """Generate a personalized story based on the uploaded image."""
    try:
        child_name = request.form.get('child_name', '')
        theme = request.form.get('theme', 'adventure')
        age_range = request.form.get('age_range', '4-6')
        generate_illustrations = request.form.get('generate_illustrations') == 'true'
        rhyming = request.form.get('rhyming') == 'true'
        
        logger.info(f"Generating story for {child_name}, theme: {theme}, age: {age_range}, illustrations: {generate_illustrations}, rhyming: {rhyming}")
        
        # Check if an image was uploaded
        if 'child_image' not in request.files or request.files['child_image'].filename == '':
            logger.error("No image uploaded")
            return "No image uploaded", 400
        
        # Save the uploaded image to a temporary file
        image_file = request.files['child_image']
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        image_file.save(temp_file.name)
        temp_file.close()
        temp_path = temp_file.name
        
        # Encode the image to base64
        image_data = encode_image(temp_path)
        
        # Get API key from environment variable
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            return "API key not configured", 500
        
        # Generate a Ghibli-style main image
        ghibli_image_path = generate_ghibli_style_image(image_data, api_key)
        if not ghibli_image_path:
            logger.warning("Failed to generate Ghibli-style image, using original image")
            ghibli_image_path = temp_path
        
        # Generate the story
        story = generate_story(child_name, image_data, theme, age_range, generate_illustrations, rhyming)
        
        # Store the story and image path
        story_id = str(int(time.time()))
        stories[story_id] = {
            'story': story,
            'image_path': ghibli_image_path,  # Use the Ghibli-style image
            'original_image_path': temp_path,  # Keep the original image as backup
            'child_name': child_name,
            'theme': theme,
            'age_range': age_range,
            'generate_illustrations': generate_illustrations,
            'rhyming': rhyming
        }
        
        # Generate illustrations if requested
        if generate_illustrations:
            # Extract illustration descriptions from the story
            descriptions = extract_illustration_descriptions(story)
            
            # Generate images for each description
            illustration_images[story_id] = []
            for desc in descriptions:
                # Generate image using OpenAI
                image_path = generate_illustration(desc, theme)
                
                if image_path:
                    # Create a unique ID for this illustration
                    illustration_id = str(uuid.uuid4())
                    illustration_images[story_id].append({
                        'id': illustration_id,
                        'description': desc,
                        'image_path': image_path
                    })
        
        return redirect(url_for('view_story', story_id=story_id))
    except Exception as e:
        logger.error(f"Error in generate route: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/story/<story_id>')
def view_story(story_id):
    """View a generated story."""
    try:
        if story_id not in stories:
            logger.error(f"Story not found: {story_id}")
            return "Story not found", 404
        
        story_data = stories[story_id]
        generate_illustrations = story_data.get('generate_illustrations', False)
        rhyming = story_data.get('rhyming', False)
        
        # Process the story to highlight illustration descriptions or replace with actual images
        story_html = story_data['story']
        
        if generate_illustrations and story_id in illustration_images:
            # Replace illustration descriptions with actual images
            for illustration in illustration_images[story_id]:
                desc = illustration['description']
                illustration_id = illustration['id']
                img_url = f"/illustration/{story_id}/{illustration_id}"
                img_tag = f'<div class="illustration"><img src="{img_url}" alt="{desc}" class="illustration-image" onerror="this.src=\'/static/placeholder.jpg\'; this.alt=\'Image could not be loaded\'"><p><i class="bi bi-image me-2"></i>{desc}</p></div>'
                story_html = story_html.replace(f'[ILLUSTRATION: {desc}]', img_tag)
        else:
            # Just highlight the illustration descriptions
            story_html = story_html.replace('[ILLUSTRATION:', '<div class="illustration"><i class="bi bi-image me-2"></i>[ILLUSTRATION:')
            story_html = story_html.replace(']', ']</div>')
        
        # Replace paragraphs with proper HTML
        story_html = story_html.replace('\n\n', '</p><p>')
        story_html = f'<p>{story_html}</p>'
        
        # Use a simpler approach to render templates
        template = render_template_string(
            STORY_TEMPLATE,
            story_html=story_html,
            image_path=f"/image/{story_id}",
            child_name=story_data['child_name'],
            theme=story_data['theme'],
            age_range=story_data['age_range'],
            rhyming=rhyming,
            page_title=f"{story_data['child_name']}'s Story | Storybook Magic"
        )
        
        return render_template_string(MAIN_TEMPLATE, content=template)
    except Exception as e:
        logger.error(f"Error in view_story route: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/image/<story_id>')
def get_image(story_id):
    """Serve the image associated with a story."""
    try:
        if story_id not in stories:
            logger.error(f"Story not found for image: {story_id}")
            return "Story not found", 404
        
        # Use the Ghibli-style image if available, otherwise fall back to original
        image_path = stories[story_id]['image_path']
        if not os.path.exists(image_path):
            logger.warning(f"Image not found at {image_path}, using original")
            image_path = stories[story_id]['original_image_path']
            
        return send_file(image_path)
    except Exception as e:
        logger.error(f"Error in get_image route: {str(e)}")
        return "Image not available", 404

@app.route('/illustration/<story_id>/<illustration_id>')
def get_illustration(story_id, illustration_id):
    """Serve an illustration image using a unique ID instead of description."""
    try:
        if story_id not in illustration_images:
            logger.error(f"Illustrations not found for story: {story_id}")
            return "Illustration not found", 404
        
        for illustration in illustration_images[story_id]:
            if illustration['id'] == illustration_id:
                image_path = illustration['image_path']
                if os.path.exists(image_path):
                    return send_file(image_path)
                else:
                    logger.error(f"Illustration file not found: {image_path}")
                    return "Illustration file not found", 404
        
        logger.error(f"Illustration ID not found: {illustration_id}")
        return "Illustration not found", 404
    except Exception as e:
        logger.error(f"Error in get_illustration route: {str(e)}")
        return "Illustration not available", 404

# Create a static directory for placeholder images
@app.route('/static/<filename>')
def static_files(filename):
    """Serve static files."""
    try:
        if filename == 'placeholder.jpg':
            # Return a simple placeholder image
            placeholder_path = os.path.join(tempfile.gettempdir(), 'placeholder.jpg')
            if not os.path.exists(placeholder_path):
                from PIL import Image, ImageDraw, ImageFont
                img = Image.new('RGB', (400, 300), color=(200, 200, 200))
                d = ImageDraw.Draw(img)
                d.text((150, 150), "Image not available", fill=(0, 0, 0))
                img.save(placeholder_path)
            return send_file(placeholder_path)
        return "File not found", 404
    except Exception as e:
        logger.error(f"Error in static_files route: {str(e)}")
        return "File not available", 404

if __name__ == '__main__':
    # Use the PORT environment variable provided by Render
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
