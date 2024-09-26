from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.personnel.payroll.serializers import PayrollMovSerializer
from backend.pas.payroll.models import PayrollMovs


class PayrollMovView(generics.ListAPIView):
    serializer_class = PayrollMovSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = PayrollMovs.objects.filter(mov_type_id=self.request.query_params.get('mov_type_id'))
        return queryset