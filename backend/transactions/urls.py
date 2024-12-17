from django.urls import path
from .views import ImportDataView

urlpatterns = [
    path('import-accounts/', ImportDataView.as_view(), name='import-accounts'),
]