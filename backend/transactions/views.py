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
            
            for row in df.iterrows():
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
    
    def checkDuplicates(self,id):
        pass
    def addAccounts(self,id,name,balance):
        pass
    def checkBalance(self,id,balance):
        pass
    def updateBalance(self,id,balance):
        pass
    
        
