from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.personnel.endorsement.serializers import EndorsementSerializer, EndorsementPeopleSerializer
from backend.pas.endorsement.models import PasEndorsement, PasEndorsementPeople


class EndorsementView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EndorsementSerializer

    def get_queryset(self):
        employee = self.request.query_params.get('employee')
        if employee:
            employee = PasEndorsementPeople.objects.filter(Q(emp__pi__user__first_name__icontains=employee) |
                                                           Q(emp__pi__user__last_name__icontains=employee)).order_by('id')

            queryset = PasEndorsement.objects.filter(id__in=[row.endorsement_id for row in employee])
            return queryset
        else:
            queryset = PasEndorsement.objects.order_by('-date')
            return queryset


class EndorsementPeopleView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EndorsementPeopleSerializer

    def get_queryset(self):
        if self.request.query_params.get('pk'):
            queryset = PasEndorsementPeople.objects.filter(endorsement_id=self.request.query_params.get('pk')).order_by('id')
            return queryset