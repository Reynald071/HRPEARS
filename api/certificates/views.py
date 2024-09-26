from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.certificates.serializers import CertificationTransactionSerializer
from backend.certificates.models import CertTransaction


class CertificationTransactionViews(generics.ListAPIView):
    serializer_class = CertificationTransactionSerializer
    permissions_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CertTransaction.objects.filter(
            emp_id=self.request.query_params.get('employee_id'),
            status=1
        )
        return queryset
