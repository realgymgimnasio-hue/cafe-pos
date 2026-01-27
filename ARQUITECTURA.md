# 🏗️ ARQUITECTURA DEL SISTEMA

## Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────┐
│                      NAVEGADOR WEB                          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  index.html  │  │  styles.css  │  │  script.js   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                                    │              │
│         └────────────────┬──────────────────┘              │
└──────────────────────────│──────────────────────────────────┘
                           │
                           │ HTTP Requests
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     FLASK SERVER                             │
│                     (app.py)                                 │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │             RUTAS / ENDPOINTS                         │  │
│  │                                                       │  │
│  │  /api/login         → Autenticación                  │  │
│  │  /api/menu          → Obtener/Crear menú            │  │
│  │  /api/pedidos       → Crear/Obtener pedidos         │  │
│  │  /api/reportes      → Generar reportes              │  │
│  │  /api/init          → Inicializar datos             │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           │ Firebase Admin SDK               │
└───────────────────────────│──────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    FIREBASE CLOUD                            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              FIRESTORE DATABASE                       │  │
│  │                                                       │  │
│  │  📦 Colección: usuarios                              │  │
│  │     └─ admin {username, password, rol, ...}          │  │
│  │     └─ super {username, password, rol, ...}          │  │
│  │                                                       │  │
│  │  📦 Colección: menu                                  │  │
│  │     └─ doc1 {nombre, precio, activo}                 │  │
│  │     └─ doc2 {nombre, precio, activo}                 │  │
│  │     └─ ...                                           │  │
│  │                                                       │  │
│  │  📦 Colección: pedidos                               │  │
│  │     └─ pedido1 {usuario, items, total, fecha}       │  │
│  │     └─ pedido2 {usuario, items, total, fecha}       │  │
│  │     └─ ...                                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Flujo de Datos: Login

```
Usuario escribe credenciales
         │
         ▼
script.js: función login()
         │
         │ fetch('/api/login', {username, password})
         ▼
app.py: @app.route('/api/login')
         │
         ├─ Busca usuario en Firestore
         │  db.collection('usuarios').document(username)
         │
         ├─ Verifica contraseña
         │
         ├─ Actualiza último acceso
         │  user_ref.update({ultimo_acceso: {...}})
         │
         ▼
Responde: {success: true, user: {...}}
         │
         ▼
script.js: Muestra pantalla de menú
```

---

## Flujo de Datos: Crear Pedido

```
Usuario selecciona productos
         │
         ▼
script.js: Actualiza carrito
         │
         ▼
Usuario hace clic en "Finalizar Compra"
         │
         ▼
script.js: función generateTicket()
         │
         │ fetch('/api/pedidos', {usuario, items})
         ▼
app.py: @app.route('/api/pedidos')
         │
         ├─ Calcula subtotal, IGV, total
         │
         ├─ Crea objeto pedido
         │  {usuario, items, subtotal, igv, total, fecha, hora}
         │
         ├─ Guarda en Firestore
         │  db.collection('pedidos').add(pedido)
         │
         ▼
Responde: {success: true, pedido_id, pedido}
         │
         ▼
script.js: Genera y muestra ticket HTML
```

---

## Componentes del Sistema

### FRONTEND (Cliente)

**Archivos:**
- `index.html` - Estructura (login, menú, ticket)
- `styles.css` - Diseño visual
- `script.js` - Lógica e interacción

**Responsabilidades:**
- Mostrar interfaz de usuario
- Capturar eventos (clicks, inputs)
- Hacer peticiones HTTP a Flask
- Renderizar datos (menú, carrito, ticket)

---

### BACKEND (Servidor)

**Archivo:**
- `app.py` - Servidor Flask

**Responsabilidades:**
- Servir archivos estáticos (HTML, CSS, JS)
- Procesar peticiones API
- Validar datos
- Interactuar con Firebase
- Cálculos (totales, IGV)
- Generar respuestas JSON

---

### DATABASE (Firebase)

**Servicio:**
- Firestore Database

**Responsabilidades:**
- Almacenar usuarios
- Almacenar menú
- Almacenar pedidos
- Persistencia de datos
- Consultas y filtros

---

## Tecnologías Utilizadas

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos y diseño responsivo
- **JavaScript (Vanilla)** - Lógica del cliente
- **Fetch API** - Peticiones HTTP

### Backend
- **Python 3.8+** - Lenguaje
- **Flask** - Framework web
- **Flask-CORS** - Manejo de CORS

### Base de Datos
- **Firebase Firestore** - Base de datos NoSQL
- **Firebase Admin SDK** - Interacción desde Python

---

## Seguridad

### Autenticación
- Login con usuario y contraseña
- Validación en el servidor
- Registro de último acceso

### Datos
- Credenciales en archivo separado
- `.gitignore` para archivos sensibles
- CORS configurado

### Mejoras Recomendadas
- [ ] Hash de contraseñas (bcrypt)
- [ ] Tokens JWT
- [ ] Firebase Authentication
- [ ] HTTPS en producción
- [ ] Rate limiting
- [ ] Validación de inputs

---

## Escalabilidad

### Actual
- Maneja múltiples usuarios concurrentes
- Firebase escala automáticamente
- Flask en modo desarrollo

### Para Producción
- **Servidor**: Gunicorn + Nginx
- **Hosting**: Google Cloud Run / Heroku
- **SSL**: Let's Encrypt
- **CDN**: Cloudflare
- **Monitoreo**: Firebase Analytics

---

## Modelo de Datos Firestore

### Colección: usuarios
```
usuarios/
  ├─ admin/
  │    ├─ username: "admin"
  │    ├─ password: "1234"
  │    ├─ rol: "admin"
  │    ├─ activo: true
  │    └─ ultimo_acceso: {fecha, hora}
  │
  └─ super/
       ├─ username: "super"
       ├─ password: "4444"
       ├─ rol: "supervisor"
       └─ ...
```

### Colección: menu
```
menu/
  ├─ [auto-id-1]/
  │    ├─ nombre: "Café Expresso"
  │    ├─ precio: 10
  │    ├─ activo: true
  │    └─ fecha_creacion: Timestamp
  │
  ├─ [auto-id-2]/
  │    ├─ nombre: "Café Clásico"
  │    └─ ...
  └─ ...
```

### Colección: pedidos
```
pedidos/
  ├─ [auto-id-1]/
  │    ├─ usuario: "admin"
  │    ├─ items: [
  │    │    {nombre, precio, cantidad, subtotal},
  │    │    {...}
  │    │  ]
  │    ├─ subtotal: 20
  │    ├─ igv: 3.6
  │    ├─ total: 23.6
  │    ├─ fecha: "27/01/2026"
  │    ├─ hora: "14:30:00"
  │    └─ timestamp: Timestamp
  └─ ...
```

---

## Performance

### Optimizaciones Implementadas
- ✅ Carga del menú desde Firebase (una vez)
- ✅ Carrito en memoria del cliente
- ✅ Límite de 50 pedidos en consultas
- ✅ Índices automáticos de Firestore

### Métricas Esperadas
- **Tiempo de login**: < 500ms
- **Carga de menú**: < 300ms
- **Creación de pedido**: < 1s
- **Generación de ticket**: < 100ms

---

## Monitoreo

### Firebase Console
- Número de lecturas/escrituras
- Uso de almacenamiento
- Usuarios activos

### Logs de Flask
```python
app.logger.info(f"Usuario {username} inició sesión")
app.logger.error(f"Error al crear pedido: {str(e)}")
```

### Métricas Recomendadas
- Total de ventas por día
- Producto más vendido
- Horas pico
- Usuarios activos
- Tiempo promedio de pedido
