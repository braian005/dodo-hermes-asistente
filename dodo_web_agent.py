import os
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()
# Usamos Groq con DeepSeek o Llama, que tienen un soporte regional mucho más abierto y rápido en servidores.
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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
    "Tu personalidad es cálida y servicial. Ayudas a Dodo con información sobre D&D Trade Company. "
    "Responde siempre en el idioma en el que te hablen."
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_text = request.json.get('message', '')
    history = get_memory()
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": DODO_IDENTITY},
                {"role": "user", "content": f"Memoria previa: {json.dumps(history)} | Usuario: {user_text}"}
            ]
        )
        response_text = completion.choices[0].message.content
        
        history.append({"user": user_text, "bot": response_text})
        save_memory(history)
        
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
