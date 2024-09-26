from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from api.birthday.serializers import BirthdaySerializer
from backend.models import Empprofile


class BirthdayView(generics.ListAPIView):
    serializer_class = BirthdaySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Empprofile.objects.filter(
            pi__dob__month=self.request.query_params.get('month'),
            pi__user__is_active=1
        ).order_by('pi__dob__day', 'pi__user__last_name')

        return queryset
