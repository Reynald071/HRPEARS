from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.help_desk.serializers import DeskServicesTransactionSerializer
from frontend.models import DeskServices


class DeskServicesTransactionView(generics.ListAPIView):
    serializer_class = DeskServicesTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('my_request'):
            queryset = DeskServices.objects.filter(requested_by_id=self.request.query_params.get('employee_id'))
            return queryset
        elif self.request.query_params.get('atm'):
            queryset = DeskServices.objects.filter(assigned_emp_id=self.request.query_params.get('employee_id'))
            return queryset
        else:
            if self.request.query_params.get('status') == '0':
                queryset = DeskServices.objects.filter(latest_status=0)
                return queryset
            elif self.request.query_params.get('status') == '1':
                queryset = DeskServices.objects.filter(latest_status=1)
                return queryset
            elif self.request.query_params.get('status') == '3':
                queryset = DeskServices.objects.filter(latest_status=3)
                return queryset
            elif self.request.query_params.get('status') == '4':
                queryset = DeskServices.objects.filter(latest_status=4)
                return queryset
            else:
                queryset = DeskServices.objects.all()
                return queryset