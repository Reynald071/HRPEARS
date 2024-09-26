from django.urls import path

from api.tracking.views import DtsTransactionView, DtsDocumentCustodianView, DtsTransactionOthersView, \
    MyDtsDocumentView, DtsTransactionArchiveView

urlpatterns = [
    path('transaction/', DtsTransactionView.as_view(), name='api_dt_transactions'),
    path('transaction/others/', DtsTransactionOthersView.as_view(), name='api_dt_transactions_others'),
    path('transaction/my-drn/', MyDtsDocumentView.as_view(), name='api_my_drn_transactions'),
    path('transaction/archive/', DtsTransactionArchiveView.as_view(), name='api_archive_transactions'),
    path('custodian/', DtsDocumentCustodianView.as_view(), name='api_dt_custodians')
]