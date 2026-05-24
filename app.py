from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from better_profanity import profanity
import os
import sys
import json
import uuid
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database import Database
except ImportError:
    Database = None

app = Flask(__name__)
CORS(app)

profanity.load_censor_words()


# ============================================
# SERVIR ARCHIVOS ESTATICOS
# ============================================

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('js', filename)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_html(filename):
    if filename.endswith('.html'):
        return send_from_directory('.', filename)
    return send_from_directory('.', filename)


# ============================================
# PALABRAS CLAVE PARA FLASHCARDS
# ============================================

PALABRAS_CLAVE = {
    'Que es la Fisica': ['fisica', 'materia', 'energia', 'espacio', 'tiempo'],
    'MRU': ['velocidad', 'distancia', 'tiempo', 'uniforme', 'rectilineo'],
    'MRUA': ['aceleracion', 'velocidad', 'tiempo', 'desplazamiento'],
    'Leyes de Newton': ['newton', 'inercia', 'fuerza', 'masa'],
    'Energia': ['cinetica', 'potencial', 'conservacion', 'trabajo'],
    'Vectores': ['vector', 'escalar', 'magnitud', 'direccion']
}


# ============================================
# FUNCION AYUDANTE
# ============================================

def get_db():
    if Database:
        db = Database()
        if db is None:
            print("ERROR: Database() devolvio None")
            return None
        if db.supabase is None:
            print("ERROR: db.supabase es None")
            return None
        return db
    return None


# ============================================
# API - REGISTRO
# ============================================

@app.route('/api/registro', methods=['POST'])
def registro():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not nombre or not email or not password:
        return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'}), 400
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Minimo 6 caracteres'}), 400
    
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        # Verificar si el email ya existe
        response = db.supabase.table('usuarios').select('id').eq('email', email).execute()
        if response.data:
            return jsonify({'success': False, 'message': 'Correo ya registrado'}), 400
        
        # Crear usuario
        hashed = generate_password_hash(password)
        user_id = str(uuid.uuid4())
        
        response = db.supabase.table('usuarios').insert({
            'id': user_id,
            'nombre': nombre,
            'email': email,
            'password_hash': hashed
        }).execute()
        
        return jsonify({'success': True, 'usuario_id': user_id})
    except Exception as e:
        print(f"ERROR REGISTRO: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error al registrar'}), 500


# ============================================
# API - LOGIN
# ============================================

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
    
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        response = db.supabase.table('usuarios').select('id, nombre, password_hash').eq('email', email).execute()
        user = response.data[0] if response.data else None
        
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'success': False, 'message': 'Credenciales incorrectas'}), 401
        
        return jsonify({'success': True, 'usuario_id': str(user['id']), 'nombre': user['nombre']})
    except Exception as e:
        print(f"ERROR LOGIN: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error al iniciar sesion'}), 500


# ============================================
# API - TEMAS
# ============================================

@app.route('/api/temas', methods=['GET'])
def obtener_temas():
    db = get_db()
    if not db:
        print("ERROR: No se pudo conectar a la base de datos")
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        response = db.supabase.table('temas').select('*').order('orden').execute()
        temas = response.data
        print(f"DEBUG: Se encontraron {len(temas)} temas")
        return jsonify({'success': True, 'temas': temas})
    except Exception as e:
        print(f"ERROR TEMAS: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ============================================
# API - SUBTEMAS
# ============================================

@app.route('/api/temas/<int:tema_id>/subtemas', methods=['GET'])
def obtener_subtemas(tema_id):
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        response = db.supabase.table('subtemas').select('*').eq('tema_id', tema_id).order('orden').execute()
        subtemas = response.data
        return jsonify({'success': True, 'subtemas': subtemas})
    except Exception as e:
        print(f"ERROR SUBTEMAS: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ============================================
# API - CONTENIDO
# ============================================

@app.route('/api/contenido/<int:subtema_id>', methods=['GET'])
def obtener_contenido(subtema_id):
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        response = db.supabase.table('subtemas').select('*').eq('id', subtema_id).execute()
        subtema = response.data[0] if response.data else None
        
        usuario_id = request.args.get('usuario_id')
        leido = False
        if usuario_id:
            prog_response = db.supabase.table('progreso').select('leido').eq('usuario_id', usuario_id).eq('subtema_id', subtema_id).execute()
            prog = prog_response.data[0] if prog_response.data else None
            leido = prog['leido'] if prog else False
        
        if not subtema:
            return jsonify({'success': False, 'message': 'Subtema no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'subtema': subtema,
            'contenido': {
                'titulo': subtema['nombre'],
                'contenido_html': subtema.get('contenido_html') or '<p>Contenido en construccion...</p>'
            },
            'leido': leido
        })
    except Exception as e:
        print(f"ERROR CONTENIDO: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ============================================
# API - FLASHCARDS
# ============================================

@app.route('/api/flashcards/<int:subtema_id>', methods=['GET'])
def obtener_flashcards(subtema_id):
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        tema_response = db.supabase.table('subtemas').select('nombre').eq('id', subtema_id).execute()
        tema_info = tema_response.data[0] if tema_response.data else None
        
        response = db.supabase.table('flashcards').select('*, usuarios(nombre)').eq('subtema_id', subtema_id).eq('estado', 'aprobada').order('es_oficial', desc=True).execute()
        flashcards = response.data
        
        return jsonify({
            'success': True,
            'flashcards': flashcards,
            'tema_nombre': tema_info['nombre'] if tema_info else '',
            'total': len(flashcards)
        })
    except Exception as e:
        print(f"ERROR FLASHCARDS: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/flashcards/crear', methods=['POST'])
def crear_flashcard():
    data = request.get_json()
    subtema_id = data.get('subtema_id')
    pregunta = data.get('pregunta', '').strip()
    respuesta = data.get('respuesta', '').strip()
    usuario_id = data.get('usuario_id')
    
    if not subtema_id or not pregunta or not respuesta:
        return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
    
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        es_oficial = not usuario_id
        
        response = db.supabase.table('flashcards').insert({
            'subtema_id': subtema_id,
            'pregunta': pregunta,
            'respuesta': respuesta,
            'es_oficial': es_oficial,
            'creado_por': usuario_id if usuario_id else None,
            'estado': 'aprobada' if es_oficial else 'pendiente'
        }).execute()
        
        return jsonify({'success': True, 'message': 'Flashcard creada'})
    except Exception as e:
        print(f"ERROR CREAR FLASHCARD: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error al crear'}), 500


# ============================================
# API - EXAMENES
# ============================================

@app.route('/api/examen/<int:subtema_id>', methods=['GET'])
def obtener_examen(subtema_id):
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        response = db.supabase.table('examenes').select('*').eq('subtema_id', subtema_id).execute()
        preguntas = response.data
        
        for p in preguntas:
            if p.get('opciones'):
                try:
                    p['opciones'] = json.loads(p['opciones'])
                except:
                    p['opciones'] = []
            else:
                p['opciones'] = None
        
        return jsonify({'success': True, 'preguntas': preguntas, 'total': len(preguntas)})
    except Exception as e:
        print(f"ERROR EXAMEN: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/examen/guardar-resultado', methods=['POST'])
def guardar_resultado():
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    subtema_id = data.get('subtema_id')
    aciertos = data.get('aciertos')
    total = data.get('total')
    
    if not all([usuario_id, subtema_id, aciertos is not None, total]):
        return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
    
    porcentaje = (aciertos / total) * 100 if total > 0 else 0
    
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        response = db.supabase.table('resultados_examenes').insert({
            'usuario_id': usuario_id,
            'subtema_id': subtema_id,
            'aciertos': aciertos,
            'total': total,
            'porcentaje': porcentaje
        }).execute()
        
        return jsonify({'success': True, 'porcentaje': round(porcentaje, 2)})
    except Exception as e:
        print(f"ERROR GUARDAR RESULTADO: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error al guardar'}), 500


# ============================================
# API - PROGRESO
# ============================================

@app.route('/api/progreso/<int:subtema_id>/marcar-leido', methods=['POST'])
def marcar_leido(subtema_id):
    data = request.get_json() or {}
    usuario_id = data.get('usuario_id')
    
    if not usuario_id:
        return jsonify({'success': False, 'message': 'Usuario no identificado'}), 401
    
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        # Verificar si existe
        existe_response = db.supabase.table('progreso').select('id').eq('usuario_id', usuario_id).eq('subtema_id', subtema_id).execute()
        existe = existe_response.data[0] if existe_response.data else None
        
        if existe:
            db.supabase.table('progreso').update({
                'leido': True,
                'ultimo_acceso': 'now()'
            }).eq('usuario_id', usuario_id).eq('subtema_id', subtema_id).execute()
        else:
            db.supabase.table('progreso').insert({
                'usuario_id': usuario_id,
                'subtema_id': subtema_id,
                'leido': True
            }).execute()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"ERROR PROGRESO: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/progreso/general', methods=['GET'])
def progreso_general():
    return jsonify({'temas_leidos': 0, 'total_temas': 0, 'porcentaje': 0, 'detalle': []})


# ============================================
# INICIAR SERVIDOR
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
