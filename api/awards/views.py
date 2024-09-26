from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.awards.serializers import AwGuidelinesSerializer
from backend.awards.models import AwGuidelines


class AwGuidelinesViews(generics.ListAPIView):
    queryset = AwGuidelines.objects.all().order_by('-year')
    serializer_class = AwGuidelinesSerializer
    permission_classes = [IsAuthenticated]