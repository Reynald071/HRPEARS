from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.directory_list.serializers import DirectoryListSerializers
from backend.models import DirectoryContact


class DirectoryListView(generics.ListAPIView):
    serializer_class = DirectoryListSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('orgtype_id'):
            queryset = DirectoryContact.objects.filter(Q(orgtype_id=self.request.query_params.get('orgtype_id')), ~Q(status=0))
            return queryset
        else:
            queryset = DirectoryContact.objects.filter(~Q(status=0))
            return queryset