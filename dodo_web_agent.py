import os
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__, template_folder='templates')
CORS(app)

# Memoria en memoria (Render borra el disco al reiniciar, así que usamos RAM)
# Si necesitas persistencia real, usaríamos una base de datos.
chat_memory = []

DODO_IDENTITY = (
    "Eres Hermes, asistente personal de Dodo y experto en D&D Trade Company. "
    "Tu comportamiento es profesional, técnico y directo. "
    "1. NO ALUCINES: Si no conoces un dato, admítelo. "
    "2. RESPUESTAS: Si te hablan en chino, responde en chino. Si en español, responde en español. "
    "3. CONSISTENCIA: Mantén un tono serio y eficiente."
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_text = request.json.get('message', '')
    
    # Mantener historial en RAM (Render no permite persistencia en disco de archivos modificados)
    chat_memory.append({"role": "user", "content": user_text})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": DODO_IDENTITY}] + chat_memory[-10:]
        )
        response_text = completion.choices[0].message.content
        chat_memory.append({"role": "assistant", "content": response_text})
        
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
