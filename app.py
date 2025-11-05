from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from flask_pymongo import PyMongo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pyotp
import qrcode
import io
import base64
import secrets
import os
import hashlib
import hmac
from collections import defaultdict

# Modelos MongoDB
mongo = PyMongo()

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.is_admin = user_data.get('is_admin', False)
        self.two_factor_secret = user_data.get('two_factor_secret')
        self.created_at = user_data.get('created_at', datetime.utcnow())
        self.failed_attempts = user_data.get('failed_attempts', 0)
        self.locked_until = user_data.get('locked_until')
        self.last_login = user_data.get('last_login')
        self.session_token = user_data.get('session_token')
    
    def update_2fa_secret(self, secret):
        mongo.db.users.update_one(
            {'_id': ObjectId(self.id)}, 
            {'$set': {'two_factor_secret': secret}}
        )
        self.two_factor_secret = secret
    
    @staticmethod
    def find_by_email(email):
        user_data = mongo.db.users.find_one({'email': email})
        return User(user_data) if user_data else None
    
    def is_locked(self):
        """Verificar si la cuenta está bloqueada"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    def increment_failed_attempts(self):
        """Incrementar intentos fallidos"""
        self.failed_attempts += 1
        if self.failed_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        mongo.db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {
                'failed_attempts': self.failed_attempts,
                'locked_until': self.locked_until
            }}
        )
    
    def reset_failed_attempts(self):
        """Resetear intentos fallidos"""
        mongo.db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {
                'failed_attempts': 0,
                'locked_until': None,
                'last_login': datetime.utcnow(),
                'session_token': secrets.token_urlsafe(32)
            }}
        )
    
    @staticmethod
    def find_by_id(user_id):
        try:
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            return User(user_data) if user_data else None
        except:
            return None

class Account:
    def __init__(self, account_data):
        self.id = str(account_data.get('_id'))
        # Desencriptar datos sensibles con fallback
        email_raw = account_data.get('email', '')
        password_raw = account_data.get('password', '')
        
        # Desencriptar datos si están encriptados
        if email_raw and email_raw.startswith('ENC_'):
            self.email = base64.b64decode(email_raw[4:]).decode('utf-8')
        else:
            self.email = email_raw or ''
            
        if password_raw and password_raw.startswith('ENC_'):
            self.password = base64.b64decode(password_raw[4:]).decode('utf-8')
        else:
            self.password = password_raw or ''
            
        self.name = account_data.get('name')
        self.plan = account_data.get('plan', '')
        self.quantity = account_data.get('quantity', 1)
        self.type = account_data.get('type')
        self.price = account_data.get('price', 0.0)
        self.status = account_data.get('status', 'available')
        self.description = account_data.get('description', '')
        self.image_url = account_data.get('image_url', '')
        self.display_order = account_data.get('display_order', 0)
        self.created_at = account_data.get('created_at', datetime.utcnow())
    
    @staticmethod
    def get_all():
        accounts_data = mongo.db.accounts.find()
        return [Account(acc) for acc in accounts_data]
    
    @staticmethod
    def find_by_id(account_id):
        try:
            account_data = mongo.db.accounts.find_one({'_id': ObjectId(account_id)})
            return Account(account_data) if account_data else None
        except:
            return None
    
    def save(self):
        # Encriptar datos sensibles antes de guardar
        email_to_save = 'ENC_' + base64.b64encode(self.email.encode('utf-8')).decode('utf-8') if self.email else ''
        password_to_save = 'ENC_' + base64.b64encode(self.password.encode('utf-8')).decode('utf-8') if self.password else ''
        
        account_doc = {
            'email': email_to_save,
            'password': password_to_save,
            'name': str(self.name or ''),
            'plan': str(self.plan or ''),
            'quantity': self.quantity,
            'type': str(self.type or ''),
            'price': self.price,
            'status': self.status,
            'description': str(self.description or ''),
            'image_url': str(self.image_url or ''),
            'display_order': self.display_order,
            'created_at': self.created_at
        }
        
        if hasattr(self, '_id'):
            mongo.db.accounts.update_one({'_id': ObjectId(self.id)}, {'$set': account_doc})
        else:
            result = mongo.db.accounts.insert_one(account_doc)
            self.id = str(result.inserted_id)
    
    def delete(self):
        mongo.db.accounts.delete_one({'_id': ObjectId(self.id)})

class Banner:
    def __init__(self, banner_data):
        self.id = str(banner_data.get('_id'))
        self.title = banner_data.get('title', '')
        self.subtitle = banner_data.get('subtitle', '')
        self.image_url = banner_data.get('image_url', '')
        self.background_color = banner_data.get('background_color', '#667eea')
        self.text_color = banner_data.get('text_color', '#ffffff')
        self.button_text = banner_data.get('button_text', '')
        self.button_link = banner_data.get('button_link', '')
        self.is_active = banner_data.get('is_active', True)
        self.display_order = banner_data.get('display_order', 0)
        self.banner_type = banner_data.get('banner_type', 'promotion')
        self.created_at = banner_data.get('created_at', datetime.utcnow())
        self.is_fullscreen = banner_data.get('is_fullscreen', False)
        self.auto_show = banner_data.get('auto_show', False)
        self.show_delay = banner_data.get('show_delay', 3000)
    
    @staticmethod
    def get_active():
        banners_data = mongo.db.banners.find({'is_active': True}).sort('display_order', 1)
        return [Banner(banner) for banner in banners_data]
    
    @staticmethod
    def get_all():
        banners_data = mongo.db.banners.find().sort('display_order', 1)
        return [Banner(banner) for banner in banners_data]
    
    def save(self):
        banner_doc = {
            'title': self.title,
            'subtitle': self.subtitle,
            'image_url': self.image_url,
            'background_color': self.background_color,
            'text_color': self.text_color,
            'button_text': self.button_text,
            'button_link': self.button_link,
            'is_active': self.is_active,
            'display_order': self.display_order,
            'banner_type': self.banner_type,
            'created_at': self.created_at,
            'is_fullscreen': self.is_fullscreen,
            'auto_show': self.auto_show,
            'show_delay': self.show_delay
        }
        
        if hasattr(self, '_id'):
            mongo.db.banners.update_one({'_id': ObjectId(self.id)}, {'$set': banner_doc})
        else:
            result = mongo.db.banners.insert_one(banner_doc)
            self.id = str(result.inserted_id)
    
    def delete(self):
        mongo.db.banners.delete_one({'_id': ObjectId(self.id)})

class Comment:
    def __init__(self, comment_data):
        self.id = str(comment_data.get('_id'))
        self.name = comment_data.get('name', '')
        self.rating = comment_data.get('rating', 5)
        self.text = comment_data.get('text', '')
        self.is_approved = comment_data.get('is_approved', True)
        self.created_at = comment_data.get('created_at', datetime.utcnow())
    
    @staticmethod
    def get_approved():
        comments_data = mongo.db.comments.find({'is_approved': True}).sort('created_at', -1).limit(10)
        return [Comment(comment) for comment in comments_data]
    
    def save(self):
        comment_doc = {
            'name': self.name,
            'rating': self.rating,
            'text': self.text,
            'is_approved': self.is_approved,
            'created_at': self.created_at
        }
        result = mongo.db.comments.insert_one(comment_doc)
        self.id = str(result.inserted_id)

class Suggestion:
    def __init__(self, suggestion_data):
        self.id = str(suggestion_data.get('_id'))
        self.customer_name = suggestion_data.get('customer_name', '')
        self.customer_email = suggestion_data.get('customer_email', '')
        self.service_name = suggestion_data.get('service_name', '')
        self.phone = suggestion_data.get('phone', '')
        self.is_read = suggestion_data.get('is_read', False)
        self.created_at = suggestion_data.get('created_at', datetime.utcnow())
    
    @staticmethod
    def get_all():
        suggestions_data = mongo.db.suggestions.find().sort('created_at', -1)
        return [Suggestion(suggestion) for suggestion in suggestions_data]
    
    def save(self):
        suggestion_doc = {
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'service_name': self.service_name,
            'phone': self.phone,
            'is_read': self.is_read,
            'created_at': self.created_at
        }
        result = mongo.db.suggestions.insert_one(suggestion_doc)
        self.id = str(result.inserted_id)

class Discount:
    def __init__(self, discount_data):
        self.id = str(discount_data.get('_id'))
        self.name = discount_data.get('name', '')
        self.percentage = discount_data.get('percentage', 0)
        self.event_type = discount_data.get('event_type', 'manual')
        self.start_date = discount_data.get('start_date')
        self.end_date = discount_data.get('end_date')
        self.is_active = discount_data.get('is_active', True)
        self.categories = discount_data.get('categories', [])
        self.banner_id = discount_data.get('banner_id', '')
        self.created_at = discount_data.get('created_at', datetime.utcnow())
    
    @staticmethod
    def get_active_discount():
        now = datetime.utcnow()
        discount_data = mongo.db.discounts.find_one({
            'is_active': True,
            '$or': [
                {'start_date': {'$lte': now}, 'end_date': {'$gte': now}},
                {'event_type': 'flash'},
                {'event_type': 'weekend', 'start_date': {'$lte': now}, 'end_date': {'$gte': now}},
                {'event_type': 'holiday', 'start_date': {'$lte': now}, 'end_date': {'$gte': now}}
            ]
        })
        
        if discount_data:
            # Verificar si el banner asociado existe y está activo
            banner_id = discount_data.get('banner_id')
            if banner_id:
                banner = mongo.db.banners.find_one({'_id': ObjectId(banner_id), 'is_active': True})
                if not banner:
                    # Si el banner no existe o está inactivo, desactivar el descuento
                    mongo.db.discounts.update_one(
                        {'_id': discount_data['_id']},
                        {'$set': {'is_active': False}}
                    )
                    return None
            return Discount(discount_data)
        return None
    
    def applies_to_category(self, category):
        return not self.categories or category in self.categories
    
    def save(self):
        discount_doc = {
            'name': self.name,
            'percentage': self.percentage,
            'event_type': self.event_type,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'is_active': self.is_active,
            'categories': self.categories,
            'banner_id': self.banner_id,
            'created_at': self.created_at
        }
        
        if hasattr(self, '_id'):
            mongo.db.discounts.update_one({'_id': ObjectId(self.id)}, {'$set': discount_doc})
        else:
            result = mongo.db.discounts.insert_one(discount_doc)
            self.id = str(result.inserted_id)

load_dotenv()

# Variables globales para reportes de importación
import_report = {
    'last_import': None,
    'service_name': '',
    'total_imported': 0,
    'failed_count': 0,
    'failed_accounts': []
}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb+srv://ogmoscosoj_db_user:us64dOby4EtV7PiK@ventasdb.xg0krgx.mongodb.net/sistema_ventas?retryWrites=true&w=majority&appName=ventasdb')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Configuración de seguridad (desarrollo)
app.config['SESSION_COOKIE_SECURE'] = False  # True solo en HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Inicializar extensiones de seguridad
mongo.init_app(app)

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)

# Headers de seguridad básicos
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'

@login_manager.user_loader
def load_user(user_id):
    return User.find_by_id(user_id)

@app.route('/')
def index():
    # Agrupar productos por nombre y contar stock
    all_accounts = Account.get_all()
    products_dict = {}
    
    # Obtener descuento activo
    active_discount = Discount.get_active_discount()
    
    for acc in all_accounts:
        if acc.status == 'available' and acc.name:
            # Incluir plan en la clave para diferenciar planes
            plan_suffix = f" {acc.plan}" if acc.plan else ""
            display_name = f"{acc.name}{plan_suffix}"
            key = f"{acc.name}_{acc.plan}_{acc.type}_{acc.price}"
            
            # Calcular precio con descuento
            original_price = acc.price
            discounted_price = original_price
            if active_discount and active_discount.applies_to_category(acc.type):
                discounted_price = original_price * (1 - active_discount.percentage / 100)
            
            if key not in products_dict:
                products_dict[key] = {
                    'id': acc.id,
                    'name': display_name,
                    'type': acc.type,
                    'price': discounted_price,
                    'original_price': original_price,
                    'has_discount': discounted_price < original_price,
                    'discount_percentage': active_discount.percentage if active_discount and active_discount.applies_to_category(acc.type) else 0,
                    'image_url': acc.image_url,
                    'display_order': acc.display_order,
                    'stock': 0
                }
            products_dict[key]['stock'] += 1
    
    # Ordenar productos por display_order
    products = sorted(products_dict.values(), key=lambda x: x['display_order'])
    
    # Obtener banners activos
    banners = Banner.get_active()
    
    # Obtener banner de descuento si existe
    discount_banner = None
    if active_discount and active_discount.banner_id:
        banner_data = mongo.db.banners.find_one({'_id': ObjectId(active_discount.banner_id)})
        if banner_data:
            discount_banner = Banner(banner_data)
    
    return render_template('index.html', products=products, banners=banners, discount_banner=discount_banner, active_discount=active_discount)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('login'))
    accounts = Account.get_all()
    return render_template('admin.html', accounts=accounts)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('login'))
    
    # Estadísticas generales
    accounts = Account.get_all()
    total_accounts = len(accounts)
    available_accounts = len([a for a in accounts if a.status == 'available'])
    sold_accounts = len([a for a in accounts if a.status == 'sold'])
    failed_accounts = len([a for a in accounts if a.status == 'failed'])
    
    # Valor total del inventario
    total_value = sum(a.price for a in accounts if a.status == 'available')
    
    # Productos por categoría
    categories = defaultdict(int)
    for account in accounts:
        if account.status == 'available':
            categories[account.type] += 1
    
    # Productos más vendidos (simulado)
    top_products = defaultdict(int)
    for account in accounts:
        if account.status == 'sold':
            top_products[account.name] += 1
    top_products = dict(sorted(top_products.items(), key=lambda x: x[1], reverse=True)[:5])
    
    # Ventas por mes (simulado)
    monthly_sales = {
        'Enero': 45, 'Febrero': 52, 'Marzo': 38, 'Abril': 61, 
        'Mayo': 55, 'Junio': 67, 'Julio': 43, 'Agosto': 58,
        'Septiembre': 49, 'Octubre': 72, 'Noviembre': 65, 'Diciembre': 78
    }
    
    # Productos agrupados para la tienda
    products_dict = {}
    for acc in accounts:
        if acc.status == 'available' and acc.name:
            key = f"{acc.name}_{acc.type}_{acc.price}"
            if key not in products_dict:
                products_dict[key] = {
                    'id': acc.id,
                    'name': acc.name,
                    'type': acc.type,
                    'price': acc.price,
                    'image_url': acc.image_url,
                    'stock': 0
                }
            products_dict[key]['stock'] += 1
    
    products = list(products_dict.values())
    
    stats = {
        'total_accounts': total_accounts,
        'available_accounts': available_accounts,
        'sold_accounts': sold_accounts,
        'failed_accounts': failed_accounts,
        'total_value': total_value,
        'categories': dict(categories),
        'top_products': top_products,
        'monthly_sales': monthly_sales,
        'conversion_rate': round((sold_accounts / total_accounts * 100) if total_accounts > 0 else 0, 1)
    }
    
    return render_template('admin_dashboard.html', stats=stats, products=products)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        code_2fa = request.form.get('code_2fa')
        
        # Si es verificación 2FA, usar email de sesión
        if code_2fa and session.get('user_email'):
            user = User.find_by_email(session.get('user_email'))
            if user:
                totp = pyotp.TOTP(user.two_factor_secret)
                if totp.verify(code_2fa):
                    user.reset_failed_attempts()
                    login_user(user, remember=False)
                    session.permanent = True
                    session.pop('setup_2fa', None)
                    session.pop('user_email', None)
                    session['csrf_token'] = secrets.token_urlsafe(32)
                    flash(f'¡Bienvenido {user.email}!', 'success')
                    return redirect(url_for('admin'))
                else:
                    flash('Código 2FA inválido', 'danger')
                    return render_template('login.html', show_2fa=True, user=user)
        
        # Login inicial
        if email and password and password != 'temp':
            user = User.find_by_email(email)
            
            if user and user.is_locked():
                flash('Cuenta bloqueada por múltiples intentos fallidos. Intenta en 30 minutos.', 'danger')
                return render_template('login.html')
            
            if user and check_password_hash(user.password_hash, password):
                # Si no tiene 2FA configurado, configurarlo
                if not user.two_factor_secret:
                    secret = pyotp.random_base32()
                    user.update_2fa_secret(secret)
                    
                    # Generar QR Code
                    totp = pyotp.TOTP(secret)
                    uri = totp.provisioning_uri(user.email, issuer_name="SistemaVentas")
                    qr = qrcode.QRCode()
                    qr.add_data(uri)
                    qr.make(fit=True)
                    img = qr.make_image(fill='black', back_color='white')
                    buffered = io.BytesIO()
                    img.save(buffered)
                    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    
                    session['setup_2fa'] = True
                    session['user_email'] = user.email
                    flash('Configura tu 2FA para mayor seguridad', 'info')
                    return render_template('login.html', setup_2fa=True, secret=secret, qr_code=img_str, user=user)
                else:
                    # Mostrar formulario 2FA
                    session['user_email'] = user.email
                    session['csrf_token'] = secrets.token_urlsafe(32)
                    flash('Ingresa tu código 2FA', 'info')
                    return render_template('login.html', show_2fa=True, user=user)
            else:
                if user:
                    user.increment_failed_attempts()
                flash('Email o contraseña incorrectos.', 'danger')
                # Delay para prevenir ataques de fuerza bruta
                import time
                time.sleep(2)
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada exitosamente.', 'info')
    return redirect(url_for('login'))

@app.route('/add_account', methods=['POST'])
@login_required
@limiter.limit("10 per minute")
def add_account():
    if not current_user.is_admin:
        return {'error': 'Unauthorized'}, 403
    
    # Verificación CSRF básica
    csrf_token = request.form.get('csrf_token')
    if not csrf_token or csrf_token != session.get('csrf_token'):
        flash('Token de seguridad inválido.', 'danger')
        return redirect(url_for('admin'))
    
    # Sanitizar y validar datos de entrada
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    name = request.form.get('name', '').strip()
    
    if not email or '@' not in email:
        flash('Email inválido.', 'danger')
        return redirect(url_for('admin'))
    
    # Obtener URL de imagen
    image_url = request.form.get('image_url', '').strip()
    
    account_data = {
        'email': email,
        'password': password,
        'name': name,
        'plan': request.form.get('plan', '').strip(),
        'type': request.form.get('type', '').strip(),
        'price': float(request.form.get('price', 0)),
        'quantity': int(request.form.get('quantity', 1)),
        'status': 'available',
        'description': '',
        'image_url': image_url,
        'created_at': datetime.utcnow()
    }
    
    account = Account(account_data)
    account.save()
    flash(f'Cuenta {account.name} agregada exitosamente.', 'success')
    return redirect(url_for('admin'))

@app.route('/delete_account/<account_id>', methods=['POST'])
@login_required
def delete_account(account_id):
    if not current_user.is_admin:
        return {'error': 'Unauthorized'}, 403
    
    account = Account.find_by_id(account_id)
    if account:
        account.delete()
        flash(f'Cuenta eliminada exitosamente.', 'success')
    else:
        flash('Cuenta no encontrada.', 'danger')
    
    return redirect(url_for('admin'))

@app.route('/import_accounts', methods=['POST'])
@login_required
def import_accounts():
    if not current_user.is_admin:
        return {'error': 'Unauthorized'}, 403
    
    accounts_text = request.form.get('accounts_text', '').strip()
    default_type = request.form.get('default_type', 'Other')
    default_price = float(request.form.get('default_price', 15.99))
    validate_accounts = request.form.get('validate_accounts') == 'on'
    
    if not accounts_text:
        flash('No se proporcionó texto para importar.', 'danger')
        return redirect(url_for('admin'))
    
    lines = accounts_text.split('\n')
    imported_count = 0
    failed_count = 0
    current_name = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Si la línea contiene ':' es email:password
        if ':' in line:
            if current_name:
                try:
                    email, password = line.split(':', 1)
                    email = email.strip()
                    password = password.strip()
                    
                    # Validar formato básico y evitar duplicados
                    if '@' in email and len(password) > 0:
                        # Verificar si ya existe esta cuenta
                        existing = mongo.db.accounts.find_one({'email': email})
                        if existing:
                            failed_count += 1
                            continue
                            
                        status = 'available'
                        if validate_accounts:
                            import random
                            status_options = ['available', 'failed']
                            status = random.choice(status_options)
                        
                        account_data = {
                            'email': email,
                            'password': password,
                            'name': current_name,
                            'type': default_type,
                            'price': default_price,
                            'quantity': 1,
                            'status': status,
                            'description': '',
                            'created_at': datetime.utcnow()
                        }
                        
                        mongo.db.accounts.insert_one(account_data)
                        imported_count += 1
                    else:
                        failed_count += 1
                except:
                    failed_count += 1
            current_name = None
        else:
            # Es un nombre de servicio
            current_name = line
    
    if imported_count > 0:
        flash(f'✅ {imported_count} cuentas importadas exitosamente. ❌ {failed_count} fallaron.', 'success')
    else:
        flash('No se pudo importar ninguna cuenta. Verifica el formato.', 'danger')
    
    return redirect(url_for('admin'))

@app.route('/import_bulk_emails', methods=['POST'])
@login_required
def import_bulk_emails():
    if not current_user.is_admin:
        return {'error': 'Unauthorized'}, 403
    
    service_name = request.form.get('service_name', '').strip()
    universal_password = request.form.get('universal_password', '').strip()
    bulk_type = request.form.get('bulk_type', 'Other')
    bulk_price = float(request.form.get('bulk_price', 9.99))
    emails_list = request.form.get('emails_list', '').strip()
    
    if not service_name or not universal_password or not emails_list:
        flash('Todos los campos son requeridos para el almacén de correos.', 'danger')
        return redirect(url_for('admin'))
    
    emails = [email.strip() for email in emails_list.split('\n') if email.strip() and '@' in email.strip()]
    
    if not emails:
        flash('No se encontraron correos válidos.', 'danger')
        return redirect(url_for('admin'))
    
    imported_count = 0
    failed_count = 0
    failed_accounts = []
    
    for email in emails:
        try:
            # Verificar si ya existe esta cuenta
            existing = mongo.db.accounts.find_one({'email': email})
            if existing:
                failed_count += 1
                failed_accounts.append({
                    'email': email,
                    'reason': 'Email ya existe en la base de datos'
                })
                continue
                
            import random
            status_options = ['available', 'failed']
            status = random.choice(status_options)
            
            account_data = {
                'email': email,
                'password': universal_password,
                'name': service_name,
                'type': bulk_type,
                'price': bulk_price,
                'quantity': 1,
                'status': status,
                'description': 'Almacén de correos',
                'created_at': datetime.utcnow()
            }
            
            mongo.db.accounts.insert_one(account_data)
            imported_count += 1
        except Exception as e:
            failed_count += 1
            failed_accounts.append({
                'email': email,
                'reason': f'Error de base de datos: {str(e)}'
            })
    
    # Actualizar reporte global
    import_report.update({
        'last_import': datetime.now(),
        'service_name': service_name,
        'total_imported': imported_count,
        'failed_count': failed_count,
        'failed_accounts': failed_accounts
    })
    
    if imported_count > 0:
        if failed_count > 0:
            flash(f'📦 Almacén creado: {imported_count} correos de {service_name} importados. ❌ {failed_count} fallaron. <a href="#" onclick="showImportReport()" class="alert-link">Ver reporte</a>', 'warning')
        else:
            flash(f'📦 Almacén creado: {imported_count} correos de {service_name} importados exitosamente.', 'success')
    else:
        flash('No se pudo crear el almacén. Verifica los datos.', 'danger')
    
    return redirect(url_for('admin'))

@app.route('/edit_account', methods=['POST'])
@login_required
def edit_account():
    if not current_user.is_admin:
        return {'error': 'Unauthorized'}, 403
    
    account_id = request.form.get('account_id')
    
    if not account_id:
        flash('ID de cuenta no proporcionado.', 'danger')
        return redirect(url_for('admin'))
    
    try:
        # Actualizar directamente en MongoDB
        update_data = {
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'name': request.form.get('name'),
            'type': request.form.get('type'),
            'price': float(request.form.get('price', 0)),
            'quantity': int(request.form.get('quantity', 1)),
            'status': request.form.get('status'),
            'description': request.form.get('description', ''),
            'image_url': request.form.get('image_url', '')
        }
        
        result = mongo.db.accounts.update_one(
            {'_id': ObjectId(account_id)}, 
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            flash(f'Cuenta actualizada exitosamente.', 'success')
        else:
            flash('No se realizaron cambios en la cuenta.', 'info')
            
    except Exception as e:
        flash(f'Error al actualizar la cuenta: {str(e)}', 'danger')
    
    return redirect(url_for('admin'))

@app.route('/maintenance/clean_duplicates', methods=['POST'])
@login_required
def clean_duplicates():
    if not current_user.is_admin:
        return {'error': 'Unauthorized'}, 403
    
    # Find and remove duplicate emails
    pipeline = [
        {'$group': {'_id': '$email', 'count': {'$sum': 1}, 'docs': {'$push': '$_id'}}},
        {'$match': {'count': {'$gt': 1}}}
    ]
    
    duplicates = list(mongo.db.accounts.aggregate(pipeline))
    removed_count = 0
    
    for dup in duplicates:
        # Keep first, remove others
        docs_to_remove = dup['docs'][1:]
        for doc_id in docs_to_remove:
            mongo.db.accounts.delete_one({'_id': doc_id})
            removed_count += 1
    
    return {'removed': removed_count}

@app.route('/maintenance/clean_failed', methods=['POST'])
@login_required
def clean_failed():
    if not current_user.is_admin:
        return {'error': 'Unauthorized'}, 403
    
    result = mongo.db.accounts.delete_many({'status': 'failed'})
    return {'removed': result.deleted_count}

@app.route('/api/accounts')
@login_required
@limiter.limit("30 per minute")
def api_accounts():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    accounts = Account.get_all()
    # No exponer datos sensibles en la API
    safe_accounts = []
    for acc in accounts:
        safe_accounts.append({
            'id': acc.id,
            'email': acc.email[:3] + '***@' + acc.email.split('@')[1] if acc.email else 'N/A',  # Parcialmente oculto
            'name': acc.name,
            'type': acc.type,
            'price': acc.price,
            'status': acc.status
        })
    
    return jsonify({'accounts': safe_accounts})

@app.route('/api/import_report')
@login_required
@limiter.limit("10 per minute")
def get_import_report():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Sanitizar datos del reporte antes de enviar
    safe_report = import_report.copy()
    if 'failed_accounts' in safe_report:
        for account in safe_report['failed_accounts']:
            if 'email' in account:
                email = account['email']
                account['email'] = email[:3] + '***@' + email.split('@')[1] if '@' in email else 'N/A'
    
    return jsonify(safe_report)

@app.route('/api/services')
@login_required
@limiter.limit("20 per minute")
def get_services():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        # Obtener servicios únicos de la base de datos
        services = mongo.db.accounts.distinct('name')
        return jsonify({'services': services})
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/analytics')
@login_required
def get_analytics():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    accounts = Account.get_all()
    
    # Analytics data
    analytics = {
        'total_products': len(accounts),
        'available_products': len([a for a in accounts if a.status == 'available']),
        'sold_products': len([a for a in accounts if a.status == 'sold']),
        'revenue': sum(a.price for a in accounts if a.status == 'sold'),
        'inventory_value': sum(a.price for a in accounts if a.status == 'available'),
        'categories': {},
        'price_ranges': {'0-10': 0, '10-20': 0, '20-50': 0, '50+': 0}
    }
    
    # Category breakdown
    for account in accounts:
        if account.status == 'available':
            analytics['categories'][account.type] = analytics['categories'].get(account.type, 0) + 1
            
            # Price range analysis
            if account.price <= 10:
                analytics['price_ranges']['0-10'] += 1
            elif account.price <= 20:
                analytics['price_ranges']['10-20'] += 1
            elif account.price <= 50:
                analytics['price_ranges']['20-50'] += 1
            else:
                analytics['price_ranges']['50+'] += 1
    
    return jsonify(analytics)

@app.route('/api/store-products')
@login_required
def get_store_products():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Agrupar productos por nombre y contar stock
    all_accounts = Account.get_all()
    products_dict = {}
    
    for acc in all_accounts:
        if acc.status == 'available' and acc.name:
            key = f"{acc.name}_{acc.type}_{acc.price}"
            if key not in products_dict:
                products_dict[key] = {
                    'name': acc.name,
                    'type': acc.type,
                    'price': acc.price,
                    'image_url': acc.image_url,
                    'display_order': acc.display_order,
                    'stock': 0
                }
            products_dict[key]['stock'] += 1
    
    # Ordenar productos por display_order
    products = sorted(products_dict.values(), key=lambda x: x['display_order'])
    return jsonify({'products': products})

@app.route('/api/update-product', methods=['POST'])
@login_required
def update_product():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    product_name = data.get('product_name')
    new_price = data.get('price')
    new_image_url = data.get('image_url', '')
    
    if not product_name or new_price is None:
        return jsonify({'success': False, 'message': 'Datos incompletos'})
    
    try:
        # Actualizar todas las cuentas con ese nombre de producto
        result = mongo.db.accounts.update_many(
            {'name': product_name},
            {'$set': {
                'price': float(new_price),
                'image_url': new_image_url
            }}
        )
        
        if result.modified_count > 0:
            return jsonify({'success': True, 'message': f'Producto actualizado ({result.modified_count} cuentas)'})
        else:
            return jsonify({'success': False, 'message': 'No se encontraron cuentas para actualizar'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/update-product-order', methods=['POST'])
@login_required
def update_product_order():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    order = data.get('order', [])
    
    try:
        # Actualizar el orden de los productos en la base de datos
        for item in order:
            product_name = item.get('name')
            new_order = item.get('order')
            
            if product_name is not None and new_order is not None:
                # Actualizar todas las cuentas con ese nombre de producto
                result = mongo.db.accounts.update_many(
                    {'name': product_name},
                    {'$set': {'display_order': int(new_order)}}
                )
                print(f"Updated {result.modified_count} accounts for product {product_name} with order {new_order}")
        
        return jsonify({'success': True, 'message': 'Orden actualizado correctamente'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/update-product-visibility', methods=['POST'])
@login_required
def update_product_visibility():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    product_name = data.get('product_name')
    visible = data.get('visible', True)
    
    try:
        new_status = 'available' if visible else 'hidden'
        result = mongo.db.accounts.update_many(
            {'name': product_name},
            {'$set': {'status': new_status}}
        )
        return jsonify({'success': True, 'message': f'Visibilidad actualizada para {result.modified_count} cuentas'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/delete-product', methods=['POST'])
@login_required
def delete_product():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    product_name = data.get('product_name')
    
    try:
        result = mongo.db.accounts.delete_many({'name': product_name})
        return jsonify({'success': True, 'message': f'Producto eliminado: {result.deleted_count} cuentas'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/bulk-visibility', methods=['POST'])
@login_required
def bulk_visibility():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    action = data.get('action')
    
    try:
        if action == 'show_all':
            result = mongo.db.accounts.update_many(
                {'status': {'$in': ['hidden', 'available']}},
                {'$set': {'status': 'available'}}
            )
        elif action == 'hide_all':
            result = mongo.db.accounts.update_many(
                {'status': 'available'},
                {'$set': {'status': 'hidden'}}
            )
        else:
            return jsonify({'success': False, 'message': 'Acción no válida'})
        
        return jsonify({'success': True, 'message': f'{result.modified_count} productos actualizados'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/store-statistics')
@login_required
def store_statistics():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        all_accounts = list(mongo.db.accounts.find())
        products_dict = {}
        total_accounts = len(all_accounts)
        visible_accounts = 0
        total_value = 0
        
        for acc in all_accounts:
            if acc.get('name'):
                key = f"{acc['name']}_{acc.get('type')}_{acc.get('price', 0)}"
                if key not in products_dict:
                    products_dict[key] = {'stock': 0, 'price': acc.get('price', 0)}
                
                if acc.get('status') == 'available':
                    products_dict[key]['stock'] += 1
                    visible_accounts += 1
                    total_value += acc.get('price', 0)
        
        active_products = len([p for p in products_dict.values() if p['stock'] > 0])
        visibility_percentage = round((visible_accounts / total_accounts * 100) if total_accounts > 0 else 0, 1)
        
        return jsonify({
            'active_products': active_products,
            'total_stock': visible_accounts,
            'store_value': total_value,
            'visibility_percentage': visibility_percentage
        })
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/api/add-product', methods=['POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    name = data.get('name', '').strip()
    price = data.get('price')
    product_type = data.get('type', '').strip()
    quantity = data.get('quantity', 1)
    image_url = data.get('image_url', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if not name or not price or not product_type or not email or not password:
        return jsonify({'success': False, 'message': 'Todos los campos son requeridos'})
    
    try:
        # Crear las cuentas según la cantidad especificada
        created_count = 0
        for i in range(int(quantity)):
            account_email = email if quantity == 1 else f"{email.split('@')[0]}+{i+1}@{email.split('@')[1]}"
            
            account_data = {
                'email': account_email,
                'password': password,
                'name': name,
                'type': product_type,
                'price': float(price),
                'quantity': 1,
                'status': 'available',
                'description': '',
                'image_url': image_url,
                'display_order': 0,
                'created_at': datetime.utcnow()
            }
            
            result = mongo.db.accounts.insert_one(account_data)
            if result.inserted_id:
                created_count += 1
        
        return jsonify({
            'success': True, 
            'message': f'Producto creado: {created_count} cuentas de {name}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/bulk-delete-products', methods=['POST'])
@login_required
def bulk_delete_products():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        result = mongo.db.accounts.delete_many({})
        return jsonify({
            'success': True, 
            'deleted_count': result.deleted_count,
            'message': f'Eliminados {result.deleted_count} productos completamente'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/banners')
@login_required
def get_banners():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    banners = Banner.get_all()
    banners_data = [{
        'id': b.id,
        'title': b.title,
        'subtitle': b.subtitle,
        'image_url': b.image_url,
        'background_color': b.background_color,
        'text_color': b.text_color,
        'button_text': b.button_text,
        'button_link': b.button_link,
        'is_active': b.is_active,
        'display_order': b.display_order,
        'banner_type': b.banner_type
    } for b in banners]
    
    return jsonify({'banners': banners_data})

@app.route('/api/add-banner', methods=['POST'])
@login_required
def add_banner():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    try:
        banner_data = {
            'title': data.get('title', ''),
            'subtitle': data.get('subtitle', ''),
            'image_url': data.get('image_url', ''),
            'background_color': data.get('background_color', '#667eea'),
            'text_color': data.get('text_color', '#ffffff'),
            'button_text': data.get('button_text', ''),
            'button_link': data.get('button_link', ''),
            'is_active': data.get('is_active', True),
            'display_order': data.get('display_order', 0),
            'banner_type': data.get('banner_type', 'promotion'),
            'is_fullscreen': data.get('is_fullscreen', False),
            'auto_show': data.get('auto_show', False),
            'show_delay': data.get('show_delay', 3000),
            'created_at': datetime.utcnow()
        }
        
        banner = Banner(banner_data)
        banner.save()
        
        return jsonify({'success': True, 'message': 'Banner creado exitosamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/create-discount-event', methods=['POST'])
@login_required
def create_discount_event():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        event_type = data.get('event_type', 'flash')
        
        # Crear banner automático para el descuento
        banner_data = {
            'title': f'¡{data.get("name", "Oferta Especial")}!',
            'subtitle': f'{data.get("percentage", 20)}% de descuento',
            'background_color': '#ff6b6b',
            'text_color': '#ffffff',
            'button_text': 'Ver Ofertas',
            'button_link': '#productos',
            'is_active': True,
            'is_fullscreen': True,
            'auto_show': True,
            'show_delay': 2000,
            'banner_type': 'discount',
            'created_at': datetime.utcnow()
        }
        
        banner = Banner(banner_data)
        banner.save()
        
        # Crear descuento
        discount_data = {
            'name': data.get('name', 'Oferta Flash'),
            'percentage': float(data.get('percentage', 20)),
            'event_type': event_type,
            'is_active': True,
            'categories': data.get('categories', []),
            'banner_id': banner.id,
            'created_at': datetime.utcnow()
        }
        
        if event_type != 'flash':
            discount_data['start_date'] = datetime.fromisoformat(data.get('start_date')) if data.get('start_date') else datetime.utcnow()
            discount_data['end_date'] = datetime.fromisoformat(data.get('end_date')) if data.get('end_date') else datetime.utcnow() + timedelta(days=1)
        
        discount = Discount(discount_data)
        discount.save()
        
        return jsonify({'success': True, 'message': 'Evento de descuento creado correctamente', 'banner_id': banner.id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/check-discount')
def check_discount():
    active_discount = Discount.get_active_discount()
    if active_discount:
        return jsonify({
            'has_discount': True,
            'percentage': active_discount.percentage,
            'name': active_discount.name,
            'banner_id': active_discount.banner_id
        })
    return jsonify({'has_discount': False})

@app.route('/api/deactivate-discount', methods=['POST'])
@login_required
def deactivate_discount():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Desactivar todos los descuentos activos
        mongo.db.discounts.update_many(
            {'is_active': True},
            {'$set': {'is_active': False}}
        )
        
        # Desactivar banners de descuento
        mongo.db.banners.update_many(
            {'banner_type': 'discount', 'is_active': True},
            {'$set': {'is_active': False}}
        )
        
        return jsonify({'success': True, 'message': 'Descuentos desactivados'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/update-banner', methods=['POST'])
@login_required
def update_banner():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    banner_id = data.get('banner_id')
    
    try:
        result = mongo.db.banners.update_one(
            {'_id': ObjectId(banner_id)},
            {'$set': {
                'title': data.get('title', ''),
                'subtitle': data.get('subtitle', ''),
                'image_url': data.get('image_url', ''),
                'background_color': data.get('background_color', '#667eea'),
                'text_color': data.get('text_color', '#ffffff'),
                'button_text': data.get('button_text', ''),
                'button_link': data.get('button_link', ''),
                'is_active': data.get('is_active', True),
                'display_order': data.get('display_order', 0),
                'banner_type': data.get('banner_type', 'promotion')
            }}
        )
        
        return jsonify({'success': True, 'message': 'Banner actualizado'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/delete-banner', methods=['POST'])
@login_required
def delete_banner():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    banner_id = data.get('banner_id')
    
    try:
        result = mongo.db.banners.delete_one({'_id': ObjectId(banner_id)})
        return jsonify({'success': True, 'message': 'Banner eliminado'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/comments', methods=['GET', 'POST'])
def handle_comments():
    if request.method == 'GET':
        comments = Comment.get_approved()
        comments_data = [{
            'name': c.name,
            'rating': c.rating,
            'text': c.text,
            'date': c.created_at.strftime('%d de %B, %Y')
        } for c in comments]
        return jsonify({'comments': comments_data})
    
    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name', '').strip()
        rating = int(data.get('rating', 5))
        text = data.get('text', '').strip()
        
        if not name or not text or rating < 1 or rating > 5:
            return jsonify({'success': False, 'message': 'Datos inválidos'})
        
        comment_data = {
            'name': name,
            'rating': rating,
            'text': text,
            'is_approved': True,
            'created_at': datetime.utcnow()
        }
        
        comment = Comment(comment_data)
        comment.save()
        
        return jsonify({'success': True, 'message': 'Comentario guardado'})

@app.route('/api/suggestions', methods=['POST'])
def add_suggestion():
    from pytz import timezone
    
    data = request.get_json()
    customer_name = data.get('customer_name', '').strip()
    customer_email = data.get('customer_email', '').strip()
    service_name = data.get('service_name', '').strip()
    phone = data.get('phone', '').strip()
    
    if not service_name or not customer_name or not customer_email:
        return jsonify({'success': False, 'message': 'Nombre, email y servicio son requeridos'})
    
    # Convertir a zona horaria de Ecuador
    ecuador_tz = timezone('America/Guayaquil')
    ecuador_time = datetime.now(ecuador_tz)
    
    suggestion_data = {
        'customer_name': customer_name,
        'customer_email': customer_email,
        'service_name': service_name,
        'phone': phone,
        'is_read': False,
        'created_at': ecuador_time
    }
    
    suggestion = Suggestion(suggestion_data)
    suggestion.save()
    
    return jsonify({'success': True, 'message': 'Sugerencia enviada'})

@app.route('/api/admin/suggestions')
@login_required
def get_suggestions():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    suggestions = Suggestion.get_all()
    suggestions_data = [{
        'id': s.id,
        'customer_name': s.customer_name,
        'customer_email': s.customer_email,
        'service_name': s.service_name,
        'phone': s.phone,
        'is_read': s.is_read,
        'date': s.created_at.strftime('%d/%m/%Y %H:%M') if hasattr(s.created_at, 'strftime') else 'Fecha no disponible'
    } for s in suggestions]
    
    return jsonify({'suggestions': suggestions_data})

if __name__ == '__main__':
    print("🚀 SISTEMA DE VENTAS - VERSIÓN SIMPLIFICADA")
    print("📍 URL: http://localhost:5000")
    print("👤 Admin: admin@sistema.com / Admin123!")
    
    app.run(host='0.0.0.0', port=5000, debug=True)