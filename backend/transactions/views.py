from django.shortcuts import render
import sqlite3
import pandas as pd
from transactions.models import Account

class ImportData:
    def __init__(self, file="accounts.csv"):
        self.csv_file = file
    
    def import_and_update_csv(self):
            try:
                df = pd.read_csv(self.csv_file)
            except FileNotFoundError:
                print(f"Error: File '{self.csv_file}' not found")
                return
            
            for _,row in df.iterrows():
                id = row['ID']
                name = row['Name']
                balance = row['Balance']
                
                if self.checkDuplicates(id):
                    if self.checkBalance(id,balance):
                        continue
                    else:
                        self.updateBalance(id,balance)
                else:
                    self.addAccounts(id, name, balance)
    
    # checking for a duplicate
    def checkDuplicates(self,id):
        return Account.objects.filter(id=id).exists()
    # checking balance incase of a duplicate
    def checkBalance(self,id,new_balance):
        try:
            account = Account.objects.get(id=id)
            return account.balance == new_balance
        except Account.DoesNotExist:
            print(f"Error: Account with id {id} does not exist")
            return False
    def updateBalance(self,id,new_balance):
        try:
            account = Account.objects.get(id=id)
            account.balance = new_balance
            account.save()
        except Account.DoesNotExist:
            print(f"Error: Account with ID {id} not found for update") 
            

    def addAccounts(self,id,name,balance):
        Account.objects.create(id=id, name=name, balance=balance)
