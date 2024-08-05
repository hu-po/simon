""" Generate more tool functions from a set of existing tools in a python file.

> python simon/scripts/generate_tools.py app-simon-says.py

"""
import argparse
import os
import re
import google.generativeai as genai

# Parse command line arguments
parser = argparse.ArgumentParser(description="Generate tool functions for Simon project")
parser.add_argument("file_path", help="Path to the file containing existing tools")
parser.add_argument("-n", type=int, default=10, help="Number of new tool functions to generate")
parser.add_argument("-m", "--model", default="models/gemini-1.5-pro-latest", help="Gemini model to use")
parser.add_argument("-t", "--temperature", type=float, default=0.9, help="Temperature for generation (0.0 to 1.0)")
args = parser.parse_args()

# Configure Google API
genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
model = genai.GenerativeModel(model_name=args.model)

# Extract existing tools from file
with open(args.file_path, 'r') as file:
    content = file.read()
pattern = r'# ---- TOOLS 🛠️ ----\s*([\s\S]*?)# ---- TOOLS 🛠️ ----'
match = re.search(pattern, content)
tools_content = match.group(1).strip() if match else "Tools section not found."

# Generate new functions
generated_functions = []
print("\n" + "-"*50 + "\n")

for i in range(args.n):
    prompt = f"""You are a tool function generator for a robot behavior project.
Existing tools:
{tools_content}
Generate a new Python tool function that would be useful for the Simon project.
Generate a unique function each time, different from the ones already shown.
{generated_functions}
Follow the existing format and naming conventions.
Be creative about the emoji and function name, but make it specific.
Only output the function, no explanations."""

    response = model.generate_content(prompt, generation_config=genai.GenerationConfig(temperature=args.temperature))
    new_function = re.sub(r'```python\n', '', response.text)
    new_function = re.sub(r'```\n?', '', new_function).strip()

    generated_functions.append(new_function)
    print(new_function)
    print("\n" + "-"*50 + "\n")