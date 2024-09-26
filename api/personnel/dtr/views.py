from django.db.models.functions import Upper
from django_mysql.models.functions import SHA1
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.personnel.dtr.serializers import DTRTimeSerializer
from backend.models import WfhTime, Empprofile


class DTRTimeViews(generics.ListAPIView):
    serializer_class = DTRTimeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('period_from') and self.request.query_params.get('period_to'):
            employee = Empprofile.objects.filter(id_number=self.request.query_params.get('employee_id')).first()
            queryset = WfhTime.objects.filter(emp_id=employee.id,
                                              type_id__isnull=False,
                                              datetime__date__range=(
                                                  self.request.query_params.get('period_from'), self.request.query_params.get('period_to')
                                              )).annotate(date=Upper('datetime'))
            return queryset
        else:
            queryset = WfhTime.objects.annotate(hash=SHA1('emp_id')).filter(hash=self.request.query_params.get('employee_id')).annotate(date=Upper('datetime'))
            return queryset