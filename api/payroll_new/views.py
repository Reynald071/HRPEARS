from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from frontend.payroll_new.models import Payslip
from .serializers import PayslipSerializer


class PayslipViews(generics.ListAPIView):
    serializer_class = PayslipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id_number = self.request.query_params.get('id_number')
        queryset = Payslip.objects.using('payslip').filter(fldempid=id_number)

        return queryset
        

