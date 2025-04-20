# Storybook Magic - Deployment Guide

This repository contains the Storybook Magic application, a personalized bedtime story generator that uses the Gemini API to create unique stories based on a child's photo and name.

## Features

- Upload a child's photo and enter their name
- Select from multiple story themes
- Generate personalized bedtime stories featuring the child as the main character
- View stories with illustration suggestions
- Order printed books through Blurb integration

## Technology Stack

- Python 3.10+
- Flask web framework
- Google Gemini API for AI-powered story generation
- Bootstrap 5 for modern UI
- Pillow for image processing

## Local Development

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```
   export GEMINI_API_KEY=your_api_key_here
   ```
4. Run the application:
   ```
   python app.py
   ```

## Deployment

This application is configured for deployment on Render.com.

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key
- `PORT`: Port for the application (default: 8080)
- `DEBUG`: Set to 'True' for development, 'False' for production

## License

MIT
