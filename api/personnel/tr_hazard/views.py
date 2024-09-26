from django_mysql.models.functions import SHA1
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.personnel.tr_hazard.serializers import HazardReportSerializer
from backend.models import Empprofile
from frontend.models import HazardReport


class HazardReportView(generics.ListAPIView):
    serializer_class = HazardReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('status'):
            queryset = HazardReport.objects.annotate(hash=SHA1('emp_id')).filter(
                status=self.request.query_params.get('status'),
                hash=self.request.query_params.get('employee_id')
            )

            return queryset
        else:
            queryset = HazardReport.objects.annotate(hash=SHA1('emp_id')).filter(
                hash=self.request.query_params.get('employee_id')
            )

            return queryset


class HazardReportAnnexBView(generics.ListAPIView):
    serializer_class = HazardReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        employee = Empprofile.objects.filter(id=self.request.query_params.get('employee_id'))

        if employee:
            queryset = HazardReport.objects.filter(emp__section__div_id=employee.first().section.div_id, status=1)

            return queryset
