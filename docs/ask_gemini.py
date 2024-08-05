import os
import google.generativeai as genai

genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

if __name__ == "__main__":
    print("👩‍💻 Welcome to the Simon Help Chat! 🙋‍")
    prompt: str = "You are a useful coding and robotics assistant. Help the user answer questions about their Simon project."
    prompt += "Here is the build guide and some context for the project:"
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'BUILDGUIDE.md')) as f:
        prompt += f.read()
    prompt += "\n Here is the user question:"
    while True:
        question = input("Enter a question about Simon: ")
        response = model.generate_content([prompt, question])
        print(response.text)