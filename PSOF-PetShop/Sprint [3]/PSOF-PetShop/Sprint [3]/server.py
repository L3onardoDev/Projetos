#!/usr/bin/env python3
import hashlib
import json
import secrets
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / 'petlife.db'
HOST = '0.0.0.0'
PORT = 4173
SESSIONS = {}

PRODUCTS = [
    ('Ração para Cães Adultos - 1kg', 29.99),
    ('Coleira - Rosa Filhote', 29.99),
    ('Shampoo - Gatos Neutro', 29.99),
    ('Biscoito de Banana e Aveia Gatos - Cães', 29.99),
    ('Kaldog Bifinho Churrasco Gatos - Cães', 29.99),
    ('Shampoo para Filhote Todos - 200g', 29.99),
    ('Kit de higiene bucal Todos', 29.99),
    ('Tapete higiênico Todos', 29.99),
    ('Coleira Ajustável Cães Adultos', 29.99),
    ('Laço para Pet Filhote', 29.99),
    ('Brinquedo Mordedor Filhote', 29.99),
]


def db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    return connection


def init_db():
    with db() as connection:
        connection.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                species TEXT NOT NULL,
                breed TEXT,
                age INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 10
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                zip TEXT NOT NULL,
                city TEXT NOT NULL,
                payment TEXT NOT NULL,
                total REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL
            );
        ''')
        for name, price in PRODUCTS:
            connection.execute('INSERT OR IGNORE INTO products (name, price) VALUES (?, ?)', (name, price))


def password_hash(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def json_response(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', str(len(body)))
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(fmt % args)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()

    def read_json(self):
        length = int(self.headers.get('Content-Length', '0'))
        return json.loads(self.rfile.read(length) or '{}')

    def user(self):
        token = self.headers.get('Authorization', '').replace('Bearer ', '')
        return SESSIONS.get(token)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/health':
            return json_response(self, 200, {'ok': True, 'database': str(DB_PATH.name)})
        if path == '/api/products':
            with db() as connection:
                rows = connection.execute('SELECT id, name, price, stock FROM products ORDER BY id').fetchall()
            return json_response(self, 200, {'products': [dict(row) for row in rows]})
        file_path = ROOT / ('Pagina_Inicial.html' if path == '/' else path.lstrip('/'))
        if file_path.is_file() and ROOT in file_path.resolve().parents:
            content_type = 'text/html; charset=utf-8' if file_path.suffix == '.html' else 'text/plain; charset=utf-8'
            if file_path.suffix == '.css': content_type = 'text/css; charset=utf-8'
            if file_path.suffix == '.js': content_type = 'application/javascript; charset=utf-8'
            if file_path.suffix in ('.png', '.jpg', '.jpeg', '.ico'): content_type = 'image/' + ('jpeg' if file_path.suffix in ('.jpg', '.jpeg') else file_path.suffix[1:])
            content = file_path.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        json_response(self, 404, {'error': 'Página não encontrada'})

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            data = self.read_json()
            if path == '/api/register':
                required = ['ownerName', 'email', 'password', 'petName', 'species', 'age']
                if any(not data.get(field) for field in required):
                    return json_response(self, 400, {'error': 'Preencha todos os campos obrigatórios.'})
                with db() as connection:
                    cursor = connection.execute('INSERT INTO users (owner_name, email, password_hash) VALUES (?, ?, ?)', (data['ownerName'], data['email'].lower().strip(), password_hash(data['password'])))
                    user_id = cursor.lastrowid
                    connection.execute('INSERT INTO pets (user_id, name, species, breed, age) VALUES (?, ?, ?, ?, ?)', (user_id, data['petName'], data['species'], data.get('breed', ''), int(data['age'])))
                return json_response(self, 201, {'ok': True, 'message': 'Cadastro criado. Faça login para continuar.'})

            if path == '/api/login':
                email = data.get('email', '').lower().strip()
                with db() as connection:
                    row = connection.execute('SELECT id, owner_name, email, password_hash FROM users WHERE email = ?', (email,)).fetchone()
                if not row or row['password_hash'] != password_hash(data.get('password', '')):
                    return json_response(self, 401, {'error': 'E-mail ou senha inválidos.'})
                token = secrets.token_urlsafe(24)
                SESSIONS[token] = {'id': row['id'], 'ownerName': row['owner_name'], 'email': row['email']}
                return json_response(self, 200, {'ok': True, 'token': token, 'user': SESSIONS[token]})

            if path == '/api/orders':
                current_user = self.user()
                if not current_user:
                    return json_response(self, 401, {'error': 'Faça login antes de finalizar o pedido.'})
                items = data.get('items') or []
                if not items:
                    return json_response(self, 400, {'error': 'O carrinho está vazio.'})
                total = sum(float(item.get('price', 0)) * int(item.get('quantity', 0)) for item in items)
                with db() as connection:
                    cursor = connection.execute('INSERT INTO orders (user_id, name, address, zip, city, payment, total) VALUES (?, ?, ?, ?, ?, ?, ?)', (current_user['id'], data.get('name', ''), data.get('address', ''), data.get('zip', ''), data.get('city', ''), data.get('payment', ''), total))
                    order_id = cursor.lastrowid
                    for item in items:
                        connection.execute('INSERT INTO order_items (order_id, product_name, quantity, unit_price) VALUES (?, ?, ?, ?)', (order_id, item['name'], int(item['quantity']), float(item['price'])))
                return json_response(self, 201, {'ok': True, 'order': f'PL-{order_id:06d}', 'total': total})
            return json_response(self, 404, {'error': 'Endpoint não encontrado'})
        except sqlite3.IntegrityError:
            return json_response(self, 409, {'error': 'Este e-mail já está cadastrado.'})
        except (ValueError, KeyError, json.JSONDecodeError) as error:
            return json_response(self, 400, {'error': f'Dados inválidos: {error}'})
        except Exception as error:
            return json_response(self, 500, {'error': f'Erro interno: {error}'})


if __name__ == '__main__':
    init_db()
    print(f'PetLife server running at http://localhost:{PORT}')
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
