from django.urls import path
from .views import ImportDataView, ShowBalance, ListAccounts,TransferFunds

urlpatterns = [
    path('import-accounts/', ImportDataView.as_view(), name='import-accounts'),
    path('balance/<uuid:id>/', ShowBalance.as_view(), name='show_balance'),
    path('list/', ListAccounts.as_view(), name='list_accounts'),
    path('transfer/', TransferFunds.as_view(), name='transfer_funds')
]