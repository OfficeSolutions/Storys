import os
import tempfile
import uuid
import base64
import re
import json
import logging
import time
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template_string, redirect, url_for, send_file, jsonify, abort

from enhanced_story_generator import (
    generate_story,
    extract_illustration_descriptions,
    generate_illustration,
    generate_ghibli_style_image
)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure Flask for URL generation outside request context
app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME', 'storys.onrender.com')
app.config['APPLICATION_ROOT'] = os.environ.get('APPLICATION_ROOT', '/')
app.config['PREFERRED_URL_SCHEME'] = os.environ.get('PREFERRED_URL_SCHEME', 'https')

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
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
            color: #333;
        }
        
        .navbar {
            background-color: #fff;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .navbar-brand {
            font-weight: 600;
            color: #0d6efd;
        }
        
        .hero-section {
            background-color: #e9f2ff;
            padding: 5rem 0;
            border-radius: 0 0 2rem 2rem;
            margin-bottom: 3rem;
        }
        
        .hero-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: #0d6efd;
        }
        
        .hero-subtitle {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            color: #6c757d;
        }
        
        .form-container {
            background-color: #fff;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 3rem;
        }
        
        .form-label {
            font-weight: 600;
        }
        
        .story-content {
            background-color: #fff;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 3rem;
            font-size: 1.1rem;
            line-height: 1.8;
        }
        
        .story-content p {
            margin-bottom: 1.5rem;
        }
        
        .illustration {
            margin: 2rem 0;
            text-align: center;
        }
        
        .illustration-image {
            max-width: 100%;
            border-radius: 0.5rem;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        .book-container {
            perspective: 1000px;
            width: 300px;
            height: 450px;
            margin: 0 auto 2rem;
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
        
        .book-front, .book-back, .book-right, .book-left, .book-top, .book-bottom {
            position: absolute;
            width: 100%;
            height: 100%;
            background-color: #0d6efd;
            border-radius: 2px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        }
        
        .book-front {
            transform: translateZ(25px);
            background-color: #fff;
            border: 2px solid #0d6efd;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
            text-align: center;
        }
        
        .book-back {
            transform: translateZ(-25px) rotateY(180deg);
            background-color: #0d6efd;
        }
        
        .book-right {
            width: 50px;
            transform: rotateY(90deg) translateZ(150px);
            background-color: #e9ecef;
        }
        
        .book-left {
            width: 50px;
            transform: rotateY(-90deg) translateZ(150px);
            background-color: #e9ecef;
        }
        
        .book-top {
            height: 50px;
            transform: rotateX(90deg) translateZ(150px);
            background-color: #e9ecef;
        }
        
        .book-bottom {
            height: 50px;
            transform: rotateX(-90deg) translateZ(300px);
            background-color: #e9ecef;
        }
        
        .book-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #0d6efd;
            margin-bottom: 1rem;
        }
        
        .book-spine {
            position: absolute;
            width: 50px;
            height: 100%;
            transform: rotateY(90deg) translateZ(25px);
            background-color: #0d6efd;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            font-weight: 700;
            writing-mode: vertical-rl;
            text-orientation: mixed;
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

    <!-- Progress Modal -->
    <div class="modal fade progress-modal" id="progressModal" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="progressModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="progressModalLabel">Creating Your Story</h5>
                </div>
                <div class="modal-body">
                    <div class="progress-message text-center mb-4" id="progressMessage">Preparing your story...</div>
                    
                    <div class="progress mb-4" style="height: 25px;">
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
                            <span>Generating illustrations</span>
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
                            if (data.status === 'complete' && data.redirect_url) {
                                console.log('Story complete, redirecting to:', data.redirect_url);
                                clearInterval(pollingInterval);
                                window.location.href = data.redirect_url;
                            }
                            
                            // If error, show error and stop polling
                            if (data.status === 'error') {
                                console.error('Error in story generation:', data.message);
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
                        progressBar.style.width = data.percent + '%';
                        progressBar.setAttribute('aria-valuenow', data.percent);
                        progressBar.textContent = data.percent + '%';
                    }
                    
                    // Update message
                    const progressMessage = document.getElementById('progressMessage');
                    if (progressMessage) {
                        progressMessage.textContent = data.message;
                    }
                    
                    // Update step indicators based on current step
                    const currentStep = data.current_step;
                    const steps = ['Initializing', 'Analyzing image', 'Creating story', 'Generating illustrations', 'Preparing display', 'Complete'];
                    
                    for (let i = 1; i <= 5; i++) {
                        const indicator = document.getElementById('step' + i + 'Indicator');
                        const icon = document.getElementById('step' + i + 'Icon');
                        
                        if (indicator && icon) {
                            // Reset classes
                            indicator.classList.remove('completed', 'active');
                            icon.classList.remove('bi-check-circle-fill', 'bi-circle-fill', 'bi-circle');
                            icon.classList.remove('text-success', 'text-primary', 'text-secondary');
                            
                            const stepName = steps[i-1];
                            
                            if (currentStep === stepName) {
                                // Current step
                                indicator.classList.add('active');
                                icon.classList.add('bi-circle-fill', 'text-primary');
                            } else if (steps.indexOf(currentStep) > steps.indexOf(stepName)) {
                                // Completed step
                                indicator.classList.add('completed');
                                icon.classList.add('bi-check-circle-fill', 'text-success');
                            } else {
                                // Future step
                                icon.classList.add('bi-circle', 'text-secondary');
                            }
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

UPLOAD_TEMPLATE = """
<div class="hero-section">
    <div class="container">
        <div class="row align-items-center">
            <div class="col-md-6">
                <h1 class="hero-title">Create Magical Stories for Your Child</h1>
                <p class="hero-subtitle">Upload a photo of your child and we'll create a personalized bedtime story featuring them as the main character!</p>
            </div>
            <div class="col-md-6">
                <div class="book-container">
                    <div class="book">
                        <div class="book-front">
                            <i class="bi bi-stars text-primary mb-4" style="font-size: 3rem;"></i>
                            <h2 class="book-title">Storybook Magic</h2>
                            <p>Create personalized stories for your child</p>
                        </div>
                        <div class="book-back"></div>
                        <div class="book-spine">Storybook Magic</div>
                        <div class="book-right"></div>
                        <div class="book-top"></div>
                        <div class="book-bottom"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="form-container">
    <form id="storyForm" action="/generate" method="post" enctype="multipart/form-data">
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
            <button type="submit" class="btn btn-primary btn-lg px-4" id="createStoryBtn">Create Story</button>
        </div>
    </form>
</div>

<script>
    document.addEventListener('DOMContentLoaded', function() {
        const storyForm = document.getElementById('storyForm');
        const progressModal = new bootstrap.Modal(document.getElementById('progressModal'));
        let sessionId = null;
        let pollingInterval = null;
        
        storyForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show progress modal immediately
            progressModal.show();
            
            // Create FormData object
            const formData = new FormData(storyForm);
            
            // Submit form via AJAX
            fetch('/generate_ajax', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                    progressModal.hide();
                    return;
                }
                
                // Store session ID for polling
                sessionId = data.session_id;
                
                // Start polling for progress updates
                startProgressPolling(sessionId);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while submitting the form. Please try again.');
                progressModal.hide();
            });
        });
        
        function startProgressPolling(sessionId) {
            // Clear any existing interval
            if (pollingInterval) {
                clearInterval(pollingInterval);
            }
            
            // Poll every 1.5 seconds
            pollingInterval = setInterval(() => {
                fetch('/progress_status/' + sessionId)
                .then(response => response.json())
                .then(data => {
                    updateProgressUI(data);
                    
                    // If complete, redirect to story page
                    if (data.status === 'complete' && data.redirect_url) {
                        clearInterval(pollingInterval);
                        window.location.href = data.redirect_url;
                    }
                    
                    // If error, show error and stop polling
                    if (data.status === 'error') {
                        clearInterval(pollingInterval);
                        alert('Error: ' + data.message);
                        progressModal.hide();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }, 1500);
        }
        
        function updateProgressUI(data) {
            // Update progress bar
            const progressBar = document.getElementById('progressBar');
            progressBar.style.width = data.percent + '%';
            progressBar.setAttribute('aria-valuenow', data.percent);
            progressBar.textContent = data.percent + '%';
            
            // Update message
            document.getElementById('progressMessage').textContent = data.message;
            
            // Update step indicators based on current step
            const currentStep = data.current_step;
            const steps = ['Initializing', 'Analyzing image', 'Creating story', 'Generating illustrations', 'Preparing display', 'Complete'];
            
            for (let i = 1; i <= 5; i++) {
                const indicator = document.getElementById('step' + i + 'Indicator');
                const icon = document.getElementById('step' + i + 'Icon');
                
                // Reset classes
                indicator.classList.remove('completed', 'active');
                icon.classList.remove('bi-check-circle-fill', 'bi-circle-fill', 'bi-circle');
                icon.classList.remove('text-success', 'text-primary', 'text-secondary');
                
                const stepName = steps[i-1];
                
                if (currentStep === stepName) {
                    // Current step
                    indicator.classList.add('active');
                    icon.classList.add('bi-circle-fill', 'text-primary');
                } else if (steps.indexOf(currentStep) > steps.indexOf(stepName)) {
                    // Completed step
                    indicator.classList.add('completed');
                    icon.classList.add('bi-check-circle-fill', 'text-success');
                } else {
                    // Future step
                    icon.classList.add('bi-circle', 'text-secondary');
                }
            }
        }
    });
</script>
"""

STORY_TEMPLATE = """
<div class="mt-5 mb-5">
    <div class="book-container">
        <div class="book">
            <div class="book-front">
                <img src="{{ story_data['image_path'] }}" alt="Story cover image" class="img-fluid mb-3" style="max-height: 200px; border-radius: 8px;">
                <h2 class="book-title">{{ story_data["child_name"] }}'s Adventure</h2>
                <p>A magical tale featuring {{ story_data["child_name"] }}</p>
            </div>
            <div class="book-back"></div>
            <div class="book-spine"></div>
            <div class="book-top"></div>
            <div class="book-bottom"></div>
            <div class="book-right"></div>
        </div>
    </div>
    
    <div class="story-content">
        {{ story_data["story_html_final"]|safe }}
    </div>
    
    <div class="text-center mt-5">
        <a href="/" class="btn btn-primary me-2">Create Another Story</a>
        <button class="btn btn-outline-primary" onclick="window.print()">Print Story</button>
    </div>
</div>
"""

@app.route("/")
def index():
    content = render_template_string(UPLOAD_TEMPLATE)
    return render_template_string(MAIN_TEMPLATE, content=content, page_title="Create Your Story - Storybook Magic")

def update_progress(session_id, percent, message, current_step, status='in_progress', redirect_url=None):
    """Update the progress for a specific session."""
    story_progress[session_id] = {
        'percent': percent,
        'message': message,
        'current_step': current_step,
        'status': status,
        'redirect_url': redirect_url
    }
    logger.info(f"Progress updated for {session_id}: {percent}% - {message}")

@app.route("/progress_status/<session_id>")
def progress_status(session_id):
    """Return the current progress status as JSON for AJAX polling."""
    # Get progress data or default values if not found
    progress_data = story_progress.get(session_id, {
        'percent': 10,
        'message': 'Starting story creation...',
        'current_step': 'Initializing',
        'status': 'in_progress',
        'redirect_url': None
    })
    
    return jsonify(progress_data)

@app.route("/generate_ajax", methods=["POST"])
def generate_ajax():
    """AJAX endpoint for story generation."""
    try:
        # Generate a unique session ID for tracking progress
        session_id = str(uuid.uuid4())
        
        # Initialize progress
        update_progress(session_id, 10, "Uploading and processing image...", "Processing uploaded image")
        
        # Store form data
        child_name = request.form["child_name"]
        child_image_file = request.files["child_image"]
        age_range = request.form["age_range"]
        theme = request.form["theme"]
        generate_illustrations_flag = request.form.get("generate_illustrations") == "true"
        rhyming_flag = request.form.get("rhyming") == "true"

        if not child_image_file or child_image_file.filename == "":
            return jsonify({"error": "No image file provided"})

        # Save the uploaded image
        filename = secure_filename(child_image_file.filename if child_image_file.filename else "uploaded_image")
        temp_dir = tempfile.mkdtemp()
        image_path = os.path.join(temp_dir, filename)
        child_image_file.save(image_path)

        # Create a new story ID and store initial data
        story_id = str(uuid.uuid4())
        stories[story_id] = {
            "child_name": child_name,
            "session_id": session_id,
            "theme": theme,
            "age_range": age_range,
            "generate_illustrations": generate_illustrations_flag,
            "rhyming": rhyming_flag,
            "image_path": image_path,
            "status": "processing"
        }
        
        # Start background processing in a separate thread
        import threading
        processing_thread = threading.Thread(target=process_story_background, args=(story_id,))
        processing_thread.daemon = True
        processing_thread.start()
        
        # Return session ID for progress tracking
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "Story generation started"
        })
        
    except Exception as e:
        logger.error(f"Error in /generate_ajax: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)})

def process_story_background(story_id):
    """Background processing function for story generation."""
    with app.app_context():  # Add Flask application context
        try:
            story_data = stories.get(story_id)
            if not story_data:
                logger.error(f"Story not found: {story_id}")
                return
                
            session_id = story_data["session_id"]
            child_name = story_data["child_name"]
            theme = story_data["theme"]
            age_range = story_data["age_range"]
            generate_illustrations_flag = story_data["generate_illustrations"]
            rhyming_flag = story_data["rhyming"]
            image_path = story_data["image_path"]
        
            # Encode image to base64
            with open(image_path, "rb") as f:
                image_data_base64 = base64.b64encode(f.read()).decode("utf-8")
        
            # Update progress after image processing
            update_progress(session_id, 20, "Analyzing child's features...", "Analyzing image")
        
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.error("OPENAI_API_KEY environment variable not set.")
                update_progress(session_id, 0, "Server configuration error: API key not set.", "Error", status="error")
                return
            
            # Generate Ghibli-style image for the cover
            update_progress(session_id, 30, "Creating Ghibli-style cover image...", "Generating cover image")
            ghibli_image_path = generate_ghibli_style_image(image_data_base64, api_key)
            if not ghibli_image_path:
                logger.warning("Failed to generate Ghibli-style image, using original image as fallback.")
                ghibli_image_path = image_path # Fallback to original if Ghibli fails
                
            # Update progress after Ghibli image generation
            update_progress(session_id, 50, "Writing your personalized story...", "Creating story")
            
            # Generate the story
            story_text = generate_story(
                child_name, 
                image_data_base64, 
                theme, 
                age_range, 
                generate_illustrations_flag,
                rhyming_flag
            )
        
            # Update story data with generated content
            stories[story_id]["story_text"] = story_text
            stories[story_id]["image_path"] = url_for("get_uploaded_image", story_id=story_id, filename=os.path.basename(ghibli_image_path))
        
            # Process illustrations if requested
            illustration_images = {}
            generated_illustration_paths_urls = []
        
            if generate_illustrations_flag:
                update_progress(session_id, 70, "Story created! Now adding illustrations...", "Generating illustrations")
            
                # Extract illustration descriptions from the story
                illustration_descriptions = extract_illustration_descriptions(story_text)
            
                # Generate illustrations for each description
                for i, desc in enumerate(illustration_descriptions):
                    logger.info(f"Generating illustration {i+1}/{len(illustration_descriptions)}: {desc}")
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
                            processed_html += f'<div class="illustration"><p class="text-danger"><em>Illustration for "{original_desc_text}" could not be generated.</em></p></div>'
                        processed_html += rest_of_story
                    except IndexError:
                        processed_html += part # Append the remainder if parsing fails
                story_html = processed_html
            else:
                update_progress(session_id, 80, "Story created! Finalizing your story...", "Finalizing")
                # Remove illustration placeholders if not generating
                story_html = re.sub(r'\[ILLUSTRATION: (.*?)\]', '', story_text)
            
            # Final progress update before redirecting
            update_progress(session_id, 90, "Finalizing your story...", "Preparing display")
            
            # Store the final HTML (with illustrations or removed placeholders)
            stories[story_id]["story_html_final"] = story_html
            stories[story_id]["status"] = "complete"
        
            # Set final progress to 100% with redirect URL
            update_progress(
                session_id, 
                100, 
                "Story complete! Redirecting...", 
                "Complete", 
                status="complete", 
                redirect_url=url_for("show_story", story_id=story_id)
            )
        
        except Exception as e:
            logger.error(f"Error in process_story_background: {str(e)}", exc_info=True)
            if story_id in stories and "session_id" in stories[story_id]:
                session_id = stories[story_id]["session_id"]
                update_progress(session_id, 0, f"Error: {str(e)}", "Error", status="error")

@app.route("/generate", methods=["POST"])
def generate():
    """Legacy endpoint for non-AJAX form submission (fallback)."""
    try:
        # Generate a unique session ID for tracking progress
        session_id = str(uuid.uuid4())
        
        # Initialize progress
        update_progress(session_id, 10, "Uploading and processing image...", "Processing uploaded image")
        
        # Store form data
        child_name = request.form["child_name"]
        child_image_file = request.files["child_image"]
        age_range = request.form["age_range"]
        theme = request.form["theme"]
        generate_illustrations_flag = request.form.get("generate_illustrations") == "true"
        rhyming_flag = request.form.get("rhyming") == "true"

        if not child_image_file or child_image_file.filename == "":
            return "No image file provided", 400

        # Save the uploaded image
        filename = secure_filename(child_image_file.filename if child_image_file.filename else "uploaded_image")
        temp_dir = tempfile.mkdtemp()
        image_path = os.path.join(temp_dir, filename)
        child_image_file.save(image_path)

        # Create a new story ID and store initial data
        story_id = str(uuid.uuid4())
        stories[story_id] = {
            "child_name": child_name,
            "session_id": session_id,
            "theme": theme,
            "age_range": age_range,
            "generate_illustrations": generate_illustrations_flag,
            "rhyming": rhyming_flag,
            "image_path": image_path,
            "status": "processing"
        }
        
        # Start background processing in a separate thread
        import threading
        processing_thread = threading.Thread(target=process_story_background, args=(story_id,))
        processing_thread.daemon = True
        processing_thread.start()
        
        # For non-AJAX fallback, redirect to the story page
        # The story page will show progress until the story is ready
        return redirect(url_for("show_story", story_id=story_id))
        
    except Exception as e:
        logger.error(f"Error in /generate: {str(e)}", exc_info=True)
        return f"An error occurred: {str(e)}", 500

@app.route("/story/<story_id>")
def show_story(story_id):
    story_data = stories.get(story_id)
    if not story_data:
        abort(404)
    
    # If story is still processing, show progress modal
    if story_data.get("status") == "processing" and "session_id" in story_data:
        session_id = story_data["session_id"]
        progress_data = story_progress.get(session_id, {
            'percent': 10,
            'message': 'Starting story creation...',
            'current_step': 'Initializing',
            'status': 'in_progress'
        })
        
        # Create a waiting page with progress modal that auto-refreshes
        waiting_content = f"""
        <div class="text-center mt-5">
            <h2>Creating Your Story...</h2>
            <p class="lead">Please wait while we create a personalized story for {story_data["child_name"]}.</p>
            
            <div class="progress mt-4 mb-4" style="height: 30px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" 
                     style="width: {progress_data['percent']}%;" 
                     aria-valuenow="{progress_data['percent']}" aria-valuemin="0" aria-valuemax="100">
                    {progress_data['percent']}%
                </div>
            </div>
            
            <p class="fs-5">{progress_data['message']}</p>
            <p class="text-muted">This page will automatically update. Please don't close your browser.</p>
        </div>
        
        <script>
            // Auto-refresh every 3 seconds
            setTimeout(function() {{
                window.location.reload();
            }}, 3000);
        </script>
        """
        return render_template_string(MAIN_TEMPLATE, content=waiting_content, page_title=f"{story_data['child_name']}'s Story - Creating...")
    
    # If story is complete, show the story
    content = render_template_string(STORY_TEMPLATE, story_data=story_data)
    return render_template_string(MAIN_TEMPLATE, content=content, page_title=f"{story_data['child_name']}'s Story - Storybook Magic")

@app.route("/uploads/<story_id>/<filename>")
def get_uploaded_image(story_id, filename):
    story_data = stories.get(story_id)
    if not story_data:
        abort(404)
    
    image_path = story_data.get("image_path")
    if not image_path:
        abort(404)
    
    return send_file(image_path)

@app.route("/illustrations/<image_id>")
def get_illustration_image(image_id):
    # Find the story that contains this illustration
    for story_id, story_data in stories.items():
        if story_id in image_id:  # Simple check if the image_id contains the story_id
            # Look for the illustration in the story's illustration images
            for img_id, img_path in story_data.get("illustration_images", {}).items():
                if img_id == image_id:
                    return send_file(img_path)
    
    abort(404)

if __name__ == "__main__":
    app.run(debug=True)
