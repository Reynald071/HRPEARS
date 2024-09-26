from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.personnel.overtime.serializers import OvertimeDetailsSerializer, OvertimeSerializer
from frontend.pas.overtime.models import OvertimeDetails, Overtime


class OvertimeDetailsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OvertimeDetailsSerializer

    def get_queryset(self):
        queryset = OvertimeDetails.objects.filter(overtime__status=self.request.query_params.get('status'))
        return queryset


class OvertimeView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OvertimeSerializer

    def get_queryset(self):
        queryset = Overtime.objects.filter(status=self.request.query_params.get('status'))
        return queryset

