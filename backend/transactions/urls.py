from django.urls import path
from .views import ImportDataView, ShowBalance, ListAccounts

urlpatterns = [
    path('import-accounts/', ImportDataView.as_view(), name='import-accounts'),
    path('balance/<uuid:id>/', ShowBalance.as_view(), name='show_balance'),
    path('list/', ListAccounts.as_view(), name='list_accounts')
]