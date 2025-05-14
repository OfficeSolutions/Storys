import os
import tempfile
import time
import base64
import uuid
import urllib.parse
import logging
import re # Added re import
from flask import Flask, render_template_string, request, redirect, url_for, send_file, abort
from werkzeug.utils import secure_filename
from enhanced_story_generator import (
    generate_story, 
    generate_illustration, 
    extract_illustration_descriptions,
    generate_ghibli_style_image
)

# Set up logging
logging.basicConfig(level=logging.INFO, format=\'%(asctime)s - %(levelname)s - %(message)s\')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload size

# In-memory storage for stories and images
stories = {}
illustration_images = {}

def encode_image(image_path):
    """Encode an image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# HTML template for the main layout
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title|default("Storybook Magic") }}</title>
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
            font-family: "Nunito", sans-serif;
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
{% extends "main_layout" %}
{% block content %}
<div class="hero-section text-center mb-5">
    <div class="container">
        <h1 class="display-4 fw-bold mb-3">Create Magical Bedtime Stories</h1>
        <p class="lead mb-4">Upload a photo of your child and we\'ll create a personalized bedtime story featuring them as the main character!</p>
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
            <label for="child_name" class="form-label">Child\'s Name</label>
            <input type="text" class="form-control" id="child_name" name="child_name" required>
        </div>
        <div class="mb-3">
            <label for="child_image" class="form-label">Upload a Photo</label>
            <input type="file" class="form-control" id="child_image" name="child_image" accept="image/*" required>
            <div class="form-text">We\'ll use this photo to personalize the story.</div>
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
    const form = document.querySelector("form");
    form.addEventListener("submit", function(event) {
        const childName = document.getElementById("child_name").value;
        const childImage = document.getElementById("child_image").files;
        if (!childName.trim()) {
            alert("Please enter the child\'s name.");
            event.preventDefault();
            return;
        }
        if (childImage.length === 0) {
            alert("Please upload a photo of the child.");
            event.preventDefault();
            return;
        }
    });
</script>
{% endblock %}
"""

# HTML template for the story page
STORY_TEMPLATE = """
{% extends "main_layout" %}
{% block content %}
<div class="story-container">
    <div class="row mb-4">
        <div class="col-md-8">
            <h1 class="mb-3">{{ child_name }}\'s {{ theme|title }} Story</h1>
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
                        <div class="book-title">{{ child_name }}\'s {{ theme|title }} Adventure</div>
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
    document.addEventListener("DOMContentLoaded", function() {
        const printButton = document.querySelector(".print-story");
        if (printButton) {
            printButton.addEventListener("click", function(event) {
                event.preventDefault();
                window.print();
            });
        }

        const shareButton = document.querySelector(".share-story");
        if (shareButton) {
            shareButton.addEventListener("click", function(event) {
                event.preventDefault();
                if (navigator.share) {
                    navigator.share({
                        title: document.title,
                        text: "Check out this personalized story I created!",
                        url: window.location.href
                    }).then(() => {
                        console.log("Thanks for sharing!");
                    }).catch(console.error);
                } else {
                    // Fallback for browsers that don\'t support navigator.share
                    alert("Sharing is not supported on this browser, but you can copy the URL!");
                }
            });
        }
    });
</script>
{% endblock %}
"""

@app.route("/")
def index():
    content = render_template_string(UPLOAD_TEMPLATE)
    return render_template_string(MAIN_TEMPLATE, content=content, page_title="Create Your Story - Storybook Magic")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        child_name = request.form["child_name"]
        child_image_file = request.files["child_image"]
        age_range = request.form["age_range"]
        theme = request.form["theme"]
        generate_illustrations_flag = request.form.get("generate_illustrations") == "true"
        rhyming_flag = request.form.get("rhyming") == "true"

        if not child_image_file or child_image_file.filename == "":
            return "No image file provided", 400

        filename = secure_filename(child_image_file.filename if child_image_file.filename else "uploaded_image")
        temp_dir = tempfile.mkdtemp()
        image_path = os.path.join(temp_dir, filename)
        child_image_file.save(image_path)

        with open(image_path, "rb") as f:
            image_data_base64 = base64.b64encode(f.read()).decode("utf-8")

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set.")
            return "Server configuration error: API key not set.", 500

        # Generate Ghibli-style image for the cover
        ghibli_image_path = generate_ghibli_style_image(image_data_base64, api_key)
        if not ghibli_image_path:
            logger.warning("Failed to generate Ghibli-style image, using original image as fallback.")
            ghibli_image_path = image_path # Fallback to original if Ghibli fails

        story_text = generate_story(
            child_name, 
            image_data_base64, 
            theme, 
            age_range, 
            generate_illustrations_flag,
            rhyming_flag
        )

        story_id = str(uuid.uuid4())
        stories[story_id] = {
            "child_name": child_name,
            "theme": theme,
            "age_range": age_range,
            "story_text": story_text, # Store raw story text with placeholders
            "image_path": url_for("get_uploaded_image", story_id=story_id, filename=os.path.basename(ghibli_image_path)),
            "original_image_path": image_path, # Store path to original for Ghibli fallback
            "ghibli_image_path": ghibli_image_path, # Store path to Ghibli image
            "generate_illustrations": generate_illustrations_flag,
            "rhyming": rhyming_flag
        }

        # Generate illustrations if requested and replace placeholders
        story_html = story_text # Start with the raw story text
        if generate_illustrations_flag:
            illustration_descriptions = extract_illustration_descriptions(story_text)
            generated_illustration_paths_urls = [] # URLs for the template
            
            if not api_key: # This check is redundant if already checked above, but good for safety
                logger.error("OPENAI_API_KEY not found for illustrations. Cannot generate.")
            else:
                for i, desc in enumerate(illustration_descriptions):
                    logger.info(f"Requesting illustration for: {desc}")
                    # Corrected call: Pass api_key, not theme
                    illustration_path = generate_illustration(desc, api_key) 
                    if illustration_path:
                        img_id = f"{story_id}_illustration_{i}"
                        illustration_images[img_id] = illustration_path # Store the actual file path
                        generated_illustration_paths_urls.append(url_for("get_illustration_image", image_id=img_id))
                        logger.info(f"Illustration {i} generated: {illustration_path}, URL: {generated_illustration_paths_urls[-1]}")
                    else:
                        generated_illustration_paths_urls.append(None)
                        logger.warning(f"Failed to generate illustration for: {desc}")

            # Replace placeholders in story with actual image tags or placeholders
            story_html_parts = story_text.split("[ILLUSTRATION:")
            processed_html = story_html_parts[0]
            for i, part in enumerate(story_html_parts[1:]):
                try:
                    desc_and_rest = part.split("]", 1)
                    original_desc_text = desc_and_rest[0]
                    rest_of_story = desc_and_rest[1]
                    
                    if i < len(generated_illustration_paths_urls) and generated_illustration_paths_urls[i]:
                        processed_html += f'<div class="illustration"><img src="{generated_illustration_paths_urls[i]}" alt="Illustration: {original_desc_text}" class="illustration-image"><p class="text-muted"><em>{original_desc_text}</em></p></div>'
                    else:
                        processed_html += f'<div class="illustration"><p class="text-danger"><em>Illustration for \"{original_desc_text}\" could not be generated.</em></p></div>'
                    processed_html += rest_of_story
                except IndexError:
                    processed_html += part # Append the remainder if parsing fails
            story_html = processed_html
        else:
            # Remove illustration placeholders if not generating
            story_html = re.sub(r\'\[ILLUSTRATION: (.*?)\]\', \'\', story_text)

        # Store the final HTML (with illustrations or removed placeholders)
        stories[story_id]["story_html_final"] = story_html

        return redirect(url_for("show_story", story_id=story_id))

    except Exception as e:
        logger.error(f"Error in /generate: {str(e)}", exc_info=True)
        # You might want to render an error page here
        return f"An error occurred: {str(e)}", 500

@app.route("/story/<story_id>")
def show_story(story_id):
    story_data = stories.get(story_id)
    if not story_data:
        abort(404)
    
    story_html_final = story_data.get("story_html_final", story_data["story_text"]) # Fallback to raw if not processed

    content = render_template_string(
        STORY_TEMPLATE, 
        child_name=story_data["child_name"],
        theme=story_data["theme"],
        age_range=story_data["age_range"],
        story_html=story_html_final,
        image_path=story_data["image_path"],
        rhyming=story_data.get("rhyming", False)
    )
    return render_template_string(MAIN_TEMPLATE, content=content, page_title=f"{story_data["child_name"]}\'s Story - Storybook Magic")

@app.route("/image/<story_id>/<filename>")
def get_uploaded_image(story_id, filename):
    story_data = stories.get(story_id)
    if not story_data:
        abort(404)
    # Determine if it's the Ghibli image or the original upload
    # The filename in image_path is already the basename of the Ghibli image (or original if Ghibli failed)
    image_to_serve = story_data.get("ghibli_image_path")
    if not image_to_serve or os.path.basename(image_to_serve) != filename:
        # This case should ideally not happen if image_path is set correctly
        # but as a fallback, try original if ghibli_image_path is missing or filename doesn't match
        image_to_serve = story_data.get("original_image_path")
        if not image_to_serve or os.path.basename(image_to_serve) != filename:
             abort(404)

    if not os.path.exists(image_to_serve):
        logger.error(f"Image file not found: {image_to_serve}")
        abort(404)
    return send_file(image_to_serve)

@app.route("/illustration/<image_id>")
def get_illustration_image(image_id):
    image_path = illustration_images.get(image_id)
    if not image_path or not os.path.exists(image_path):
        logger.error(f"Illustration image not found for ID: {image_id}, Path: {image_path}")
        abort(404)
    return send_file(image_path)

if __name__ == "__main__":
    # Ensure OPENAI_API_KEY is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        exit(1)
    app.run(host="0.0.0.0", port=10000, debug=False)

