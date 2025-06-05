import os
import tempfile
import uuid
import base64
import re
import json
import logging
import time
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template_string, redirect, url_for, send_file, jsonify, abort, send_from_directory

from enhanced_story_generator import (
    generate_story,
    generate_story_image,
    PERSISTENT_IMAGE_DIR
)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure Flask for URL generation outside request context
app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME', 'storys.onrender.com')
app.config['APPLICATION_ROOT'] = os.environ.get('APPLICATION_ROOT', '/')
app.config['PREFERRED_URL_SCHEME'] = os.environ.get('PREFERRED_URL_SCHEME', 'https')

# Ensure the static directory exists
os.makedirs(PERSISTENT_IMAGE_DIR, exist_ok=True)

# In-memory storage for stories
stories = {}
story_progress = {}

# Templates
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.3/font/bootstrap-icons.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Open+Sans:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <style>
        :root {
            --primary: #4361ee;
            --secondary: #3f37c9;
            --accent: #4cc9f0;
            --background: #f8f9fa;
            --text: #212529;
            --white: #ffffff;
            --border-radius: 8px;
        }
        
        body {
            font-family: 'Open Sans', sans-serif;
            background-color: var(--background);
            color: var(--text);
            line-height: 1.6;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Montserrat', sans-serif;
            font-weight: 600;
        }
        
        .navbar {
            background-color: var(--white);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            padding: 1rem 0;
        }
        
        .navbar-brand {
            font-weight: 700;
            color: var(--primary);
            font-family: 'Montserrat', sans-serif;
        }
        
        .nav-link {
            font-weight: 500;
            color: var(--text);
            transition: color 0.3s ease;
        }
        
        .nav-link:hover {
            color: var(--primary);
        }
        
        .hero-section {
            background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
            padding: 6rem 0;
            border-radius: 0 0 var(--border-radius) var(--border-radius);
            margin-bottom: 4rem;
            color: var(--white);
        }
        
        .hero-title {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
        }
        
        .hero-subtitle {
            font-size: 1.3rem;
            margin-bottom: 2.5rem;
            opacity: 0.9;
        }
        
        .btn-primary {
            background-color: var(--accent);
            border-color: var(--accent);
            padding: 0.75rem 2rem;
            font-weight: 600;
            border-radius: var(--border-radius);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .btn-primary:hover {
            background-color: var(--accent);
            border-color: var(--accent);
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        .form-container {
            background-color: var(--white);
            border-radius: var(--border-radius);
            padding: 2.5rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            margin-bottom: 4rem;
        }
        
        .form-label {
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--text);
        }
        
        .form-control {
            border-radius: var(--border-radius);
            padding: 0.75rem 1rem;
            border: 1px solid #dee2e6;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        
        .form-control:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 0.25rem rgba(67, 97, 238, 0.25);
        }
        
        .form-select {
            border-radius: var(--border-radius);
            padding: 0.75rem 1rem;
            border: 1px solid #dee2e6;
        }
        
        .story-container {
            margin-bottom: 4rem;
        }
        
        .story-image-container {
            position: relative;
            margin-bottom: 2rem;
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        }
        
        .story-image {
            width: 100%;
            border-radius: var(--border-radius);
            transition: transform 0.5s ease;
        }
        
        .story-image:hover {
            transform: scale(1.02);
        }
        
        .story-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            color: var(--primary);
        }
        
        .step-indicator {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            margin-right: 10px;
        }
        
        .step-indicator.completed {
            background-color: rgba(25, 135, 84, 0.1);
        }
        
        .step-indicator.active {
            background-color: rgba(13, 110, 253, 0.1);
        }
        
        .progress-message {
            font-size: 1.2rem;
            margin-bottom: 1rem;
        }
        
        .progress-steps {
            margin-top: 2rem;
        }
        
        .modal-content {
            border-radius: var(--border-radius);
            border: none;
        }
        
        .modal-header {
            border-bottom: none;
            padding: 1.5rem 1.5rem 0.5rem;
        }
        
        .modal-body {
            padding: 1.5rem;
        }
        
        .progress {
            height: 10px;
            border-radius: 5px;
        }
        
        .progress-bar {
            background-color: var(--primary);
        }
        
        @media (max-width: 768px) {
            .hero-section {
                padding: 4rem 0;
            }
            
            .hero-title {
                font-size: 2.2rem;
            }
            
            .form-container {
                padding: 1.5rem;
            }
            
            .story-title {
                font-size: 2rem;
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

    <!-- Progress Modal -->
    <div class="modal fade progress-modal" id="progressModal" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="progressModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="progressModalLabel">Creating Your Story</h5>
                </div>
                <div class="modal-body">
                    <div class="progress-message text-center mb-4" id="progressMessage">Preparing your story...</div>
                    
                    <div class="progress mb-4" style="height: 10px;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" id="progressBar" role="progressbar" 
                             style="width: 10%;" 
                             aria-valuenow="10" aria-valuemin="0" aria-valuemax="100">
                            10%
                        </div>
                    </div>
                    
                    <div class="progress-steps">
                        <div class="d-flex align-items-center mb-3">
                            <div class="step-indicator completed me-2" id="step1Indicator">
                                <i class="bi bi-check-circle-fill text-success" id="step1Icon"></i>
                            </div>
                            <span>Preparing your story</span>
                        </div>
                        
                        <div class="d-flex align-items-center mb-3">
                            <div class="step-indicator me-2" id="step2Indicator">
                                <i class="bi bi-circle text-secondary" id="step2Icon"></i>
                            </div>
                            <span>Analyzing image</span>
                        </div>
                        
                        <div class="d-flex align-items-center mb-3">
                            <div class="step-indicator me-2" id="step3Indicator">
                                <i class="bi bi-circle text-secondary" id="step3Icon"></i>
                            </div>
                            <span>Creating story</span>
                        </div>
                        
                        <div class="d-flex align-items-center mb-3">
                            <div class="step-indicator me-2" id="step4Indicator">
                                <i class="bi bi-circle text-secondary" id="step4Icon"></i>
                            </div>
                            <span>Generating story image</span>
                        </div>
                        
                        <div class="d-flex align-items-center">
                            <div class="step-indicator me-2" id="step5Indicator">
                                <i class="bi bi-circle text-secondary" id="step5Icon"></i>
                            </div>
                            <span>Finalizing</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize Bootstrap components
            try {
                // Initialize all Bootstrap tooltips
                var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
                var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                    return new bootstrap.Tooltip(tooltipTriggerEl)
                });
                
                console.log('Bootstrap components initialized successfully');
            } catch (error) {
                console.error('Error initializing Bootstrap components:', error);
            }
            
            // Progress bar functionality
            const storyForm = document.getElementById('storyForm');
            if (storyForm) {
                console.log('Story form found, setting up event listeners');
                
                // Try to initialize the modal
                let progressModal;
                try {
                    progressModal = new bootstrap.Modal(document.getElementById('progressModal'));
                    console.log('Progress modal initialized successfully');
                } catch (error) {
                    console.error('Error initializing progress modal:', error);
                }
                
                let sessionId = null;
                let pollingInterval = null;
                
                storyForm.addEventListener('submit', function(e) {
                    console.log('Form submitted');
                    e.preventDefault();
                    
                    // Show progress modal immediately
                    try {
                        if (progressModal) {
                            progressModal.show();
                            console.log('Progress modal shown');
                        } else {
                            // Fallback if modal initialization failed
                            document.getElementById('progressModal').classList.add('show');
                            document.getElementById('progressModal').style.display = 'block';
                            console.log('Progress modal shown using fallback method');
                        }
                    } catch (error) {
                        console.error('Error showing progress modal:', error);
                    }
                    
                    // Create FormData object
                    const formData = new FormData(storyForm);
                    
                    // Submit form via AJAX
                    fetch('/generate_ajax', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => {
                        console.log('Response received:', response);
                        return response.json();
                    })
                    .then(data => {
                        console.log('Data received:', data);
                        if (data.error) {
                            alert('Error: ' + data.error);
                            if (progressModal) progressModal.hide();
                            return;
                        }
                        
                        // Store session ID for polling
                        sessionId = data.session_id;
                        console.log('Session ID:', sessionId);
                        
                        // Start polling for progress updates
                        startProgressPolling(sessionId);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('An error occurred while submitting the form. Please try again.');
                        if (progressModal) progressModal.hide();
                    });
                });
                
                function startProgressPolling(sessionId) {
                    console.log('Starting progress polling for session:', sessionId);
                    // Clear any existing interval
                    if (pollingInterval) {
                        clearInterval(pollingInterval);
                    }
                    
                    // Poll every 1.5 seconds
                    pollingInterval = setInterval(() => {
                        fetch('/progress_status/' + sessionId)
                        .then(response => response.json())
                        .then(data => {
                            console.log('Progress update:', data);
                            updateProgressUI(data);
                            
                            // If complete, redirect to story page
                            if (data.status === 'complete') {
                                clearInterval(pollingInterval);
                                console.log('Story generation complete, redirecting to:', data.redirect_url);
                                window.location.href = data.redirect_url;
                            }
                            
                            // If error, show error and stop polling
                            if (data.status === 'error') {
                                clearInterval(pollingInterval);
                                alert('Error: ' + data.message);
                                if (progressModal) progressModal.hide();
                            }
                        })
                        .catch(error => {
                            console.error('Error polling progress:', error);
                        });
                    }, 1500);
                }
                
                function updateProgressUI(data) {
                    // Update progress bar
                    const progressBar = document.getElementById('progressBar');
                    if (progressBar) {
                        progressBar.style.width = data.progress + '%';
                        progressBar.setAttribute('aria-valuenow', data.progress);
                        progressBar.textContent = data.progress + '%';
                    }
                    
                    // Update message
                    const progressMessage = document.getElementById('progressMessage');
                    if (progressMessage) {
                        progressMessage.textContent = data.message;
                    }
                    
                    // Update step indicators
                    updateStepIndicator(data.step);
                }
                
                function updateStepIndicator(currentStep) {
                    // Reset all steps
                    for (let i = 1; i <= 5; i++) {
                        const indicator = document.getElementById('step' + i + 'Indicator');
                        const icon = document.getElementById('step' + i + 'Icon');
                        
                        if (indicator && icon) {
                            indicator.classList.remove('completed', 'active');
                            icon.classList.remove('bi-check-circle-fill', 'bi-circle-fill', 'text-success', 'text-primary');
                            icon.classList.add('bi-circle', 'text-secondary');
                        }
                    }
                    
                    // Mark completed steps
                    for (let i = 1; i < currentStep; i++) {
                        const indicator = document.getElementById('step' + i + 'Indicator');
                        const icon = document.getElementById('step' + i + 'Icon');
                        
                        if (indicator && icon) {
                            indicator.classList.add('completed');
                            icon.classList.remove('bi-circle', 'text-secondary');
                            icon.classList.add('bi-check-circle-fill', 'text-success');
                        }
                    }
                    
                    // Mark current step
                    const currentIndicator = document.getElementById('step' + currentStep + 'Indicator');
                    const currentIcon = document.getElementById('step' + currentStep + 'Icon');
                    
                    if (currentIndicator && currentIcon) {
                        currentIndicator.classList.add('active');
                        currentIcon.classList.remove('bi-circle', 'text-secondary');
                        currentIcon.classList.add('bi-circle-fill', 'text-primary');
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

HOME_TEMPLATE = """
<section class="hero-section">
    <div class="container">
        <div class="row align-items-center">
            <div class="col-lg-7">
                <h1 class="hero-title">Create Magical Stories for Your Child</h1>
                <p class="hero-subtitle">Upload a photo of your child and watch as they become the star of their very own personalized adventure.</p>
                <a href="#create-story" class="btn btn-primary btn-lg">Create a Story Now</a>
            </div>
            <div class="col-lg-5">
                <img src="https://images.unsplash.com/photo-1512253022256-19f1cd262b51?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=600&q=80" alt="Child reading a book" class="img-fluid rounded-3 shadow">
            </div>
        </div>
    </div>
</section>

<section id="create-story" class="py-5">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="form-container">
                    <h2 class="text-center mb-4">Create Your Personalized Story</h2>
                    <form id="storyForm" enctype="multipart/form-data">
                        <div class="mb-4">
                            <label for="childName" class="form-label">Child's Name</label>
                            <input type="text" class="form-control" id="childName" name="childName" required>
                        </div>
                        
                        <div class="mb-4">
                            <label for="childImage" class="form-label">Upload a Photo</label>
                            <input type="file" class="form-control" id="childImage" name="childImage" accept="image/*" required>
                            <div class="form-text">Upload a clear photo of your child's face for the best results.</div>
                        </div>
                        
                        <div class="mb-4">
                            <label for="theme" class="form-label">Story Theme</label>
                            <select class="form-select" id="theme" name="theme" required>
                                <option value="space adventure">Space Adventure</option>
                                <option value="underwater exploration">Underwater Exploration</option>
                                <option value="enchanted forest">Enchanted Forest</option>
                                <option value="dinosaur discovery">Dinosaur Discovery</option>
                                <option value="magical kingdom">Magical Kingdom</option>
                                <option value="pirate treasure">Pirate Treasure</option>
                                <option value="jungle safari">Jungle Safari</option>
                                <option value="superhero mission">Superhero Mission</option>
                            </select>
                        </div>
                        
                        <div class="mb-4">
                            <label for="ageRange" class="form-label">Age Range</label>
                            <select class="form-select" id="ageRange" name="ageRange">
                                <option value="2-4">2-4 years</option>
                                <option value="4-6" selected>4-6 years</option>
                                <option value="6-8">6-8 years</option>
                                <option value="8-10">8-10 years</option>
                            </select>
                        </div>
                        
                        <div class="mb-4 form-check">
                            <input type="checkbox" class="form-check-input" id="rhyming" name="rhyming">
                            <label class="form-check-label" for="rhyming">Make it rhyme</label>
                        </div>
                        
                        <div class="text-center">
                            <button type="submit" class="btn btn-primary btn-lg px-5">Create Story</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</section>
"""

STORY_TEMPLATE = """
<div class="row justify-content-center">
    <div class="col-lg-10">
        <div class="story-container">
            <h1 class="story-title text-center mb-4">{{ title }}</h1>
            
            <div class="story-image-container">
                <img src="{{ story_image_url }}" alt="{{ title }}" class="story-image img-fluid">
            </div>
            
            <div class="text-center mt-4">
                <a href="/" class="btn btn-primary">Create Another Story</a>
            </div>
        </div>
    </div>
</div>
"""

@app.route('/')
def home():
    """Render the home page."""
    content = HOME_TEMPLATE
    return render_template_string(MAIN_TEMPLATE, page_title="Storybook Magic - Create Personalized Stories", content=content)

@app.route('/generate', methods=['POST'])
def generate():
    """Generate a personalized story based on form inputs."""
    try:
        # Get form data
        child_name = request.form.get('childName', '')
        theme = request.form.get('theme', 'space adventure')
        age_range = request.form.get('ageRange', '4-6')
        rhyming = 'rhyming' in request.form
        
        # Get uploaded image
        if 'childImage' not in request.files:
            return "No file uploaded", 400
        
        file = request.files['childImage']
        if file.filename == '':
            return "No file selected", 400
        
        # Create a unique ID for this story
        story_id = str(uuid.uuid4())
        
        # Create a session ID for progress tracking
        session_id = str(uuid.uuid4())
        
        # Store the story data
        stories[story_id] = {
            'child_name': child_name,
            'theme': theme,
            'age_range': age_range,
            'rhyming': rhyming,
            'session_id': session_id,
            'status': 'pending'
        }
        
        # Initialize progress tracking
        story_progress[session_id] = {
            'progress': 10,
            'message': 'Preparing your story...',
            'step': 1,
            'status': 'processing'
        }
        
        # Read and encode the image
        image_data = base64.b64encode(file.read()).decode('utf-8')
        stories[story_id]['image_data'] = image_data
        
        # Start processing in a background thread
        import threading
        thread = threading.Thread(target=process_story_background, args=(story_id,))
        thread.daemon = True
        thread.start()
        
        # Redirect to progress page
        return redirect(url_for('progress', session_id=session_id))
        
    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/generate_ajax', methods=['POST'])
def generate_ajax():
    """AJAX endpoint for generating a personalized story."""
    try:
        # Get form data
        child_name = request.form.get('childName', '')
        theme = request.form.get('theme', 'space adventure')
        age_range = request.form.get('ageRange', '4-6')
        rhyming = 'rhyming' in request.form
        
        # Get uploaded image
        if 'childImage' not in request.files:
            return jsonify({'error': 'No file uploaded'})
        
        file = request.files['childImage']
        if file.filename == '':
            return jsonify({'error': 'No file selected'})
        
        # Create a unique ID for this story
        story_id = str(uuid.uuid4())
        
        # Create a session ID for progress tracking
        session_id = str(uuid.uuid4())
        
        # Store the story data
        stories[story_id] = {
            'child_name': child_name,
            'theme': theme,
            'age_range': age_range,
            'rhyming': rhyming,
            'session_id': session_id,
            'status': 'pending',
            'story_id': story_id
        }
        
        # Initialize progress tracking
        story_progress[session_id] = {
            'progress': 10,
            'message': 'Preparing your story...',
            'step': 1,
            'status': 'processing'
        }
        
        # Read and encode the image
        image_data = base64.b64encode(file.read()).decode('utf-8')
        stories[story_id]['image_data'] = image_data
        
        # Start processing in a background thread
        import threading
        thread = threading.Thread(target=process_story_background, args=(story_id,))
        thread.daemon = True
        thread.start()
        
        # Return session ID for polling
        return jsonify({
            'session_id': session_id,
            'message': 'Story generation started'
        })
        
    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        return jsonify({'error': str(e)})

@app.route('/progress/<session_id>')
def progress(session_id):
    """Show progress page for story generation."""
    if session_id not in story_progress:
        return "Invalid session ID", 404
    
    progress_data = story_progress[session_id]
    
    content = f"""
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-body text-center">
                        <h2 class="mb-4">Creating Your Story</h2>
                        <p class="lead mb-4">{progress_data['message']}</p>
                        
                        <div class="progress mb-4">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" 
                                 style="width: {progress_data['progress']}%;" 
                                 aria-valuenow="{progress_data['progress']}" aria-valuemin="0" aria-valuemax="100">
                                {progress_data['progress']}%
                            </div>
                        </div>
                        
                        <p class="text-muted">Please don't close this page. Your story is being created...</p>
                        
                        <script>
                            // Auto-refresh every 2 seconds
                            setTimeout(function() {{
                                window.location.reload();
                            }}, 2000);
                        </script>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    # If complete, redirect to story page
    if progress_data['status'] == 'complete' and 'story_id' in progress_data:
        return redirect(url_for('story', story_id=progress_data['story_id']))
    
    return render_template_string(MAIN_TEMPLATE, page_title="Creating Your Story - Storybook Magic", content=content)

@app.route('/progress_status/<session_id>')
def progress_status(session_id):
    """AJAX endpoint for getting progress status."""
    if session_id not in story_progress:
        return jsonify({
            'error': 'Invalid session ID',
            'status': 'error'
        })
    
    progress_data = story_progress[session_id].copy()
    
    # Add redirect URL if complete
    if progress_data['status'] == 'complete' and 'story_id' in progress_data:
        progress_data['redirect_url'] = url_for('story', story_id=progress_data['story_id'])
    
    return jsonify(progress_data)

@app.route('/story/<story_id>')
def story(story_id):
    """Show the generated story."""
    if story_id not in stories:
        return "Story not found", 404
    
    story_data = stories[story_id]
    
    if 'story_text' not in story_data or 'story_image' not in story_data:
        return "Story generation in progress", 202
    
    # Extract title from story text
    title = story_data.get('child_name', '') + "'s Adventure"
    story_text = story_data['story_text']
    
    # Look for markdown title format
    lines = story_text.split('\n')
    for line in lines:
        if line.startswith('# '):
            title = line.replace('# ', '')
            break
    
    # Get story image URL
    story_image_url = url_for('story_image', story_id=story_id)
    
    content = render_template_string(
        STORY_TEMPLATE,
        title=title,
        story_image_url=story_image_url
    )
    
    return render_template_string(MAIN_TEMPLATE, page_title=title + " - Storybook Magic", content=content)

@app.route('/story_image/<story_id>')
def story_image(story_id):
    """Serve the story image."""
    if story_id not in stories or 'story_image' not in stories[story_id]:
        return "Image not found", 404
    
    image_path = stories[story_id]['story_image']
    
    # Check if the path is absolute
    if os.path.isabs(image_path):
        return send_file(image_path)
    
    # Otherwise, assume it's relative to the PERSISTENT_IMAGE_DIR
    return send_from_directory(PERSISTENT_IMAGE_DIR, os.path.basename(image_path))

def process_story_background(story_id):
    """Background processing function for story generation."""
    with app.app_context():
        try:
            story_data = stories.get(story_id)
            if not story_data:
                logger.error(f"Story not found: {story_id}")
                return
                
            session_id = story_data["session_id"]
            
            # Step 1: Prepare story data
            update_progress(session_id, 20, "Analyzing image...", 2)
            
            # Step 2: Generate the story
            update_progress(session_id, 40, "Creating your personalized story...", 3)
            
            story_text = generate_story(
                story_data["child_name"],
                story_data["image_data"],
                story_data["theme"],
                story_data["age_range"],
                generate_illustrations=True,
                rhyming=story_data["rhyming"]
            )
            
            stories[story_id]["story_text"] = story_text
            
            # Step 3: Generate the story image
            update_progress(session_id, 60, "Generating story image...", 4)
            
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            story_image_path = generate_story_image(story_text, api_key)
            stories[story_id]["story_image"] = story_image_path
            
            # Step 4: Finalize
            update_progress(session_id, 90, "Finalizing your story...", 5)
            time.sleep(1)  # Brief pause for UI feedback
            
            # Mark as complete
            update_progress(session_id, 100, "Your story is ready!", 5, status="complete", story_id=story_id)
            
        except Exception as e:
            logger.error(f"Error in process_story_background: {str(e)}", exc_info=True)
            if story_id in stories and "session_id" in stories[story_id]:
                session_id = stories[story_id]["session_id"]
                update_progress(session_id, 0, f"Error: {str(e)}", "Error", status="error")

def update_progress(session_id, progress, message, step, status="processing", **kwargs):
    """Update the progress tracking for a session."""
    if session_id in story_progress:
        story_progress[session_id] = {
            "progress": progress,
            "message": message,
            "step": step,
            "status": status,
            **kwargs
        }
        logger.info(f"Progress updated: {progress}% - {message}")

if __name__ == '__main__':
    app.run(debug=True)
