import argparse
import os
import re

import google.generativeai as genai

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate tool functions for Simon project")
    parser.add_argument("file_path", help="Path to the file containing existing tools")
    parser.add_argument("-n", type=int, default=3, help="Number of new tool functions to generate")
    parser.add_argument("-m", "--model", default="models/gemini-1.5-pro-latest", help="Gemini model to use")
    return parser.parse_args()

def extract_tools(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    pattern = r'# ---- TOOLS 🛠️ ----\s*([\s\S]*?)# ---- TOOLS 🛠️ ----'
    match = re.search(pattern, content)
    return match.group(1).strip() if match else "Tools section not found."

def strip_markdown(text):
    text = re.sub(r'```python\n', '', text)
    return re.sub(r'```\n?', '', text).strip()

def generate_function(model, prompt):
    response = model.generate_content(prompt)
    return strip_markdown(response.text)

def main():
    args = parse_arguments()
    genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
    model = genai.GenerativeModel(model_name=args.model)
    tools_content = extract_tools(args.file_path)
    prompt = f"""You are a tool function generator for a robot behavior project.
    Existing tools:
    {tools_content}
    Generate a new Python tool function that would be useful for the Simon project.
    Follow the existing format and naming conventions. Only output the function, no explanations."""
    generated_functions = []
    print("\n" + "-"*50 + "\n")
    for i in range(args.n):
        new_function = generate_function(model, prompt)
        generated_functions.append(new_function)
        print(new_function)
        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    main()