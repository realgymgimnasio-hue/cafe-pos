# Sistema POS Café Bar 40° con Firebase

Sistema de punto de venta integrado con Firebase y Flask.

## 📋 Requisitos Previos

1. Python 3.8 o superior
2. Cuenta de Firebase
3. Archivo de credenciales de Firebase

## 🚀 Configuración Inicial

### 1. Configurar Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com)
2. Crea un nuevo proyecto o selecciona uno existente
3. Ve a **Project Settings** (⚙️ icono) > **Service Accounts**
4. Haz clic en **Generate New Private Key**
5. Descarga el archivo JSON
6. Renombra el archivo a `firebase_config.json`
7. Coloca el archivo en la raíz del proyecto (carpeta `cafe_pos/`)

### 2. Habilitar Firestore

1. En Firebase Console, ve a **Build** > **Firestore Database**
2. Haz clic en **Create Database**
3. Selecciona **Start in production mode** (o test mode para desarrollo)
4. Elige una ubicación cercana (ejemplo: `southamerica-east1`)

### 3. Instalar Dependencias

```bash
cd cafe_pos
pip install -r requirements.txt --break-system-packages
```

### 4. Inicializar la Base de Datos

Ejecuta el servidor:
```bash
python app.py
```

En otra terminal o usando Postman/curl, inicializa los datos:
```bash
curl -X POST http://localhost:5000/api/init
```

Esto creará:
- **Usuarios**: admin (1234), super (4444)
- **Menú**: Los 5 productos de café

## 🎯 Ejecutar la Aplicación

```bash
python app.py
```

Abre tu navegador en: `http://localhost:5000`

## 🔐 Credenciales por Defecto

- Usuario: `admin` | Contraseña: `1234`
- Usuario: `super` | Contraseña: `4444`

## 📊 Estructura del Proyecto

```
cafe_pos/
├── app.py                    # Backend Flask
├── requirements.txt          # Dependencias Python
├── firebase_config.json      # Credenciales Firebase (NO SUBIR A GIT)
├── templates/
│   └── index.html           # Frontend HTML
└── static/
    ├── script.js            # Lógica JavaScript
    └── styles.css           # Estilos CSS
```

## 🗄️ Estructura de Firebase

### Colección: `usuarios`
```json
{
  "admin": {
    "username": "admin",
    "password": "1234",
    "rol": "admin",
    "activo": true,
    "ultimo_acceso": {
      "fecha": "27/01/2026",
      "hora": "10:30:00"
    }
  }
}
```

### Colección: `menu`
```json
{
  "id_auto": {
    "nombre": "Café Expresso",
    "precio": 10,
    "activo": true
  }
}
```

### Colección: `pedidos`
```json
{
  "id_auto": {
    "usuario": "admin",
    "items": [
      {
        "nombre": "Café Expresso",
        "precio": 10,
        "cantidad": 2,
        "subtotal": 20
      }
    ],
    "subtotal": 20,
    "igv": 3.6,
    "total": 23.6,
    "fecha": "27/01/2026",
    "hora": "10:30:00",
    "timestamp": "Timestamp"
  }
}
```

## 🔌 Endpoints de la API

### Autenticación
- `POST /api/login` - Iniciar sesión

### Menú
- `GET /api/menu` - Obtener menú
- `POST /api/menu` - Agregar item al menú

### Pedidos
- `POST /api/pedidos` - Crear pedido
- `GET /api/pedidos` - Obtener historial
  - Query params: `?usuario=admin&fecha=27/01/2026`

### Reportes
- `GET /api/reportes/ventas` - Reporte de ventas
  - Query params: `?fecha=27/01/2026`

### Utilidades
- `POST /api/init` - Inicializar datos (usar solo una vez)

## 🔒 Seguridad

⚠️ **IMPORTANTE**: Nunca subas `firebase_config.json` a repositorios públicos

Crea un archivo `.gitignore`:
```
firebase_config.json
__pycache__/
*.pyc
.env
venv/
```

## 📱 Características

✅ Login de usuarios con Firebase
✅ Menú dinámico desde Firestore
✅ Carrito de compras
✅ Generación de tickets
✅ Historial de pedidos
✅ Reportes de ventas
✅ Cálculo automático de IGV (18%)
✅ Registro de último acceso

## 🐛 Solución de Problemas

### Error: "No module named 'firebase_admin'"
```bash
pip install firebase-admin --break-system-packages
```

### Error: "Could not open firebase_config.json"
Asegúrate de que el archivo esté en la carpeta raíz del proyecto.

### Error de CORS
Ya está configurado Flask-CORS, pero si hay problemas:
```bash
pip install flask-cors --break-system-packages
```

## 📈 Próximas Mejoras

- [ ] Panel de administración
- [ ] Gestión de usuarios desde la UI
- [ ] Reportes gráficos
- [ ] Autenticación con Firebase Auth
- [ ] Modo offline con sincronización
- [ ] Impresión térmica

## 📞 Soporte

Para más información sobre Firebase:
- [Documentación Firebase](https://firebase.google.com/docs)
- [Firestore Quickstart](https://firebase.google.com/docs/firestore/quickstart)
