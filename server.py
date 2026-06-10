"""
Servidor mejorado con soporte para archivos estáticos
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from functools import wraps
from datetime import datetime
from app_main import SistemaARLINOST
from database import DatabaseARLINOST
from auth import AuthARLINOST
from cliente import Cliente
from prestador import Prestador, Servicio
import os

# Inicializar aplicación
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JSON_SORT_KEYS'] = False

# Instancias globales
sistema = SistemaARLINOST()
db = DatabaseARLINOST()
auth = AuthARLINOST()

# Precarga de datos de prueba
def cargar_datos_prueba():
    """Carga datos de prueba en el sistema"""
    try:
        # Registrar usuarios de prueba
        auth.registrar_usuario("cli001", "juan", "juan@email.com", "password123", "cliente")
        auth.registrar_usuario("cli002", "maria", "maria@email.com", "password123", "cliente")
        auth.registrar_usuario("pres001", "carlos", "carlos@email.com", "password123", "prestador")
        auth.registrar_usuario("pres002", "ana", "ana@email.com", "password123", "prestador")
        
        # Registrar en sistema
        cliente1 = sistema.registrar_cliente("CLI001", "Juan Pérez", "juan@email.com")
        cliente2 = sistema.registrar_cliente("CLI002", "María García", "maria@email.com")
        prestador1 = sistema.registrar_prestador("PRES001", "Carlos López", "carlos@email.com")
        prestador2 = sistema.registrar_prestador("PRES002", "Ana Martínez", "ana@email.com")
        
        # Registrar en base de datos
        db.insertar_cliente("CLI001", "Juan Pérez", "juan@email.com")
        db.insertar_cliente("CLI002", "María García", "maria@email.com")
        db.insertar_prestador("PRES001", "Carlos López", "carlos@email.com")
        db.insertar_prestador("PRES002", "Ana Martínez", "ana@email.com")
    except:
        pass  # Ya existen datos

# Decorador para validar token
def token_requerido(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token requerido'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        valido, resultado = auth.validar_token(token)
        if not valido:
            return jsonify({'error': resultado}), 401
        
        return f(usuario_id=resultado, *args, **kwargs)
    
    return decorated

# ==================== RUTAS WEB ====================

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Página de login"""
    return render_template('login.html')

@app.route('/cliente')
def cliente_page():
    """Dashboard de cliente"""
    return render_template('cliente.html')

@app.route('/prestador')
def prestador_page():
    """Dashboard de prestador"""
    return render_template('prestador.html')

@app.route('/admin')
def admin_page():
    """Dashboard de administrador"""
    return render_template('admin.html')

# ==================== API AUTENTICACIÓN ====================

@app.route('/api/auth/registro', methods=['POST'])
def registro():
    """Registra un nuevo usuario"""
    datos = request.get_json()
    
    if not datos or not all(k in datos for k in ['usuario_id', 'usuario', 'email', 'password', 'rol']):
        return jsonify({'error': 'Faltan datos requeridos'}), 400
    
    if auth.registrar_usuario(datos['usuario_id'], datos['usuario'], 
                              datos['email'], datos['password'], datos['rol']):
        
        # Registrar en sistema según rol
        if datos['rol'] == 'cliente':
            sistema.registrar_cliente(datos['usuario_id'], datos['usuario'], datos['email'])
            db.insertar_cliente(datos['usuario_id'], datos['usuario'], datos['email'])
        else:
            sistema.registrar_prestador(datos['usuario_id'], datos['usuario'], datos['email'])
            db.insertar_prestador(datos['usuario_id'], datos['usuario'], datos['email'])
        
        return jsonify({'mensaje': 'Usuario registrado exitosamente'}), 201
    else:
        return jsonify({'error': 'El usuario ya existe'}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Autentica un usuario y devuelve un token"""
    datos = request.get_json()
    
    if not datos or 'usuario_id' not in datos or 'password' not in datos:
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
    
    token = auth.autenticar(datos['usuario_id'], datos['password'])
    
    if token:
        usuario = auth.obtener_usuario(datos['usuario_id'])
        return jsonify({
            'token': token,
            'usuario': usuario
        }), 200
    else:
        return jsonify({'error': 'Credenciales inválidas'}), 401

# ==================== API CLIENTES ====================

@app.route('/api/clientes', methods=['GET'])
@token_requerido
def listar_clientes(usuario_id):
    """Lista todos los clientes"""
    clientes = db.listar_clientes()
    return jsonify({
        'total': len(clientes),
        'clientes': clientes
    }), 200

@app.route('/api/clientes/<cliente_id>', methods=['GET'])
@token_requerido
def obtener_cliente(usuario_id, cliente_id):
    """Obtiene información de un cliente"""
    cliente = db.obtener_cliente(cliente_id)
    if cliente:
        return jsonify(cliente), 200
    return jsonify({'error': 'Cliente no encontrado'}), 404

# ==================== API PRESTADORES ====================

@app.route('/api/prestadores', methods=['GET'])
@token_requerido
def listar_prestadores(usuario_id):
    """Lista todos los prestadores"""
    prestadores = db.listar_prestadores()
    return jsonify({
        'total': len(prestadores),
        'prestadores': prestadores
    }), 200

@app.route('/api/prestadores/<prestador_id>', methods=['GET'])
@token_requerido
def obtener_prestador(usuario_id, prestador_id):
    """Obtiene información de un prestador"""
    prestador = db.obtener_prestador(prestador_id)
    if prestador:
        calificaciones = db.obtener_calificaciones_prestador(prestador_id)
        prestador['calificaciones'] = calificaciones
        return jsonify(prestador), 200
    return jsonify({'error': 'Prestador no encontrado'}), 404

# ==================== API SOLICITUDES ====================

@app.route('/api/solicitudes', methods=['GET'])
@token_requerido
def listar_solicitudes(usuario_id):
    """Lista todas las solicitudes"""
    estado = request.args.get('estado')
    cliente_id = request.args.get('cliente_id')
    
    if estado:
        solicitudes = db.listar_solicitudes_por_estado(estado)
    else:
        solicitudes = []
        for s in sistema.solicitudes.values():
            if cliente_id and s.cliente_id != cliente_id:
                continue
            solicitudes.append({
                'solicitud_id': s.id,
                'cliente_id': s.cliente_id,
                'descripcion': s.descripcion,
                'estado': s.estado,
                'prioridad': s.prioridad,
                'fecha_creacion': s.fecha_creacion.isoformat()
            })
    
    return jsonify({
        'total': len(solicitudes),
        'solicitudes': solicitudes
    }), 200

@app.route('/api/solicitudes', methods=['POST'])
@token_requerido
def crear_solicitud(usuario_id):
    """Crea una nueva solicitud"""
    datos = request.get_json()
    
    if not datos or 'cliente_id' not in datos or 'descripcion' not in datos:
        return jsonify({'error': 'Faltan datos requeridos'}), 400
    
    cliente = sistema.obtener_cliente(datos['cliente_id'])
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    
    try:
        solicitud = sistema.crear_solicitud(
            datos['cliente_id'],
            datos['descripcion'],
            datos.get('prioridad', 3)
        )
        db.insertar_solicitud(
            solicitud.id,
            datos['cliente_id'],
            datos['descripcion'],
            datos.get('prioridad', 3)
        )
        return jsonify({
            'mensaje': 'Solicitud creada',
            'solicitud_id': solicitud.id,
            'solicitud': {
                'solicitud_id': solicitud.id,
                'cliente_id': solicitud.cliente_id,
                'descripcion': solicitud.descripcion,
                'estado': solicitud.estado,
                'prioridad': solicitud.prioridad,
                'fecha_creacion': solicitud.fecha_creacion.isoformat()
            }
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/solicitudes/<solicitud_id>', methods=['GET'])
@token_requerido
def obtener_solicitud(usuario_id, solicitud_id):
    """Obtiene detalles de una solicitud"""
    solicitud = sistema.obtener_solicitud(solicitud_id)
    if solicitud:
        asignacion = sistema.obtener_prestador_asignado(solicitud_id)
        progreso = db.obtener_progreso_solicitud(solicitud_id)
        
        return jsonify({
            'solicitud_id': solicitud.id,
            'cliente_id': solicitud.cliente_id,
            'descripcion': solicitud.descripcion,
            'estado': solicitud.estado,
            'prioridad': solicitud.prioridad,
            'fecha_creacion': solicitud.fecha_creacion.isoformat(),
            'prestador_asignado': asignacion.nombre if asignacion else None,
            'progreso': progreso
        }), 200
    return jsonify({'error': 'Solicitud no encontrada'}), 404

@app.route('/api/solicitudes/<solicitud_id>/asignar', methods=['POST'])
@token_requerido
def asignar_solicitud(usuario_id, solicitud_id):
    """Asigna una solicitud a un prestador"""
    datos = request.get_json()
    
    if not datos or 'prestador_id' not in datos:
        return jsonify({'error': 'Prestador ID requerido'}), 400
    
    try:
        sistema.asignar_solicitud(solicitud_id, datos['prestador_id'])
        db.crear_asignacion(solicitud_id, datos['prestador_id'])
        db.actualizar_estado_solicitud(solicitud_id, 'asignada')
        return jsonify({'mensaje': 'Solicitud asignada exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/solicitudes/<solicitud_id>/progreso', methods=['POST'])
@token_requerido
def actualizar_progreso(usuario_id, solicitud_id):
    """Actualiza el progreso de una solicitud"""
    datos = request.get_json()
    
    if not datos or 'porcentaje' not in datos:
        return jsonify({'error': 'Porcentaje requerido'}), 400
    
    try:
        sistema.actualizar_progreso_solicitud(
            solicitud_id,
            datos['porcentaje'],
            datos.get('comentario', '')
        )
        db.registrar_progreso(
            solicitud_id,
            datos['porcentaje'],
            datos.get('comentario', '')
        )
        db.actualizar_estado_solicitud(solicitud_id, 'en_progreso')
        return jsonify({'mensaje': 'Progreso actualizado'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/solicitudes/<solicitud_id>/completar', methods=['POST'])
@token_requerido
def completar_solicitud(usuario_id, solicitud_id):
    """Completa una solicitud"""
    datos = request.get_json()
    
    if not datos or 'resultado' not in datos:
        return jsonify({'error': 'Resultado requerido'}), 400
    
    try:
        sistema.completar_solicitud(solicitud_id, datos['resultado'])
        db.actualizar_estado_solicitud(solicitud_id, 'completada')
        return jsonify({'mensaje': 'Solicitud completada'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ==================== API CALIFICACIONES ====================

@app.route('/api/calificaciones', methods=['POST'])
@token_requerido
def crear_calificacion(usuario_id):
    """Crea una calificación para un prestador"""
    datos = request.get_json()
    
    campos_requeridos = ['cliente_id', 'prestador_id', 'solicitud_id', 'calificacion']
    if not datos or not all(k in datos for k in campos_requeridos):
        return jsonify({'error': 'Faltan datos requeridos'}), 400
    
    try:
        sistema.calificar_prestador(
            datos['cliente_id'],
            datos['prestador_id'],
            datos['calificacion'],
            datos.get('comentario', '')
        )
        db.insertar_calificacion(
            datos['cliente_id'],
            datos['prestador_id'],
            datos['solicitud_id'],
            datos['calificacion'],
            datos.get('comentario', '')
        )
        return jsonify({'mensaje': 'Calificación registrada'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ==================== API ESTADÍSTICAS ====================

@app.route('/api/estadisticas', methods=['GET'])
@token_requerido
def obtener_estadisticas(usuario_id):
    """Obtiene estadísticas del sistema"""
    stats = db.obtener_estadisticas()
    sistema_stats = sistema.obtener_estadisticas_sistema()
    
    return jsonify({
        'estadisticas_db': stats,
        'estadisticas_sistema': sistema_stats
    }), 200

# ==================== RUTAS DE SALUD ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Verifica que la API está funcionando"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    }), 200

# ==================== MANEJO DE ERRORES ====================

@app.errorhandler(404)
def no_encontrado(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def error_interno(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    # Crear carpetas necesarias
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Cargar datos de prueba
    cargar_datos_prueba()
    
    # Ejecutar servidor
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
