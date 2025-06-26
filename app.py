from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import datetime

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

products = []
orders = []
next_id = 1
next_order_id = 1

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/api/products')
def get_products():
    return jsonify(products)

@app.route('/api/orders/<user_id>')
def get_user_orders(user_id):
    return jsonify([o for o in orders if o['user_id'] == user_id and o['status'] == 'aprovado'])

@app.route('/api/orders', methods=['POST'])
def make_order():
    global next_order_id
    data = request.json
    senha = data.get('senha')
    user_id = data.get('user_id')
    product_id = data.get('product_id')

    if senha not in ['venusmn137', 'admvenus1377']:
        return jsonify({'error': 'Não autorizado'}), 403

    for p in products:
        if p['id'] == product_id:
            if p['stock'] <= 0:
                return jsonify({'error': 'Produto sem estoque'}), 400
            order = {
                'order_id': next_order_id,
                'user_id': user_id,
                'product_id': p['id'],
                'product_name': p['name'],
                'product_price': p['price'],
                'product_stock': p['stock'],
                'date': datetime.datetime.now().isoformat(),
                'status': 'pendente'
            }
            orders.append(order)
            next_order_id += 1
            return jsonify({'success': True})
    return jsonify({'error': 'Produto não encontrado'}), 404

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    senha = data.get('senha')
    if senha == 'admvenus1377':
        return jsonify({'role': 'admin'})
    elif senha == 'venusmn137':
        return jsonify({'role': 'user'})
    else:
        return jsonify({'error': 'Senha incorreta'}), 403

@app.route('/api/admin/products', methods=['POST'])
def add_product():
    global next_id
    if request.headers.get('X-Admin-Token') != 'admvenus1377':
        return jsonify({'error': 'Não autorizado'}), 403
    data = request.json
    data['id'] = next_id
    next_id += 1
    products.append(data)
    return jsonify({'success': True})

@app.route('/api/admin/products/<int:pid>', methods=['PUT'])
def update_product(pid):
    if request.headers.get('X-Admin-Token') != 'admvenus1377':
        return jsonify({'error': 'Não autorizado'}), 403
    data = request.json
    for p in products:
        if p['id'] == pid:
            p.update(data)
            return jsonify({'success': True})
    return jsonify({'error': 'Produto não encontrado'}), 404

@app.route('/api/admin/products/<int:pid>', methods=['DELETE'])
def delete_product(pid):
    if request.headers.get('X-Admin-Token') != 'admvenus1377':
        return jsonify({'error': 'Não autorizado'}), 403
    global products
    products = [p for p in products if p['id'] != pid]
    return jsonify({'success': True})

@app.route('/api/admin/orders', methods=['GET'])
def list_orders():
    if request.headers.get('X-Admin-Token') != 'admvenus1377':
        return jsonify({'error': 'Não autorizado'}), 403
    return jsonify([o for o in orders if o['status'] == 'pendente'])

@app.route('/api/admin/orders/<int:oid>', methods=['PUT'])
def update_order(oid):
    if request.headers.get('X-Admin-Token') != 'admvenus1377':
        return jsonify({'error': 'Não autorizado'}), 403
    data = request.json
    for o in orders:
        if o['order_id'] == oid:
            o['status'] = data['status']
            if data['status'] == 'aprovado':
                for p in products:
                    if p['id'] == o['product_id']:
                        p['stock'] -= 1
            return jsonify({'success': True})
    return jsonify({'error': 'Pedido não encontrado'}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
