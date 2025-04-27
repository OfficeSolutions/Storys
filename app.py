import os
import tempfile
import time
import base64
import uuid
from flask import Flask, render_template_string, request, redirect, url_for, send_file, abort
from werkzeug.utils import secure_filename
from illustration_generator import generate_illustration_image

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# In-memory storage for stories and images
stories = {}
illustration_images = {}

# Get API keys from environment variables
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

def encode_image(image_path):
    """Encode an image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_story(child_name, image_data, theme, generate_illustrations=False):
    """Generate a personalized story based on the child's name, image, and theme."""
    try:
        import google.generativeai as genai
        
        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Create a prompt for the story
        prompt = f"""
        Create a personalized bedtime story for a child named {child_name}. 
        The story should be in the {theme} theme and should be appropriate for a young child.
        The story should be about 500-800 words long and should be divided into paragraphs.
        
        If the child appears in the uploaded image, incorporate their appearance into the story.
        
        Make the child the main character of the story.
        
        The story should have a clear beginning, middle, and end, with a positive message or lesson.
        
        {"Include 3-5 places in the story where illustrations would be appropriate. Mark these with [ILLUSTRATION: brief description of the illustration]." if generate_illustrations else ""}
        """
        
        # Generate the story using Gemini API
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_data}])
        
        return response.text
    except Exception as e:
        # Fallback to a simple story if the API fails
        print(f"Error generating story: {str(e)}")
        return f"""
        # {child_name}'s {theme.title()} Adventure

        Once upon a time, there was a child named {child_name} who loved {theme} adventures.
        
        One day, {child_name} discovered a magical door that led to a world of {theme}.
        
        {"[ILLUSTRATION: A child standing in front of a magical glowing door]" if generate_illustrations else ""}
        
        In this world, {child_name} met friendly creatures who became their guides.
        
        {"[ILLUSTRATION: The child meeting magical creatures in a fantastical landscape]" if generate_illustrations else ""}
        
        After many exciting adventures, {child_name} learned the importance of courage and friendship.
        
        {"[ILLUSTRATION: The child waving goodbye to their new friends as they return home]" if generate_illustrations else ""}
        
        When {child_name} returned home, they couldn't wait to share their amazing story with everyone.
        
        The End.
        """

def extract_illustration_descriptions(story):
    """Extract illustration descriptions from the story."""
    import re
    
    # Find all illustration descriptions in the story
    pattern = r'\[ILLUSTRATION: (.*?)\]'
    matches = re.findall(pattern, story)
    
    return matches

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
            --primary-color: #6a11cb;
            --secondary-color: #2575fc;
            --accent-color: #ff7eb3;
            --light-color: #f8f9fa;
            --dark-color: #343a40;
        }
        
        body {
            font-family: 'Nunito', sans-serif;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            min-height: 100vh;
            color: var(--light-color);
        }
        
        .navbar {
            background-color: rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
        }
        
        .hero-section {
            padding: 5rem 0;
            background: rgba(0, 0, 0, 0.1);
            border-radius: 1rem;
            margin: 2rem 0;
        }
        
        .card {
            border-radius: 1rem;
            overflow: hidden;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
            height: 100%;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card-img-top {
            height: 200px;
            object-fit: cover;
        }
        
        .form-container {
            background-color: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 1rem;
            padding: 2rem;
            margin: 2rem 0;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            border: none;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        .btn-light {
            background-color: var(--light-color);
            color: var(--primary-color);
            font-weight: bold;
        }
        
        footer {
            background-color: rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
            padding: 2rem 0;
            margin-top: 3rem;
        }
        
        .story-container {
            background-color: white;
            color: var(--dark-color);
            border-radius: 1rem;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .child-image {
            border-radius: 1rem;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            max-width: 100%;
            height: auto;
        }
        
        .illustration {
            background-color: #f8f9fa;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1.5rem 0;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        }
        
        .illustration-image {
            max-width: 100%;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        @media (max-width: 768px) {
            .hero-section {
                padding: 3rem 0;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
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
        {{ content|safe }}
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
        <a href="#create-story" class="btn btn-light btn-lg px-4 me-md-2">Get Started</a>
    </div>
</div>

<div class="row mb-5">
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <img src="https://source.unsplash.com/random/300x200/?child,adventure" class="card-img-top" alt="Adventure">
            <div class="card-body">
                <h5 class="card-title">Adventure Stories</h5>
                <p class="card-text">Exciting journeys to magical lands where your child becomes the hero of their own adventure.</p>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <img src="https://source.unsplash.com/random/300x200/?child,fantasy" class="card-img-top" alt="Fantasy">
            <div class="card-body">
                <h5 class="card-title">Fantasy Tales</h5>
                <p class="card-text">Enchanted worlds with dragons, wizards, and magical creatures where imagination knows no bounds.</p>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-4">
        <div class="card h-100">
            <img src="https://source.unsplash.com/random/300x200/?child,space" class="card-img-top" alt="Space">
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
            <div class="form-text text-light">We'll use this photo to personalize the story.</div>
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
            <input type="checkbox" class="form-check-input" id="generate_illustrations" name="generate_illustrations" value="true">
            <label class="form-check-label" for="generate_illustrations">Generate illustrations for the story</label>
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

# HTML template for the story page
STORY_TEMPLATE = """
{% block content %}
<div class="story-container">
    <div class="row mb-4">
        <div class="col-md-8">
            <h1 class="mb-3">{{ child_name }}'s {{ theme|title }} Story</h1>
            <div class="d-flex gap-2 mb-4">
                <span class="badge bg-primary">{{ theme|title }}</span>
                <span class="badge bg-secondary">Personalized</span>
                <span class="badge bg-info">AI-Generated</span>
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
                <a href="#" class="btn btn-primary"><i class="bi bi-printer me-2"></i>Print Story</a>
                <a href="#" class="btn btn-outline-primary"><i class="bi bi-share me-2"></i>Share Story</a>
            </div>
        </div>
        <div class="col-md-8">
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
        const printBtn = document.querySelector('.btn-primary');
        printBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
        
        // Share functionality (placeholder)
        const shareBtn = document.querySelector('.btn-outline-primary');
        shareBtn.addEventListener('click', function(e) {
            e.preventDefault();
            alert('Sharing functionality coming soon!');
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
    child_name = request.form.get('child_name', '')
    theme = request.form.get('theme', 'adventure')
    generate_illustrations = request.form.get('generate_illustrations') == 'true'
    
    # Check if an image was uploaded
    if 'child_image' not in request.files or request.files['child_image'].filename == '':
        return "No image uploaded", 400
    
    # Save the uploaded image to a temporary file
    image_file = request.files['child_image']
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
            # Try to generate image using both APIs with fallback
            image_path = generate_illustration_image(
                desc, 
                theme, 
                openai_api_key=OPENAI_API_KEY, 
                gemini_api_key=GEMINI_API_KEY
            )
            
            if image_path:
                illustration_images[story_id].append({
                    'description': desc,
                    'image_path': image_path
                })
    
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
        page_title=f"{story_data['child_name']}'s Story | Storybook Magic"
    )
    
    return render_template_string(MAIN_TEMPLATE, content=template)

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
    app.run(host='0.0.0.0', port=8080, debug=True)
