"""
Code Generation and Assistance Example using Gemini API

This script demonstrates how to use the Gemini API for code generation and assistance.
It shows how to:
1. Generate code based on requirements
2. Debug and fix existing code
3. Explain code functionality
"""

from google import genai
import time

# Initialize the client with the provided API key
API_KEY = "AIzaSyD_TRW55r7Am5mhsKiQph9RHwyfml9WOH4"
client = genai.Client(api_key=API_KEY)

def generate_content(prompt):
    """Generate content using Gemini API."""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error generating content: {str(e)}"

def main():
    print("GEMINI CODE GENERATION EXAMPLE")
    print("==============================\n")
    
    # Example 1: Generate code based on requirements
    code_prompt = """
    Write a Python function that:
    1. Takes a list of dictionaries, where each dictionary represents a product with 'name', 'price', and 'category' keys
    2. Filters the products to only include those in a specified category
    3. Sorts the filtered products by price (lowest to highest)
    4. Returns the sorted list
    
    Include docstrings and comments explaining the code.
    """
    
    print("=== CODE GENERATION EXAMPLE ===")
    print("Generating code based on requirements...\n")
    generated_code = generate_content(code_prompt)
    print(generated_code)
    print("\n" + "-"*50 + "\n")
    
    # Allow some time between API calls
    time.sleep(2)
    
    # Example 2: Debug and fix code
    buggy_code = """
    def calculate_statistics(numbers):
        # Calculate mean, median, and mode of a list of numbers
        mean = sum(numbers) / len(numbers)
        
        # Calculate median
        sorted_numbers = sorted(numbers)
        n = len(sorted_numbers)
        if n % 2 == 0:
            median = (sorted_numbers[n/2] + sorted_numbers[n/2 - 1]) / 2
        else:
            median = sorted_numbers[n/2]
        
        # Calculate mode
        frequency = {}
        for num in numbers:
            if num in frequency:
                frequency[num] += 1
            else:
                frequency[num] = 1
        mode = max(frequency.items(), key=lambda x: x[1])
        
        return {'mean': mean, 'median': median, 'mode': mode}
    
    # Test the function
    result = calculate_statistics([1, 2, 3, 3, 4, 5])
    print(result)
    """
    
    debug_prompt = f"""
    The following Python code has bugs. Identify and fix all the bugs, explaining each issue and its solution.
    
    ```python
    {buggy_code}
    ```
    """
    
    print("=== CODE DEBUGGING EXAMPLE ===")
    print("Debugging and fixing code...\n")
    debug_result = generate_content(debug_prompt)
    print(debug_result)
    print("\n" + "-"*50 + "\n")
    
    # Allow some time between API calls
    time.sleep(2)
    
    # Example 3: Explain code functionality
    complex_code = """
    def memoize(func):
        cache = {}
        def wrapper(*args):
            if args not in cache:
                cache[args] = func(*args)
            return cache[args]
        return wrapper

    @memoize
    def fibonacci(n):
        if n < 2:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    """
    
    explain_prompt = f"""
    Explain the following Python code in detail, including:
    1. What it does
    2. How it works
    3. The purpose of each function
    4. Any design patterns or techniques being used
    
    Make the explanation accessible to an intermediate Python programmer.
    
    ```python
    {complex_code}
    ```
    """
    
    print("=== CODE EXPLANATION EXAMPLE ===")
    print("Explaining code functionality...\n")
    explanation = generate_content(explain_prompt)
    print(explanation)
    
    print("\nCode generation examples complete!")

if __name__ == "__main__":
    main()
