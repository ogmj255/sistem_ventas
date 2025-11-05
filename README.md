# 🛒 Sistema de Ventas - MongoDB Atlas

Sistema de ventas seguro con autenticación 2FA y MongoDB Atlas.

## 🚀 Configuración Rápida

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar MongoDB Atlas
Tu cluster **ventasdb** ya está configurado con:
- **Usuario**: ogmoscosoj_db_user
- **Password**: us64dOby4EtV7PiK
- **Cluster**: ventasdb.mongodb.net

### 3. Inicializar base de datos
```bash
python init_atlas.py
```

### 4. Ejecutar aplicación
```bash
python app.py
```

## 🔐 Credenciales de Acceso

**Admin por defecto:**
- Email: `admin@sistema.com`
- Password: `Admin123!`

## 📊 Funcionalidades

### ✅ Seguridad
- 🔒 Autenticación 2FA con Google Authenticator
- 🛡️ Rate limiting anti-brute force
- 🔐 Headers de seguridad (Talisman)
- 🚫 Protección CSRF
- 🔑 Hashing seguro de passwords

### ✅ Base de Datos
- 🌐 MongoDB Atlas (512MB gratis)
- 📊 Índices optimizados
- 🔄 Conexión con pool de conexiones
- 💾 Backups automáticos

### ✅ API REST
- `GET /api/accounts` - Listar cuentas (Admin)
- Autenticación requerida
- Respuestas JSON

## 🛠️ Comandos CLI

```bash
# Crear admin adicional
flask create-admin

# Agregar cuentas de ejemplo
flask seed-accounts
```

## 🌐 Despliegue en Producción

### Heroku
```bash
git init
git add .
git commit -m "Initial commit"
heroku create tu-app-name
git push heroku main
```

### Railway
```bash
railway login
railway init
railway up
```

### Render
1. Conectar repositorio GitHub
2. Configurar variables de entorno
3. Deploy automático

## 🔧 Variables de Entorno

```env
SECRET_KEY=tu_clave_secreta_muy_segura
FLASK_ENV=production
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/db
```

## 📱 Estructura del Proyecto

```
sistema_ventas/
├── app.py              # Aplicación principal
├── models.py           # Modelos MongoDB
├── forms.py            # Formularios WTF
├── config.py           # Configuración
├── init_atlas.py       # Script inicialización
├── requirements.txt    # Dependencias
├── templates/          # Templates HTML
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   ├── setup_2fa.html
│   └── twofa.html
└── static/            # CSS/JS/Images
    └── style.css
```

## 🎯 Próximas Mejoras

- [ ] Panel de administración web
- [ ] Sistema de pagos (Stripe/PayPal)
- [ ] Notificaciones por email
- [ ] Dashboard con gráficos
- [ ] API completa CRUD
- [ ] Sistema de roles avanzado

## 🆘 Soporte

Si tienes problemas:
1. Verifica la conexión a MongoDB Atlas
2. Revisa las variables de entorno
3. Ejecuta `python init_atlas.py` nuevamente"# sistem_ventas" 
