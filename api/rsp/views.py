from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.rsp.serializers import RSPIntroLetterSerializer
from frontend.rsp.models import RspIntroLetter


class RSPIntroLetterView(generics.ListAPIView):
    serializer_class = RSPIntroLetterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = RspIntroLetter.objects.filter(emp_id=self.request.query_params.get('pk'), status=1)
        return queryset