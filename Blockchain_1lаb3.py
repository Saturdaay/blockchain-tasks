import hashlib
import time

# Хеш-функция
def simple_hash(data):
    # MD5 хеш-функцияны пайдаланып, деректерді хештейміз
    return hashlib.md5(data.encode('utf-8')).hexdigest()

# Класс Block
class Block:
    def __init__(self, data, previous_hash=''):
        # Блоктың уақыт белгілері
        self.timestamp = time.time()  # Блоктың жасалған уақыты
        self.data = data  # Блоктың деректері
        self.previous_hash = previous_hash  # Алдыңғы блоктың хеші (генезис-блокта бос болады)
        self.hash = self.calculate_hash()  # Блоктың өзіндік хешін есептейміз

    def calculate_hash(self):
        # Блоктың хешін есептеу үшін оның деректерін, уақытын және алдыңғы блоктың хешін біріктіріп, хеш аламыз
        block_data = str(self.timestamp) + self.data + self.previous_hash
        return simple_hash(block_data)


# Класс Blockchain
class Blockchain:
    def __init__(self):
        # Блокчейннің бастапқы блоктары
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        # Генезис-блокты жасаймыз
        return Block(data="Genesis Block")

    def add_block(self, new_block):
        # Жаңа блокты қосамыз
        self.chain.append(new_block)

    def is_valid(self):
        # Блокчейннің дұрыстығын тексереміз
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Блоктың хешін қайта тексереміз
            if current_block.hash != current_block.calculate_hash():
                return False

            # Алдыңғы блоктың хеші дұрыс емес болса
            if current_block.previous_hash != previous_block.hash:
                return False

        return True


# Пример использования
if __name__ == "__main__":
    # Блокчейнді құру
    blockchain = Blockchain()

    # Жаңа блоктар қосамыз
    blockchain.add_block(Block(data="Second Block", previous_hash=blockchain.chain[-1].hash))
    blockchain.add_block(Block(data="Third Block", previous_hash=blockchain.chain[-1].hash))

    # Блоктарды шығару
    for i, block in enumerate(blockchain.chain):
        print(f"Block {i}:")
        print(f"  Timestamp: {block.timestamp}")
        print(f"  Data: {block.data}")
        print(f"  Previous Hash: {block.previous_hash}")
        print(f"  Hash: {block.hash}")
        print("-" * 50)

    # Блокчейннің дұрыстығын тексеру
    if blockchain.is_valid():
        print("Blockchain is valid!")
    else:
        print("Blockchain is invalid!")
