import json
import time
import requests
from flask import Flask, request, jsonify
from uuid import uuid4


# 🔹 256-биттік хеш-функция (кітапханасыз)
def custom_hash(data):
    hash_value = 0
    for char in str(data):
        hash_value = (hash_value * 31 + ord(char)) % (2**256)
    return format(hash_value, '064x')


# 🔹 Блокчейн класы (негізгі логика)
class Blockchain:
    def __init__(self):
        self.chain = []  # Блоктар тізімі
        self.transactions = []  # Күтілетін транзакциялар
        self.nodes = set()  # Желі түйіндері (nodes)
        self.create_block(proof=1, previous_hash='0')  # Генезис блогын құру

    # 🔸 Желі түйіндерін тіркеу (басқа нодтарды қосу)
    def register_node(self, address):
        self.nodes.add(address)

    # 🔸 Жаңа блок жасау
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.transactions,
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.transactions = []  # Транзакция тізімін тазарту
        self.chain.append(block)  # Блокты блокчейнге қосу

        # 🔹 Желіге жаңа блокты тарату
        self.broadcast_block(block)
        return block

    # 🔸 Жаңа транзакция қосу
    def add_transaction(self, sender, recipient, amount):
        transaction = {'sender': sender, 'recipient': recipient, 'amount': amount}
        self.transactions.append(transaction)

        # 🔹 Барлық түйіндерге жаңа транзакцияны тарату
        self.broadcast_transaction(transaction)
        return self.last_block['index'] + 1

    # 🔸 Блок хешін есептеу
    @staticmethod
    def hash(block):
        return custom_hash(json.dumps(block, sort_keys=True))

    # 🔸 Соңғы блокты алу
    @property
    def last_block(self):
        return self.chain[-1]

    # 🔸 Proof-of-Work алгоритмі (майнинг)
    def proof_of_work(self, last_proof):
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    # 🔸 Proof-of-Work дұрыстығын тексеру (маңызды ереже: 4 "0" болуы керек)
    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'
        return custom_hash(guess)[:4] == '0000'

    # 🔸 Блокчейннің дұрыстығын тексеру
    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            last_block = block
            current_index += 1

        return True

    # 🔸 Консенсус алгоритмі (ең ұзын тізбекті таңдау)
    def resolve_conflicts(self):
        new_chain = None
        max_length = len(self.chain)

        for node in self.nodes:
            try:
                response = requests.get(f'http://{node}/chain')
                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']

                    if length > max_length and self.valid_chain(chain):
                        max_length = length
                        new_chain = chain
            except requests.exceptions.RequestException:
                continue

        if new_chain:
            self.chain = new_chain
            return True

        return False

    # 🔸 Баланс есептеу (мекенжай бойынша)
    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['recipient'] == address:
                    balance += transaction['amount']
                if transaction['sender'] == address:
                    balance -= transaction['amount']
        return balance

    # 🔸 Жаңа транзакцияны барлық түйіндерге жіберу
    def broadcast_transaction(self, transaction):
        for node in self.nodes:
            try:
                requests.post(f'http://{node}/transactions/new', json=transaction)
            except requests.exceptions.RequestException:
                continue

    # 🔸 Жаңа блокты барлық түйіндерге жіберу
    def broadcast_block(self, block):
        for node in self.nodes:
            try:
                requests.post(f'http://{node}/blocks/new', json=block)
            except requests.exceptions.RequestException:
                continue


# 🔹 Flask API сервері (негізгі интерфейс)
app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')  # Бірегей түйін идентификаторы
blockchain = Blockchain()


# 🔸 Майнинг жасау (жаңа блок құру)
@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block['proof'])
    blockchain.add_transaction(sender='0', recipient=node_identifier, amount=1)
    block = blockchain.create_block(proof, blockchain.hash(last_block))
    return jsonify(block), 200


# 🔸 Жаңа транзакция қосу
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    data = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing values'}), 400

    index = blockchain.add_transaction(data['sender'], data['recipient'], data['amount'])
    return jsonify({'message': f'Transaction will be added to Block {index}'}), 201


# 🔸 Жаңа блокты қабылдау (басқа нодтардан)
@app.route('/blocks/new', methods=['POST'])
def new_block():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid block data'}), 400

    blockchain.chain.append(data)
    return jsonify({'message': 'Block added'}), 201


# 🔸 Блокчейнді көру (толық тізбек)
@app.route('/chain', methods=['GET'])
def full_chain():
    return jsonify({'chain': blockchain.chain, 'length': len(blockchain.chain)}), 200


# 🔸 Желіге түйін қосу
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    data = request.get_json()
    nodes = data.get('nodes', [])
    for node in nodes:
        blockchain.register_node(node)
    return jsonify({'message': 'New nodes added', 'nodes': list(blockchain.nodes)}), 201


# 🔸 Консенсус алгоритмін орындау (синхронизация)
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    return jsonify({'message': 'Chain replaced' if replaced else 'Chain is authoritative'}), 200


# 🔸 Белгілі бір мекенжайдың балансын көру
@app.route('/balance/<string:address>', methods=['GET'])
def get_balance(address):
    return jsonify({'address': address, 'balance': blockchain.get_balance(address)}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
