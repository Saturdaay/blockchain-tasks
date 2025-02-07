import sys
import hashlib
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget

# Транзакция моделі
class Transaction:
    def __init__(self, sender, receiver, amount, fee):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.fee = fee
        self.tx_hash = self.calculate_hash()

    def calculate_hash(self):
        data = f"{self.sender}{self.receiver}{self.amount}{self.fee}"
        return hashlib.sha256(data.encode()).hexdigest()

# Меркле ағашы
class MerkleTree:
    def __init__(self, transactions):
        self.transactions = transactions
        self.root = self.build_merkle_root()

    def build_merkle_root(self):
        tx_hashes = [tx.tx_hash for tx in self.transactions]
        if not tx_hashes:
            return None
        while len(tx_hashes) > 1:
            new_level = []
            for i in range(0, len(tx_hashes), 2):
                if i + 1 < len(tx_hashes):
                    combined = tx_hashes[i] + tx_hashes[i+1]
                else:
                    combined = tx_hashes[i] + tx_hashes[i]  # Егер тақ сан болса, соңғы элементті қайталаймыз
                new_level.append(hashlib.sha256(combined.encode()).hexdigest())
            tx_hashes = new_level
        return tx_hashes[0]

# Блок моделі
class Block:
    def __init__(self, transactions, previous_hash):
        self.transactions = transactions
        self.merkle_root = MerkleTree(transactions).root
        self.previous_hash = previous_hash
        self.block_hash = self.calculate_hash()

    def calculate_hash(self):
        data = f"{self.previous_hash}{self.merkle_root}"
        return hashlib.sha256(data.encode()).hexdigest()

# UTXO моделі
class Blockchain:
    def __init__(self):
        self.chain = []
        self.utxo = {"Alice": 100, "Bob": 100, "Charlie": 100, "Dave": 100}
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block([], "0" * 64)
        self.chain.append(genesis_block)

    # Валидация
    def validate_transaction(self, transaction):
        if transaction.sender not in self.utxo or self.utxo[transaction.sender] < transaction.amount + transaction.fee:
            return False
        return True

    def add_block(self, transactions):
        for tx in transactions:
            if not self.validate_transaction(tx):
                print(f"Қате: {tx.sender} үшін баланс жеткіліксіз!")
                return False
        for tx in transactions:
            self.utxo[tx.sender] -= (tx.amount + tx.fee)
            self.utxo[tx.receiver] = self.utxo.get(tx.receiver, 0) + tx.amount
        new_block = Block(transactions, self.chain[-1].block_hash)
        self.chain.append(new_block)
        return True

# PyQt GUI
class BlockchainGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.blockchain = Blockchain()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Blockchain Explorer")
        self.setGeometry(100, 100, 600, 400)
        
        # Виджет для отображения текста
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        
        # Кнопка для добавления нового блока
        self.button = QPushButton("Жаңа блок қосу", self)
        self.button.clicked.connect(self.add_block)
        
        # Лейаут для расположения виджетов
        layout = QVBoxLayout()
        layout.addWidget(self.text_area)
        layout.addWidget(self.button)
        
        # Контейнер для лейаута
        container = QWidget()
        container.setLayout(layout)
        
        # Установка центрального виджета
        self.setCentralWidget(container)
        
        # Обновление отображения
        self.update_display()

    def add_block(self):
        # Пример транзакций
        transactions = [Transaction("Alice", "Bob", 10, 1), Transaction("Bob", "Charlie", 5, 0.5)]
        
        if self.blockchain.add_block(transactions):
            self.update_display()

    def update_display(self):
        # Обновляем отображаемую информацию о блоках
        text = "Blockchain:\n"
        for block in self.blockchain.chain:
            text += f"Блок хэші: {block.block_hash}\n"
            text += f"Алдыңғы хэш: {block.previous_hash}\n"
            text += f"Меркле түбірі: {block.merkle_root}\n\n"
        self.text_area.setText(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = BlockchainGUI()
    gui.show()
    sys.exit(app.exec())
