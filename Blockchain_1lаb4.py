import tkinter as tk  # Tkinter - графикалық интерфейс кітапханасы
from tkinter import messagebox  # Хабарламаларды көрсету үшін messagebox
import hashlib  # Хештеу үшін hashlib кітапханасын қолданамыз
import time  # Уақытты басқару үшін time кітапханасы

# Хеш-функция (құпиялылық үшін деректерді хештеу)
def simple_hash(data):
    # Хештеу алгоритмі ретінде MD5 қолданамыз
    return hashlib.md5(data.encode('utf-8')).hexdigest()

# Блок классы (блоктардың құрылымы)
class Block:
    def __init__(self, data, previous_hash=''):
        # timestamp - блоктың жасалған уақыты
        self.timestamp = time.time()  
        # data - блоктың деректері
        self.data = data  
        # previous_hash - алдыңғы блоктың хеші
        self.previous_hash = previous_hash  
        # hash - блоктың хеші, оны есептеу үшін calculate_hash функциясын қолданамыз
        self.hash = self.calculate_hash()

    # Блоктың хешін есептейтін функция
    def calculate_hash(self):
        # Хеш үшін уақыт, деректер және алдыңғы блоктың хешін біріктіреміз
        block_data = str(self.timestamp) + self.data + self.previous_hash
        return simple_hash(block_data)

# Blockchain (блокчейн) классы
class Blockchain:
    def __init__(self):
        # Алдымен Genesis Block (алғашқы блок) құрып, тізімді бастаймыз
        self.chain = [self.create_genesis_block()]

    # Genesis Block (алғашқы блок) жасау функциясы
    def create_genesis_block(self):
        # Алғашқы блоктың деректері "Genesis Block"
        return Block(data="Genesis Block")

    # Жаңа блок қосу функциясы
    def add_block(self, new_block):
        self.chain.append(new_block)

    # Блокчейннің валидтілігін тексеретін функция
    def is_valid(self):
        # Барлық блоктарды тексереміз
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Егер ағымдағы блоктың хеші дұрыс емес болса
            if current_block.hash != current_block.calculate_hash():
                return False

            # Егер ағымдағы блоктың алдыңғы хеші дұрыс емес болса
            if current_block.previous_hash != previous_block.hash:
                return False

        return True  # Барлық блоктар дұрыс болса, blockchain дұрыс

# GUI интерфейсі классы
class BlockchainExplorerGUI:
    def __init__(self, root, blockchain):
        # root - Tkinter терезесі, blockchain - блокчейннің объектісі
        self.root = root
        self.blockchain = blockchain
        self.root.title("Blockchain Explorer")  # Тақырып

        # Интерфейсті жасау функциясын шақырамыз
        self.create_widgets()

    def create_widgets(self):
        # Бастапқы мәтін жазу (Blockchain Explorer деп көрсетеміз)
        self.label = tk.Label(self.root, text="Blockchain Explorer", font=("Arial", 16))
        self.label.pack(pady=10)

        # Блок қосу үшін батырма
        self.add_button = tk.Button(self.root, text="Add Block", command=self.add_block)
        self.add_button.pack(pady=10)

        # Blockchain-нің валидтілігін тексеру үшін батырма
        self.validate_button = tk.Button(self.root, text="Validate Blockchain", command=self.validate_blockchain)
        self.validate_button.pack(pady=10)

        # Блоктарды көрсететін тізім
        self.block_listbox = tk.Listbox(self.root, width=100, height=20)
        self.block_listbox.pack(pady=10)

    # Жаңа блок қосу функциясы
    def add_block(self):
        # Жаңа дерек қосамыз (мысалы "Block 1", "Block 2")
        new_data = f"Block {len(self.blockchain.chain)}"
        # Жаңа блокты қосамыз
        new_block = Block(data=new_data, previous_hash=self.blockchain.chain[-1].hash)
        self.blockchain.add_block(new_block)  # Блокчейнге қосамыз
        self.update_block_list()  # Блоктарды жаңарту

    # Блокчейннің валидтілігін тексеру функциясы
    def validate_blockchain(self):
        if self.blockchain.is_valid():
            # Егер блокчейн валидті болса, хабарлама көрсетеміз
            messagebox.showinfo("Blockchain Status", "Blockchain is valid!")
        else:
            # Егер блокчейн бұзылған болса, хабарлама көрсетеміз
            messagebox.showerror("Blockchain Status", "Blockchain is invalid!")

    # Блоктардың тізімін жаңарту функциясы
    def update_block_list(self):
        self.block_listbox.delete(0, tk.END)  # Алдымен ескі тізімді өшіріп тастаймыз
        # Әр блок үшін ақпаратты көрсетеміз
        for i, block in enumerate(self.blockchain.chain):
            block_info = f"Block {i}: {block.data} - {block.hash}"
            self.block_listbox.insert(tk.END, block_info)  # Жаңа ақпаратты қосамыз

# Программа басталатын негізгі код
if __name__ == "__main__":
    blockchain = Blockchain()  # Blockchain объектісін жасаймыз
    root = tk.Tk()  # Tkinter терезесін жасаймыз
    app = BlockchainExplorerGUI(root, blockchain)  # GUI қосымшасын іске қосамыз
    root.mainloop()  # Интерфейс жұмыс істей береді
