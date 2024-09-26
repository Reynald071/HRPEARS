from django.urls import path

from api.help_desk.views import DeskServicesTransactionView

urlpatterns = [
    path('transaction/', DeskServicesTransactionView.as_view(), name='help_desk_transaction'),
]