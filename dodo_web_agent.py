import os
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__, template_folder='templates')
CORS(app)

MEMORY_FILE = "/workspace/dodo_memory.json"

def get_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f: return json.load(f)
    return []

def save_memory(history):
    with open(MEMORY_FILE, 'w') as f: json.dump(history[-10:], f)

DODO_IDENTITY = (
    "Eres Hermes, el asistente personal de Dodo. Hablas perfectamente chino mandarín (中文) y español. "
    "Tu personalidad es cálida y servicial. Tienes acceso a documentos de la empresa D&D Trade Company. "
    "Tu objetivo es ayudar a Dodo. Si te habla en chino, responde en chino. Si te habla en español, responde en español."
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_text = request.json.get('message', '')
    history = get_memory()
    
    config = types.GenerateContentConfig(
        system_instruction=f"{DODO_IDENTITY}\nMemoria reciente: {json.dumps(history)}"
    )

    try:
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite-preview',
            contents=user_text,
            config=config
        )
        history.append({"user": user_text, "bot": response.text})
        save_memory(history)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
