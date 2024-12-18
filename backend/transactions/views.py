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
from django.core.paginator import Paginator
import json



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
    def get(self, request):
        return render(request, 'transactions/import_accounts.html')
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
    
    
## return account info 
@method_decorator(csrf_exempt, name='dispatch')
class ShowBalance(View):
    def get(self,request,id):
        try:
            account = Account.objects.get(id=id)
            return render(request, 'transactions/show_balance.html', {
                'account': account
            })
        except Account.DoesNotExist:
            return JsonResponse({'error': 'account not found'}, status=404)
        
## return all accounts info
@method_decorator(csrf_exempt, name='dispatch')
class ListAccounts(View):
    def get(self,request):
        try:
            accounts = Account.objects.all()  

            page_number = request.GET.get('page', 1)
            page_size = request.GET.get('page_size', 10) 
            paginator = Paginator(accounts, page_size)
            page = paginator.get_page(page_number)
            
            accounts_data = [
                {'id': account.id, 'name': account.name, 'balance': account.balance}
                for account in page
            ]
            return render(request, 'transactions/list_accounts.html', {
                'accounts': page,
                'current_page': page.number,
                'total_pages': paginator.num_pages,
                'has_previous': page.has_previous(),
                'has_next': page.has_next(),
                'page_range': paginator.get_elided_page_range(page.number, on_each_side=2, on_ends=1)
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

## transfer funds between accounts ! 
@method_decorator(csrf_exempt, name='dispatch')
class TransferFunds(View):
    def get(self, request):
        accounts = Account.objects.all().order_by('name')
        return render(request, 'transactions/transfer_funds.html', {
            'accounts': accounts
        })
    def post(self,request):
        data = json.loads(request.body)
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        amount = data.get('amount')
        
        if not sender_id or not receiver_id or not amount:
            return JsonResponse({'error': 'Missing fields'}, status=400)

        try:
            sender = Account.objects.get(id=sender_id)
            receiver = Account.objects.get(id=receiver_id)
        except Account.DoesNotExist:
            return JsonResponse({'error': 'sender or reciever account does not exist'}, status=404)

        if sender.balance < amount:
            return JsonResponse({'error': 'not enough funds'}, status=400)

        try:
            with transaction.atomic():
                sender.balance -= amount
                sender.save()

                receiver.balance += amount
                receiver.save()

            return JsonResponse({'message': 'Transfer successful'}, status=200)

        except Exception as e:
            return JsonResponse({'error': f'Transfer failed: {str(e)}'}, status=500)
        