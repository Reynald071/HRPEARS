from django.db.models import Q, F
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.tracking.serializers import DtsTransactionSerializer, DtsDocumentCustodianSerializer, \
    DtsTransactionOthersSerializer, DtsDocumentSerializer
from backend.documents.models import DtsTransaction, DtsDocument
from backend.models import Empprofile, AuthUserUserPermissions
from backend.templatetags.tags import check_permission


class DtsTransactionView(generics.ListAPIView):
    serializer_class = DtsTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DtsTransaction.objects.filter(
            Q(trans_to=self.request.query_params.get('employee_id')),
            Q(action__in=[1, 2, 3]), ~Q(action_taken='For filing'), ~Q(trans_from_id=F('trans_to_id'))
        ).order_by('-date_saved')
        if self.request.query_params.get('keyword'):
            queryset = queryset.filter(
                Q(document__generated_drn__icontains=self.request.query_params.get('keyword')) |
                Q(document__tracking_no__icontains=self.request.query_params.get('keyword')))
        if self.request.query_params.get('status'):
            queryset = queryset.filter(
                action=self.request.query_params.get('status'),
            )
        uniquedata = list()
        uniquetransactions = list()
        for d in queryset:
            if check_permission(self.request.user, 'document_custodian'):
                if d.document_id not in uniquedata:
                    uniquedata.append(d.document_id)
                    uniquetransactions.append(d.id)
            else:
                if d.document_id not in uniquedata:
                    uniquedata.append(d.document_id)
                    uniquetransactions.append(d.id)
        queryset = DtsTransaction.objects.filter(Q(id__in=uniquetransactions)).order_by('-date_saved')
        return queryset


class DtsTransactionArchiveView(generics.ListAPIView):
    serializer_class = DtsDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DtsDocument.objects.filter(is_blank=False).order_by('-date_saved')
        return queryset


class DtsTransactionOthersView(generics.ListAPIView):
    serializer_class = DtsTransactionOthersSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = None
        if self.request.query_params.get('sentbox'):
            if self.request.query_params.get('sentbox') == "all":
                queryset = DtsTransaction.objects.filter(
                    trans_from=self.request.query_params.get('employee_id'),
                    action__in=[0],
                    document__is_blank=False
                ).order_by('-date_saved')
        elif self.request.query_params.get('cc'):
            if self.request.query_params.get('cc') == "all":
                queryset = DtsTransaction.objects.filter(
                    trans_to=self.request.query_params.get('employee_id'),
                    action__in=[4], document__is_blank=False
                ).order_by('-date_saved')
        elif self.request.query_params.get('section_documents'):
            if self.request.query_params.get('section_documents') == "all":
                my_section_id = Empprofile.objects.filter(
                    id=self.request.query_params.get('employee_id')).first().section_id
                queryset = DtsTransaction.objects.filter(
                    Q(trans_to__section_id=my_section_id),
                    ~Q(trans_to=self.request.query_params.get('employee_id')),
                    ~Q(trans_from=self.request.query_params.get('employee_id')),
                    Q(action__in=[1, 2, 3]), Q(document__is_blank=False)
                ).order_by('-date_saved')

        uniquedata = list()
        uniquetransactions = list()
        for d in queryset:
            if check_permission(self.request.user, 'document_custodian'):
                if d.document_id not in uniquedata:
                    uniquedata.append(d.document_id)
                    uniquetransactions.append(d.id)
            else:
                if d.document_id not in uniquedata and not d.document.get_my_drn:
                    uniquedata.append(d.document_id)
                    uniquetransactions.append(d.id)
        queryset = DtsTransaction.objects.filter(Q(id__in=uniquetransactions)).order_by('-date_saved')
        return queryset


class MyDtsDocumentView(generics.ListAPIView):
    serializer_class = DtsTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('drn'):
            if self.request.query_params.get('drn') == "all":
                queryset = DtsTransaction.objects.filter(
                    trans_to=self.request.query_params.get('employee_id'),
                    action__in=[0],
                    document__is_blank=True
                ).order_by('-date_saved')
                return queryset


class DtsDocumentCustodianView(generics.ListAPIView):
    serializer_class = DtsDocumentCustodianSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        data = AuthUserUserPermissions.objects.filter(permission__codename='document_custodian').order_by(
            'user__first_name')
        return data
