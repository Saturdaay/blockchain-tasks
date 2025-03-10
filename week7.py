import hashlib
import json
import time
import random
import tkinter as tk
import rsa
from collections import defaultdict

# ========================
# НАСТРОЙКИ
# ========================
INITIAL_BALANCE = 100
REWARD_AMOUNT_POW = 10  # Награда за PoW
REWARD_AMOUNT_POS = 5  # Награда за PoS

# ========================
# ХЕШ-ФУНКЦИЯ & RSA
# ========================
def hash_data(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()

class Wallet:
    def __init__(self):
        self.public_key, self.private_key = rsa.newkeys(512)

    def get_address(self):
        return self.public_key.save_pkcs1().decode('utf-8')

# ========================
# КЛАСС БЛОКЧЕЙНА
# ========================
class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.balances = defaultdict(lambda: INITIAL_BALANCE)
        self.validators = {}
        self.miners = defaultdict(int)  # ✅ Баланс для PoW-майнеров
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = self.create_block([], "0", "System")
        self.chain.append(genesis_block)

    def create_block(self, transactions, previous_hash, validator):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "transactions": transactions,
            "previous_hash": previous_hash,
            "hash": hash_data(transactions),
            "validator": validator
        }
        self.chain.append(block)
        return block

    def add_transaction(self, sender, receiver, amount, fee):
        if self.balances[sender] < amount + fee:
            print("⚠ Недостаточно средств!")
            return None
        transaction = {
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "fee": fee,
        }
        self.pending_transactions.append(transaction)
        print("✅ Транзакция добавлена:", transaction)
        return transaction

    def mine_block_pow(self, miner):
        if not self.pending_transactions:
            print("⚠ Нет транзакций для майнинга!")
            return None
        block = self.create_block(self.pending_transactions, self.chain[-1]["hash"], miner)
        
        for tx in self.pending_transactions:
            self.balances[tx["sender"]] -= (tx["amount"] + tx["fee"])
            self.balances[tx["receiver"]] += tx["amount"]
            self.balances[miner] += tx["fee"]
        
        self.miners[miner] += REWARD_AMOUNT_POW  # ✅ Минер получает награду за PoW
        print(f"✅ Майнер {miner[:6]} получил награду {REWARD_AMOUNT_POW}!")
        
        self.pending_transactions = []
        print("⛏ Блок добыт (PoW):", block)
        return block

    def mine_block_pos(self):
        if not self.validators:
            print("⚠ Нет валидаторов!")
            return None
        total_stake = sum(self.validators.values())
        chosen_validator = random.choices(list(self.validators.keys()), weights=self.validators.values())[0]
        block = self.create_block(self.pending_transactions, self.chain[-1]["hash"], chosen_validator)

        for tx in self.pending_transactions:
            self.balances[tx["sender"]] -= (tx["amount"] + tx["fee"])
            self.balances[tx["receiver"]] += tx["amount"]

        self.balances[chosen_validator] += REWARD_AMOUNT_POS  # ✅ Валидатор получает награду за PoS
        print(f"✅ Валидатор {chosen_validator[:6]} получил награду {REWARD_AMOUNT_POS}!")

        self.pending_transactions = []
        print(f"⛏ Блок добыт валидатором {chosen_validator} (PoS)!")
        return block

    def register_validator(self, address, stake):
        if self.balances[address] < stake:
            print("⚠ Недостаточно средств для стейкинга!")
            return False
        self.balances[address] -= stake
        self.validators[address] = self.validators.get(address, 0) + stake
        print(f"✅ {address} теперь валидатор с {stake} монет!")
        return True

# ========================
# ФУНКЦИИ ДЛЯ TKINTER
# ========================
def send_transaction():
    sender = entry_sender.get()
    receiver = entry_receiver.get()
    amount = float(entry_amount.get())
    fee = float(entry_fee.get())
    blockchain.add_transaction(sender, receiver, amount, fee)
    update_block_explorer()

def do_pow_mine():
    blockchain.mine_block_pow("Miner")
    update_block_explorer()

def do_pos_mine():
    blockchain.mine_block_pos()
    update_block_explorer()

def register_validator():
    address = entry_validator.get()
    stake = float(entry_stake.get())
    blockchain.register_validator(address, stake)
    update_block_explorer()

def update_block_explorer():
    explorer_text.delete("1.0", tk.END)
    explorer_text.insert(tk.END, "Блокчейн:\n")
    for block in blockchain.chain:
        explorer_text.insert(tk.END, f"Блок {block['index']} | Hash: {block['hash'][:8]} | Validator: {block['validator']}\n")
    
    explorer_text.insert(tk.END, "\nМайнеры (PoW):\n")  
    for miner, balance in blockchain.miners.items():  # ✅ Теперь отображаются PoW майнеры
        explorer_text.insert(tk.END, f"{miner[:6]} - Баланс: {balance}\n")

    explorer_text.insert(tk.END, "\nВалидаторы (PoS):\n")
    for address, stake in blockchain.validators.items():
        explorer_text.insert(tk.END, f"{address[:6]} - Stake: {stake} - Баланс: {blockchain.balances[address]}\n") 

# ========================
# СОЗДАНИЕ GUI
# ========================
root = tk.Tk()
root.title("Blockchain Wallet & Explorer")

# Поля для транзакции
tk.Label(root, text="Отправитель:").grid(row=0, column=0)
entry_sender = tk.Entry(root)
entry_sender.grid(row=0, column=1)

tk.Label(root, text="Получатель:").grid(row=1, column=0)
entry_receiver = tk.Entry(root)
entry_receiver.grid(row=1, column=1)

tk.Label(root, text="Сумма:").grid(row=2, column=0)
entry_amount = tk.Entry(root)
entry_amount.grid(row=2, column=1)

tk.Label(root, text="Комиссия:").grid(row=3, column=0)
entry_fee = tk.Entry(root)
entry_fee.insert(0, "1")
entry_fee.grid(row=3, column=1)

send_btn = tk.Button(root, text="Отправить транзакцию", command=send_transaction)
send_btn.grid(row=4, column=0, columnspan=2)

# Поля для майнинга
mine_pow_btn = tk.Button(root, text="Майнинг (PoW)", command=do_pow_mine)
mine_pow_btn.grid(row=5, column=0)

mine_pos_btn = tk.Button(root, text="Майнинг (PoS)", command=do_pos_mine)
mine_pos_btn.grid(row=5, column=1)

# Поля для регистрации валидатора
tk.Label(root, text="Валидатор:").grid(row=6, column=0)
entry_validator = tk.Entry(root)
entry_validator.grid(row=6, column=1)

tk.Label(root, text="Стейк:").grid(row=7, column=0)
entry_stake = tk.Entry(root)
entry_stake.grid(row=7, column=1)

register_validator_btn = tk.Button(root, text="Зарегистрировать валидатора", command=register_validator)
register_validator_btn.grid(row=8, column=0, columnspan=2)

# Окно Block Explorer
tk.Label(root, text="Блок Эксплорер").grid(row=9, column=0, columnspan=2)
explorer_text = tk.Text(root, width=60, height=15)
explorer_text.grid(row=10, column=0, columnspan=2)

blockchain = Blockchain()
update_block_explorer()

root.mainloop()
