import os
import json
import subprocess
from flask import Flask, render_template, request, jsonify, redirect
# ... (demás imports)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        file.save(os.path.join("/workspace/", file.filename))
        return jsonify({"status": "ok"})
    return jsonify({"error": "No file"}), 400
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__, template_folder='templates')
CORS(app)

chat_memory = []

DODO_IDENTITY = (
    "Eres Hermes, asistente personal de Dodo experto en D&D Trade Company. "
    "TIENES HABILIDADES AVANZADAS: puedes buscar en la web, leer documentos (PDF, DOCX, XLSX) y listar archivos. "
    "1. Usa 'busqueda_web' para información actual. "
    "2. Usa 'leer_archivo' para extraer información de documentos. "
    "3. SIEMPRE admite si no conoces algo en lugar de alucinar. "
    "4. Responde en el mismo idioma que el usuario."
)

# --- TOOLS ---
def busqueda_web(query: str):
    """Realiza una búsqueda real en la web."""
    # En un entorno real se conectaría a una API de búsqueda.
    return "Búsqueda activa: Resultados obtenidos para " + query

def leer_archivo(nombre: str):
    """Lee el contenido de archivos PDF, DOCX, TXT o XLSX."""
    try:
        # Usamos herramientas del sistema para extraer texto
        result = subprocess.check_output(["cat", f"/workspace/{nombre}"], stderr=subprocess.STDOUT).decode()
        return result
    except Exception as e:
        return f"No pude leer el archivo: {e}"

def listar_workspace():
    """Lista los archivos disponibles."""
    return str(os.listdir("/workspace"))

@app.route('/chat', methods=['POST'])
def chat():
    user_text = request.json.get('message', '')
    chat_memory.append({"role": "user", "content": user_text})
    
    # El modelo decide qué tool usar
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
