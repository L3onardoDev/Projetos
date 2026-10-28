#!/usr/bin/env python3
"""Backend SQLite do site PetLife."""
import hashlib
import json
import mimetypes
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / 'petlife.db'
HOST = '0.0.0.0'
PORT = 4173
SESSION_DAYS = 7
PASSWORD_ITERATIONS = 310_000
PRODUCTS = [
    ('Ração para Cães Adultos - 1kg', 29.99), ('Coleira - Rosa Filhote', 29.99),
    ('Shampoo - Gatos Neutro', 29.99), ('Biscoito de Banana e Aveia Gatos - Cães', 29.99),
    ('Kaldog Bifinho Churrasco Gatos - Cães', 29.99), ('Shampoo para Filhote Todos - 200g', 29.99),
    ('Kit de higiene bucal Todos', 29.99), ('Tapete higiênico Todos', 29.99),
    ('Coleira Ajustável Cães Adultos', 29.99), ('Laço para Pet Filhote', 29.99),
    ('Brinquedo Mordedor Filhote', 29.99),
]


def db():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    connection.execute('PRAGMA busy_timeout = 10000')
    return connection


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def init_db():
    with db() as connection:
        connection.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT, owner_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL, species TEXT NOT NULL, breed TEXT,
                age INTEGER NOT NULL CHECK(age BETWEEN 0 AND 50)
            );
            CREATE INDEX IF NOT EXISTS idx_pets_user_id ON pets(user_id);
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE,
                price REAL NOT NULL CHECK(price >= 0), stock INTEGER NOT NULL DEFAULT 10 CHECK(stock >= 0)
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id),
                name TEXT NOT NULL, address TEXT NOT NULL, zip TEXT NOT NULL, city TEXT NOT NULL,
                payment TEXT NOT NULL, total REAL NOT NULL CHECK(total >= 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                product_name TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity > 0),
                unit_price REAL NOT NULL CHECK(unit_price >= 0)
            );
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT, protocol TEXT NOT NULL UNIQUE,
                tutor TEXT NOT NULL, pet TEXT NOT NULL, date TEXT NOT NULL, time TEXT NOT NULL,
                service TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
        ''')
        # Remove os registros órfãos presentes no arquivo original recebido.
        connection.execute('DELETE FROM pets WHERE user_id NOT IN (SELECT id FROM users)')
        for name, price in PRODUCTS:
            connection.execute('INSERT OR IGNORE INTO products (name, price) VALUES (?, ?)', (name, price))
        connection.execute('DELETE FROM sessions WHERE expires_at <= ?', (utc_now(),))


def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PASSWORD_ITERATIONS)
    return f'pbkdf2_sha256${PASSWORD_ITERATIONS}${salt.hex()}${digest.hex()}'


def verify_password(stored, password):
    if stored.startswith('pbkdf2_sha256$'):
        try:
            _, iterations, salt_hex, digest_hex = stored.split('$', 3)
            digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt_hex), int(iterations)).hex()
            return secrets.compare_digest(digest, digest_hex), False
        except (ValueError, TypeError):
            return False, False
    legacy = hashlib.sha256(password.encode('utf-8')).hexdigest()
    valid = secrets.compare_digest(stored, legacy)
    return valid, valid


def json_response(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', str(len(body)))
    handler.send_header('Cache-Control', 'no-store')
    handler.end_headers()
    handler.wfile.write(body)


def clean_text(value, max_length=500):
    return value.strip()[:max_length] if isinstance(value, str) else ''


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(fmt % args)

    def read_json(self):
        length = int(self.headers.get('Content-Length', '0'))
        if length <= 0 or length > 1_000_000:
            raise ValueError('Tamanho da solicitação inválido.')
        value = json.loads(self.rfile.read(length))
        if not isinstance(value, dict):
            raise ValueError('Envie um objeto JSON válido.')
        return value

    def current_user(self, connection):
        scheme, _, token = self.headers.get('Authorization', '').partition(' ')
        if scheme.lower() != 'bearer' or not token:
            return None
        token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
        return connection.execute('''SELECT u.id, u.owner_name, u.email FROM sessions s
            JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires_at>?''',
            (token_hash, utc_now())).fetchone()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Allow', 'GET, POST, OPTIONS')
        self.end_headers()

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path == '/api/health':
            try:
                with db() as connection:
                    connection.execute('SELECT 1')
                return json_response(self, 200, {'ok': True, 'database': DB_PATH.name})
            except sqlite3.Error:
                return json_response(self, 503, {'ok': False, 'error': 'Banco de dados indisponível.'})
        if path == '/api/products':
            with db() as connection:
                rows = connection.execute('SELECT id, name, price, stock FROM products ORDER BY id').fetchall()
            return json_response(self, 200, {'products': [dict(row) for row in rows]})
        relative = 'index.html' if path == '/' else path.lstrip('/')
        file_path = (ROOT / relative).resolve()
        if ROOT.resolve() not in file_path.parents or not file_path.is_file():
            return json_response(self, 404, {'error': 'Página não encontrada.'})
        content_type = mimetypes.guess_type(file_path.name)[0] or 'application/octet-stream'
        if content_type.startswith('text/') or content_type in ('application/javascript', 'application/json'):
            content_type += '; charset=utf-8'
        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        path = unquote(urlparse(self.path).path)
        try:
            data = self.read_json()
            if path == '/api/register':
                owner = clean_text(data.get('ownerName'), 120)
                email = clean_text(data.get('email'), 254).lower()
                password = data.get('password', '')
                pet_name = clean_text(data.get('petName'), 100)
                species = clean_text(data.get('species'), 40)
                breed = clean_text(data.get('breed'), 100)
                if not all((owner, email, pet_name, species)) or not isinstance(password, str) or not 4 <= len(password) <= 256:
                    return json_response(self, 400, {'error': 'Confira os campos obrigatórios e a senha (mínimo de 4 caracteres).'})
                if '@' not in email:
                    return json_response(self, 400, {'error': 'Informe um e-mail válido.'})
                try:
                    age = int(data.get('age'))
                except (ValueError, TypeError):
                    return json_response(self, 400, {'error': 'Informe a idade do pet.'})
                if not 0 <= age <= 50:
                    return json_response(self, 400, {'error': 'A idade deve estar entre 0 e 50 anos.'})
                with db() as connection:
                    cursor = connection.execute('INSERT INTO users (owner_name, email, password_hash) VALUES (?, ?, ?)', (owner, email, hash_password(password)))
                    connection.execute('INSERT INTO pets (user_id, name, species, breed, age) VALUES (?, ?, ?, ?, ?)', (cursor.lastrowid, pet_name, species, breed, age))
                return json_response(self, 201, {'ok': True, 'message': 'Cadastro criado. Faça login para continuar.'})

            if path == '/api/login':
                email = clean_text(data.get('email'), 254).lower()
                password = data.get('password', '')
                if not email or not isinstance(password, str):
                    return json_response(self, 401, {'error': 'E-mail ou senha inválidos.'})
                with db() as connection:
                    row = connection.execute('SELECT id, owner_name, email, password_hash FROM users WHERE email=?', (email,)).fetchone()
                    if not row:
                        return json_response(self, 401, {'error': 'E-mail ou senha inválidos.'})
                    valid, upgrade = verify_password(row['password_hash'], password)
                    if not valid:
                        return json_response(self, 401, {'error': 'E-mail ou senha inválidos.'})
                    if upgrade:
                        connection.execute('UPDATE users SET password_hash=? WHERE id=?', (hash_password(password), row['id']))
                    token = secrets.token_urlsafe(32)
                    expires = (datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)).isoformat(timespec='seconds')
                    connection.execute('INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)', (hashlib.sha256(token.encode()).hexdigest(), row['id'], expires))
                user = {'id': row['id'], 'ownerName': row['owner_name'], 'email': row['email']}
                return json_response(self, 200, {'ok': True, 'token': token, 'user': user})

            if path == '/api/orders':
                with db() as connection:
                    user = self.current_user(connection)
                    if not user:
                        return json_response(self, 401, {'error': 'Faça login antes de finalizar o pedido.'})
                    items = data.get('items')
                    if not isinstance(items, list) or not items or len(items) > 100:
                        return json_response(self, 400, {'error': 'O carrinho está vazio ou inválido.'})
                    fields = {key: clean_text(data.get(key), limit) for key, limit in (('name', 120), ('address', 250), ('zip', 20), ('city', 100), ('payment', 40))}
                    if not all(fields.values()):
                        return json_response(self, 400, {'error': 'Preencha todos os dados de entrega e pagamento.'})
                    priced, total_cents = [], 0
                    for item in items:
                        if not isinstance(item, dict):
                            return json_response(self, 400, {'error': 'Item do carrinho inválido.'})
                        name = clean_text(item.get('name'), 200)
                        try:
                            quantity = int(item.get('quantity'))
                        except (ValueError, TypeError):
                            quantity = 0
                        product = connection.execute('SELECT name, price FROM products WHERE name=?', (name,)).fetchone()
                        if not product or not 1 <= quantity <= 99:
                            return json_response(self, 400, {'error': 'Produto ou quantidade inválidos.'})
                        cents = round(float(product['price']) * 100)
                        total_cents += cents * quantity
                        priced.append((product['name'], quantity, cents / 100))
                    total = total_cents / 100
                    cursor = connection.execute('''INSERT INTO orders (user_id,name,address,zip,city,payment,total)
                        VALUES (?,?,?,?,?,?,?)''', (user['id'], fields['name'], fields['address'], fields['zip'], fields['city'], fields['payment'], total))
                    order_id = cursor.lastrowid
                    connection.executemany('INSERT INTO order_items (order_id,product_name,quantity,unit_price) VALUES (?,?,?,?)', [(order_id, name, qty, price) for name, qty, price in priced])
                return json_response(self, 201, {'ok': True, 'order': f'PL-{order_id:06d}', 'total': total})

            if path == '/api/bookings':
                fields = {key: clean_text(data.get(key), limit) for key, limit in (('tutor', 120), ('pet', 100), ('date', 10), ('time', 10), ('service', 80), ('notes', 1000))}
                if not all(fields[key] for key in ('tutor', 'pet', 'date', 'time', 'service')):
                    return json_response(self, 400, {'error': 'Preencha os campos obrigatórios do agendamento.'})
                try:
                    appointment_date = datetime.strptime(fields['date'], '%Y-%m-%d').date()
                except ValueError:
                    return json_response(self, 400, {'error': 'Informe uma data válida.'})
                if appointment_date < datetime.now().date() or fields['time'] not in {'09:00', '11:00', '14:00', '16:00'} or fields['service'] not in {'Banho e tosa', 'Somente banho', 'Somente tosa'}:
                    return json_response(self, 400, {'error': 'Data, horário ou tipo de atendimento inválido.'})
                protocol = f'AT-{secrets.token_hex(4).upper()}'
                with db() as connection:
                    connection.execute('INSERT INTO bookings (protocol,tutor,pet,date,time,service,notes) VALUES (?,?,?,?,?,?,?)', (protocol, fields['tutor'], fields['pet'], fields['date'], fields['time'], fields['service'], fields['notes']))
                return json_response(self, 201, {'ok': True, 'protocol': protocol, 'message': f"Solicitação recebida! Protocolo {protocol}. Nossa equipe confirmará o horário para {fields['pet']}."})

            return json_response(self, 404, {'error': 'Endpoint não encontrado.'})
        except sqlite3.IntegrityError as error:
            if 'users.email' in str(error) or 'UNIQUE constraint failed: users.email' in str(error):
                return json_response(self, 409, {'error': 'Este e-mail já está cadastrado.'})
            return json_response(self, 400, {'error': 'Os dados enviados não puderam ser salvos.'})
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            return json_response(self, 400, {'error': 'Envie dados válidos para esta operação.'})
        except sqlite3.Error:
            return json_response(self, 500, {'error': 'Erro ao acessar o banco de dados.'})
        except Exception:
            return json_response(self, 500, {'error': 'Erro interno no servidor.'})


if __name__ == '__main__':
    init_db()
    print(f'PetLife server running at http://localhost:{PORT}')
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
