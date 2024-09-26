from django_mysql.models.functions import SHA1
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.documents.serializers import Document201Serializers, DocumentIssuancesSerializers, RSOAttachmentSerializer
from backend.documents.models import Docs201Files, DocsIssuancesFiles
from backend.templatetags.tags import force_token_decryption
from frontend.rso.models import RsoAttachment


class Document201Views(generics.ListAPIView):
    serializer_class = Document201Serializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Docs201Files.objects.annotate(hash=SHA1('emp_id'), type_hash=SHA1('number_201_type_id')).filter(hash=self.request.query_params.get('employee_id'),
                                                                                                            type_hash=self.request.query_params.get('type_id'))
        return queryset


class DocumentIssuancesViews(generics.ListAPIView):
    serializer_class = DocumentIssuancesSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DocsIssuancesFiles.objects.filter(issuances_type_id=self.request.query_params.get('type_id'))

        return queryset


class RSOAttachmentViews(generics.ListAPIView):
    serializer_class = RSOAttachmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = RsoAttachment.objects.filter(type_id=force_token_decryption(self.request.query_params.get('type_pk')))
        return queryset