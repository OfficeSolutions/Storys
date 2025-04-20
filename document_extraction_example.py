"""
Document Understanding and Data Extraction Example using Gemini API

This script demonstrates how to use the Gemini API for document understanding and data extraction.
It shows how to:
1. Extract structured data from documents (receipts, forms, etc.)
2. Answer questions about document content
3. Summarize key information from documents
"""

from google import genai
import base64
import os
from PIL import Image
import requests
from io import BytesIO

# Initialize the client with the provided API key
API_KEY = "AIzaSyD_TRW55r7Am5mhsKiQph9RHwyfml9WOH4"
client = genai.Client(api_key=API_KEY)

def encode_image_from_url(image_url):
    """Download an image from a URL and encode it to base64."""
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    
    # Save the image temporarily
    img_path = "temp_document.jpg"
    img.save(img_path)
    
    # Read and encode the image
    with open(img_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Clean up the temporary file
    os.remove(img_path)
    
    return encoded_string

def encode_local_image(image_path):
    """Encode a local image to base64."""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def analyze_document(document_data, prompt):
    """Analyze a document using Gemini API."""
    try:
        # Create a multipart message with both text and image
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                {"role": "user", "parts": [
                    {"text": prompt},
                    {"inline_data": {
                        "mime_type": "image/jpeg",
                        "data": document_data
                    }}
                ]}
            ]
        )
        return response.text
    except Exception as e:
        return f"Error analyzing document: {str(e)}"

def extract_structured_data(document_data, data_format):
    """Extract structured data from a document in the specified format."""
    prompt = f"""
    Extract the following information from this document and return it in {data_format} format:
    - Date
    - Total amount
    - Vendor/Business name
    - Line items with prices (if visible)
    - Payment method (if visible)
    - Any discount or tax information
    
    Only include information that is actually visible in the document.
    """
    return analyze_document(document_data, prompt)

def main():
    print("GEMINI DOCUMENT UNDERSTANDING EXAMPLE")
    print("=====================================\n")
    
    # Example: Analyze a receipt
    # Using a sample receipt image URL
    receipt_url = "https://www.receiptmaker.net/wp-content/uploads/2023/06/Receipt-Maker-Sample-Receipt.png"
    print(f"Analyzing receipt from URL: {receipt_url}")
    
    encoded_receipt = encode_image_from_url(receipt_url)
    
    # Extract structured data in JSON format
    print("\n=== STRUCTURED DATA EXTRACTION (JSON) ===")
    json_data = extract_structured_data(encoded_receipt, "JSON")
    print(json_data)
    
    # Extract structured data in markdown table format
    print("\n=== STRUCTURED DATA EXTRACTION (MARKDOWN TABLE) ===")
    markdown_data = extract_structured_data(encoded_receipt, "markdown table")
    print(markdown_data)
    
    # Ask specific questions about the document
    questions = [
        "What is the total amount on this receipt?",
        "What date was this receipt issued?",
        "What items were purchased according to this receipt?",
        "Was tax applied to this purchase? If so, how much?"
    ]
    
    print("\n=== DOCUMENT Q&A ===")
    for question in questions:
        answer = analyze_document(encoded_receipt, question)
        print(f"\nQ: {question}")
        print(f"A: {answer}")
    
    # Generate a summary of the document
    summary_prompt = "Provide a concise summary of this receipt in 2-3 sentences."
    summary = analyze_document(encoded_receipt, summary_prompt)
    
    print("\n=== DOCUMENT SUMMARY ===")
    print(summary)
    
    print("\nDocument analysis complete!")

if __name__ == "__main__":
    main()
