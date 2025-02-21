import random

class Validator:
    def _init_(self, name, stake=0):
        self.name = name
        self.stake = stake
        self.rewards = 0
        self.delegators = {}

    def add_stake(self, amount, delegator=None):
        self.stake += amount
        if delegator:
            if delegator in self.delegators:
                self.delegators[delegator] += amount
            else:
                self.delegators[delegator] = amount

    def add_reward(self, amount):
        self.rewards += amount
        # Распределение вознаграждений между делегаторами
        if self.delegators:
            for delegator, staked_amount in self.delegators.items():
                delegator_reward = amount * (staked_amount / self.stake)
                print(f"Delegator {delegator} received reward: {delegator_reward:.2f}")

class Blockchain:
    def _init_(self):
        self.validators = []
        self.transactions = []
        self.blocks = []
        self.transaction_fee = 1  # Условная комиссия за транзакцию

    def add_validator(self, validator):
        self.validators.append(validator)

    def delegate_stake(self, delegator, validator_name, amount):
        for validator in self.validators:
            if validator.name == validator_name:
                validator.add_stake(amount, delegator)
                print(f'{delegator} delegated {amount} coins to {validator_name}')
                return
        print(f'Validator {validator_name} not found.')

    def select_validator(self):
        total_stake = sum(v.stake for v in self.validators)
        if total_stake == 0:
            return None
        choice = random.uniform(0, total_stake)
        cumulative = 0
        for validator in self.validators:
            cumulative += validator.stake
            if cumulative >= choice:
                return validator

    def validate_transaction(self, transaction):
        # Проверка транзакции (баланс, формат, подпись)
        if transaction['amount'] > 0 and 'from' in transaction and 'to' in transaction:
            # Простая проверка баланса (в реальности нужна учетная запись)
            if transaction['amount'] > 100:
                print(f"Transaction from {transaction['from']} failed: insufficient balance.")
                return False
            return True
        return False

    def create_block(self, validator):
        if not self.transactions:
            print('No transactions to add to the block.')
            return
        valid_transactions = [tx for tx in self.transactions if self.validate_transaction(tx)]
        
        block = {'transactions': valid_transactions, 'validator': validator.name}
        self.blocks.append(block)

        # Вознаграждение за блок + сборы за транзакции
        total_reward = 10 + len(valid_transactions) * self.transaction_fee
        validator.add_reward(total_reward)
        
        self.transactions.clear()
        print(f'Block created by {validator.name}. Rewards: {validator.rewards}')

    def show_status(self):
        print("\n=== Blockchain Status ===")
        for validator in self.validators:
            print(f"Validator {validator.name}: Stake={validator.stake}, Rewards={validator.rewards}")
            if validator.delegators:
                print(f"  Delegators: {validator.delegators}")
        print("=========================")

# Пример использования
blockchain = Blockchain()
blockchain.add_validator(Validator('Alice', 50))
blockchain.add_validator(Validator('Bob', 30))
blockchain.delegate_stake('Charlie', 'Alice', 20)

blockchain.transactions.append({'from': 'Alice', 'to': 'Bob', 'amount': 10})
blockchain.transactions.append({'from': 'Bob', 'to': 'Charlie', 'amount': 5})

validator = blockchain.select_validator()
if validator:
    blockchain.create_block(validator)
else:
    print('No validator selected.')

blockchain.show_status()
