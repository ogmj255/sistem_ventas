# 🚀 Guía de Despliegue en Render

## Variables de Entorno Requeridas

Configura estas variables en el dashboard de Render:

### 🔐 Seguridad
```
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
FLASK_ENV=production
FLASK_DEBUG=false
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
WTF_CSRF_ENABLED=true
```

### 🗄️ Base de Datos
```
MONGO_URI=mongodb+srv://ogmoscosoj_db_user:us64dOby4EtV7PiK@ventasdb.mongodb.net/ventasdb?retryWrites=true&w=majority
```

### ⚙️ Aplicación
```
APP_NAME=GabStore
ADMIN_EMAIL=admin@sistema.com
TIMEZONE=America/Guayaquil
WHATSAPP_NUMBER=+593985051676
```

### 🛡️ Rate Limiting
```
RATELIMIT_STORAGE_URL=memory://
RATELIMIT_DEFAULT=100 per hour
```

### 🖼️ Imágenes
```
IMAGE_RESIZE_SERVICE=images.weserv.nl
DEFAULT_IMAGE_FORMAT=400x200
```

### 📄 Paginación
```
ITEMS_PER_PAGE=10
```

## 📋 Pasos de Despliegue

### 1. Preparar Repositorio
```bash
git init
git add .
git commit -m "Initial commit - GabStore"
git branch -M main
git remote add origin https://github.com/tu-usuario/gabstore.git
git push -u origin main
```

### 2. Configurar en Render
1. Ve a [render.com](https://render.com)
2. Conecta tu repositorio GitHub
3. Selecciona "Web Service"
4. Configura:
   - **Name**: gabstore
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

### 3. Variables de Entorno
Copia todas las variables del archivo `.env.example` al dashboard de Render.

### 4. Despliegue Automático
- Render detectará automáticamente el `render.yaml`
- El despliegue se iniciará automáticamente
- La aplicación estará disponible en: `https://gabstore.onrender.com`

## 🔧 Configuración Adicional

### SSL/HTTPS
Render proporciona SSL automático. Las variables de seguridad están configuradas para producción.

### MongoDB Atlas
La base de datos ya está configurada y funcionando. No requiere cambios adicionales.

### Dominio Personalizado
Para usar un dominio personalizado:
1. Ve a Settings en tu servicio de Render
2. Agrega tu dominio en "Custom Domains"
3. Configura los DNS según las instrucciones

## 🚨 Importante

- **Nunca** subas el archivo `.env` al repositorio
- Usa siempre variables de entorno en producción
- La aplicación se reiniciará automáticamente con cada push a main
- Los logs están disponibles en el dashboard de Render

## 📞 Soporte

Si tienes problemas con el despliegue:
1. Revisa los logs en Render
2. Verifica que todas las variables estén configuradas
3. Asegúrate de que MongoDB Atlas esté accesible