from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime
import os
import json

app = Flask(__name__)
CORS(app)

# Inicializar Firebase Admin SDK
firebase_json = os.environ.get("FIREBASE_CONFIG")
cred = credentials.Certificate(json.loads(firebase_json))
firebase_admin.initialize_app(cred)

# Cliente de Firestore
db = firestore.client()

# Ruta principal - servir el HTML
@app.route('/')
def index():
    return render_template('index.html')

# ==================== AUTENTICACIÓN ====================

@app.route('/api/login', methods=['POST'])
def login():
    """Verificar credenciales de usuario"""
    try:
        data = request.json
        username = data.get('username', '').lower().strip()
        password = data.get('password', '').strip()
        
        # Buscar usuario en Firestore
        user_ref = db.collection('usuarios').document(username)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({
                'success': False, 
                'error': 'Usuario no encontrado'
            }), 404
        
        user_data = user_doc.to_dict()
        
        # Verificar contraseña
        if user_data.get('password') != password:
            return jsonify({
                'success': False,
                'error': 'Contraseña incorrecta'
            }), 401
        
        # Registrar último acceso
        now = datetime.now()
        user_ref.update({
            'ultimo_acceso': {
                'fecha': now.strftime('%d/%m/%Y'),
                'hora': now.strftime('%H:%M:%S')
            }
        })
        
        return jsonify({
            'success': True,
            'user': {
                'username': username,
                'ultimo_acceso': user_data.get('ultimo_acceso', {})
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== MENÚ ====================

@app.route('/api/menu', methods=['GET'])
def get_menu():
    """Obtener la carta del menú"""
    try:
        menu_ref = db.collection('menu').stream()
        menu = []
        
        for doc in menu_ref:
            item = doc.to_dict()
            item['id'] = doc.id
            menu.append(item)
        
        return jsonify({
            'success': True,
            'menu': menu
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/menu', methods=['POST'])
def add_menu_item():
    """Agregar un item al menú"""
    try:
        data = request.json
        
        doc_ref = db.collection('menu').add({
            'nombre': data['nombre'],
            'precio': float(data['precio']),
            'activo': True,
            'fecha_creacion': datetime.now()
        })
        
        return jsonify({
            'success': True,
            'id': doc_ref[1].id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== PEDIDOS ====================

@app.route('/api/pedidos', methods=['POST'])
def crear_pedido():
    """Guardar un nuevo pedido"""
    try:
        data = request.json
        
        # Calcular totales
        subtotal = sum(item['subtotal'] for item in data['items'])
        igv = subtotal * 0.18
        total = subtotal + igv
        
        # Crear pedido en Firestore
        pedido = {
            'usuario': data['usuario'],
            'items': data['items'],
            'subtotal': subtotal,
            'igv': igv,
            'total': total,
            'fecha': datetime.now().strftime('%d/%m/%Y'),
            'hora': datetime.now().strftime('%H:%M:%S'),
            'timestamp': datetime.now()
        }
        
        doc_ref = db.collection('pedidos').add(pedido)
        
        return jsonify({
            'success': True,
            'pedido_id': doc_ref[1].id,
            'pedido': pedido
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pedidos', methods=['GET'])
def obtener_pedidos():
    """Obtener historial de pedidos"""
    try:
        # Filtros opcionales
        usuario = request.args.get('usuario')
        fecha = request.args.get('fecha')
        
        query = db.collection('pedidos')
        
        if usuario:
            query = query.where('usuario', '==', usuario)
        if fecha:
            query = query.where('fecha', '==', fecha)
        
        # Ordenar por timestamp descendente
        query = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(50)
        
        pedidos = []
        for doc in query.stream():
            pedido = doc.to_dict()
            pedido['id'] = doc.id
            # Convertir timestamp a string para JSON
            if 'timestamp' in pedido:
                pedido['timestamp'] = pedido['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            pedidos.append(pedido)
        
        return jsonify({
            'success': True,
            'pedidos': pedidos
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== REPORTES ====================

@app.route('/api/reportes/ventas', methods=['GET'])
def reporte_ventas():
    """Generar reporte de ventas"""
    try:
        fecha = request.args.get('fecha')  # formato: dd/mm/yyyy
        
        query = db.collection('pedidos')
        if fecha:
            query = query.where('fecha', '==', fecha)
        
        pedidos = query.stream()
        
        total_ventas = 0
        total_pedidos = 0
        productos_vendidos = {}
        
        for doc in pedidos:
            pedido = doc.to_dict()
            total_ventas += pedido.get('total', 0)
            total_pedidos += 1
            
            # Contar productos
            for item in pedido.get('items', []):
                nombre = item['nombre']
                cantidad = item['cantidad']
                if nombre in productos_vendidos:
                    productos_vendidos[nombre] += cantidad
                else:
                    productos_vendidos[nombre] = cantidad
        
        return jsonify({
            'success': True,
            'reporte': {
                'fecha': fecha or 'Todas las fechas',
                'total_ventas': total_ventas,
                'total_pedidos': total_pedidos,
                'productos_vendidos': productos_vendidos
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== INICIALIZACIÓN ====================

@app.route('/api/init', methods=['POST'])
def initialize_data():
    """Inicializar datos de prueba (solo usar una vez)"""
    try:
        # Crear usuarios por defecto
        usuarios = {
            "admin": "1234",
            "super": "4444"
        }
        
        for username, password in usuarios.items():
            db.collection('usuarios').document(username).set({
                'username': username,
                'password': password,
                'rol': 'admin' if username == 'admin' else 'supervisor',
                'activo': True,
                'fecha_creacion': datetime.now()
            })
        
        # Crear menú por defecto
        carta = [
            {"nombre": "Café Expresso", "precio": 10},
            {"nombre": "Café Clásico", "precio": 8},
            {"nombre": "Espresso Martini", "precio": 12},
            {"nombre": "Carajillo", "precio": 15},
            {"nombre": "Café Calypso", "precio": 13}
        ]
        
        for item in carta:
            db.collection('menu').add({
                'nombre': item['nombre'],
                'precio': item['precio'],
                'activo': True,
                'fecha_creacion': datetime.now()
            })
        
        return jsonify({
            'success': True,
            'message': 'Datos inicializados correctamente'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
