from django.shortcuts import render
import sqlite3
import pandas as pd
from transactions.models import Account
from django.db import transaction
from django.views import View
from django.http import JsonResponse
import io
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class ImportData:
    def __init__(self, file):
        self.csv_file = file
    
    def import_and_update_csv(self):
            try:
                df = pd.read_csv(io.StringIO(self.csv_file.read().decode('utf-8')))
                stats = {
                'total_records': len(df),
                'new_accounts': 0,
                'updated_accounts': 0,
                'unchanged_accounts': 0,
                
            }
            
                try:
                    with transaction.atomic():
                        for _,row in df.iterrows():
                            try:
                                id = row['ID']
                                name = row['Name']
                                balance = row['Balance']
                                
                                if self.checkDuplicates(id):
                                    if self.checkBalance(id,balance):
                                        stats['unchanged_accounts'] += 1
                                    else:
                                        self.updateBalance(id,balance)
                                        stats['updated_accounts'] += 1
                                else:
                                    self.addAccounts(id, name, balance)
                                    stats['new_accounts'] += 1
                            except KeyError as e:
                                stats['errors'].append(f"Missing column: {str(e)}")
                                raise
                            except Exception as e:
                                stats['errors'].append(f"Error processing row: {str(e)}")
                                raise
                    return {
                        'status': 'success',
                        'message': 'import completed successfully',
                        'statistics': stats
                    }
                        
                except Exception as e:
                    print(f"transaction failed {e}")
            
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f'Failed to read CSV file: {str(e)}'
                }
    
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
        
@method_decorator(csrf_exempt, name='dispatch')
class ImportDataView(View):
    def post(self, request):
        if 'file' not in request.FILES:
            return JsonResponse({
                'status': 'error',
                'message': 'No file uploaded'
            }, status=400)
            
        csv_file = request.FILES['file']
        
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({
                'status': 'error',
                'message': 'File must be a CSV format'
            }, status=400)

        importer = ImportData(csv_file)
        result = importer.import_and_update_csv()
        
        return JsonResponse(result, safe=False)