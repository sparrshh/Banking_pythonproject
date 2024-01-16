# this is working
import pyodbc
from decimal import Decimal

class BankAccount:
    def __init__(self, account_number, account_holder, balance=0, pasword=None):
        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = balance
        self.pasword = pasword
        self.transactions = []  # Add a list to store transactions

    def deposit(self, amount):
        # Add 3% interest on deposits
        interest = Decimal(amount) * Decimal('0.03')
        total_amount = Decimal(amount) + interest
        self.balance += total_amount
        self.transactions.append(f"Deposit: Rs. {amount} (Interest: Rs. {interest})")
        return total_amount

    def withdraw(self, amount):
    # Deduct Rs. 200 on withdrawals
        total_amount = Decimal(amount) + Decimal('200')
        if total_amount > Decimal('0') and total_amount <= self.balance:
           self.balance -= total_amount
           self.transactions.append(f"Withdrawal: Rs. {amount} (Deduction: Rs. 200)")
           return total_amount
        else:
           return Decimal('0')   # Insufficient funds

    def get_balance(self):
        return self.balance
      
    def get_statement(self):
       print(f"Current Balance for account number {self.account_number} and holder ({self.account_holder} is):")
    
       num_transactions = len(self.transactions)
       total_credit = sum([amount for amount in self.transactions if 'Deposit' in amount])
       total_withdrawal = sum([amount for amount in self.transactions if 'Withdrawal' in amount])

       for transaction in self.transactions:
          print(transaction)

       
       print(f"{self.balance}\n")






def connect_to_database():
    connection = pyodbc.connect('Driver={SQL Server};Server=MSI-SPARSH\SQLEXPRESS;Database=bank_detail;Trusted_Connection=yes;')
    return connection

def create_account(cursor):
    account_number = input("Enter Account Number: ")
    account_holder = input("Enter Account Holder Name: ")
    pasword = input("Enter the password: ")
    
    cursor.execute('''
        INSERT INTO bank_accounts (account_number, account_holder, balance, pasword)
        VALUES (?, ?, ?, ?)
    ''', (account_number, account_holder, 0, pasword))

def main():
    connection = connect_to_database()
    cursor = connection.cursor()

    while True:
        print("\n1. Create Bank Account")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. View Balance")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            create_account(cursor)
            connection.commit()
            print("Account created successfully!")

        elif choice == '2':
            account_number = input("Enter Account Number: ")
            pasword = input("Enter the password: ")
            amount = float(input("Enter deposit amount: "))

            cursor.execute('SELECT balance FROM bank_accounts WHERE account_number = ? and pasword = ?', (account_number, pasword))
            row = cursor.fetchone()

            if row:
                balance = row.balance
                account = BankAccount(account_number, '', balance, pasword)
                total_amount = account.deposit(amount)

                cursor.execute('UPDATE bank_accounts SET balance = ? WHERE account_number = ? and pasword = ?', (account.get_balance(), account_number, pasword))
                connection.commit()
                print(f"Deposit successful! Amount credited with after 3% interest: Rs. {total_amount} and your current balance is {balance+total_amount}")
            else:
                print("Account not found or incorrect password!")

        elif choice == '3':
            account_number = input("Enter Account Number: ")
            pasword = input("Enter the password: ")
            amount = float(input("Enter withdrawal amount: "))

            cursor.execute('SELECT balance FROM bank_accounts WHERE account_number = ? and pasword = ?', (account_number, pasword))
            row = cursor.fetchone()

            if row:
                balance = row.balance
                account = BankAccount(account_number, '', balance, pasword)
                withdrawn_amount = account.withdraw(amount)

                if withdrawn_amount > Decimal('0'):
                    cursor.execute('UPDATE bank_accounts SET balance = ? WHERE account_number = ? and pasword = ?', (account.get_balance(), account_number, pasword))
                    connection.commit()
                    print(f"Amount Debited with 200 withdrawal fee: {withdrawn_amount} your currrent balance : {balance - withdrawn_amount} ")
                else:
                    print("Insufficient funds!")
            else:
                print("Account not found or incorrect password!")

        elif choice == '4':
            account_number = input("Enter the account number: ")
            pasword = input("Enter the password: ")
            cursor.execute('SELECT * FROM bank_accounts WHERE account_number = ? and pasword = ?', (account_number, pasword))
            row = cursor.fetchone()

            if row:
                balance = row.balance
                account = BankAccount(account_number, row.account_holder, balance, pasword)
                account.get_statement()
            else:
                print("Account not found or incorrect password!")

        elif choice == '5':
            print("Exiting program.")
            break

        else:
            print("Invalid choice. Please try again.")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()
