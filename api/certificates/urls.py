from django.urls import path

from api.certificates.views import CertificationTransactionViews

urlpatterns = [
    path('transaction/', CertificationTransactionViews.as_view(), name='api_cert_transaction')
]