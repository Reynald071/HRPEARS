from django.db.models import Q
from django_mysql.models.functions import SHA1
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from api.personnel.travel.serializers import TravelHistorySerializers, TravelDetailsSerializers, TravelSerializers
from backend.templatetags.tags import check_permission
from frontend.models import Ritopeople, Ritodetails, Rito


class TravelHistoryView(generics.ListAPIView):
    serializer_class = TravelHistorySerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Ritopeople.objects.annotate(hash=SHA1('name_id')).filter(hash=self.request.query_params.get('employee_id'),
                                                                            detail__rito__status=3)
        return queryset


class TravelDetailsView(generics.ListAPIView):
    serializer_class = TravelDetailsSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Ritodetails.objects.annotate(hash=SHA1('rito__emp_id')).filter(rito__status=self.request.query_params.get('status'),
                                                                                    hash=self.request.query_params.get('employee_id'))
        return queryset


class TravelView(generics.ListAPIView):
    serializer_class = TravelSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('status') == 'drafts':
            queryset = Rito.objects.annotate(hash=SHA1('emp_id')).filter(status=4, hash=self.request.query_params.get('employee_id'))
            return queryset
        elif self.request.query_params.get('status') == 'workflow':
            queryset = Rito.objects.annotate(hash=SHA1('emp_id')).filter(status__in=[2, 3, 5], hash=self.request.query_params.get('employee_id'))
            return queryset
        else:
            if self.request.query_params.get('status'):
                queryset = Rito.objects.annotate(hash=SHA1('emp_id')).filter(status=self.request.query_params.get('status'), hash=self.request.query_params.get('employee_id'))
                return queryset
            else:
                if self.request.query_params.get('start_date'):
                    queryset = Rito.objects.annotate(hash=SHA1('emp_id')).filter(
                        date__date__range=[self.request.query_params.get('start_date'), self.request.query_params.get('end_date')],
                        status__in=[2, 3, 5],
                        hash=self.request.query_params.get('employee_id')
                    )

                    return queryset
                else:
                    keyword = self.request.query_params.get('keyword')
                    passengers = Ritopeople.objects.filter(
                        Q(name__pi__user__last_name__icontains=keyword) |
                        Q(name__pi__user__first_name__icontains=keyword) |
                        Q(name__id_number=keyword) |
                        Q(detail__place__icontains=keyword) |
                        Q(detail__purpose__icontains=keyword) |
                        Q(detail__expected_output__icontains=keyword)
                    ).values_list('detail__rito_id')

                    queryset = Rito.objects.annotate(hash=SHA1('emp_id')).filter(
                        id__in=passengers,
                        status__in=[2, 3, 5],
                        hash=self.request.query_params.get('employee_id')
                    )

                    return queryset


class TravelAdminPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if check_permission(request.user, 'travel_order') or check_permission(request.user, 'superadmin'):
            return True
        else:
            return False


class TravelAdminView(generics.ListAPIView):
    serializer_class = TravelSerializers
    permission_classes = [IsAuthenticated, TravelAdminPermissions]

    def get_queryset(self):
        if self.request.query_params.get('status') == 'workflow':
            queryset = Rito.objects.filter(status__in=[2, 3, 5], date__year__icontains=self.request.query_params.get('year'))
            return queryset
        elif self.request.query_params.get('status') == 'to-generation':
            queryset = Rito.objects.filter(Q(approvedrito__status=1) & Q(date__year__icontains=self.request.query_params.get('year')),
                                           Q(date_administered=None))
            return queryset
        elif self.request.query_params.get('status') == 'merge':
            tracking_no = self.request.query_params.get('tracking-no')
            queryset = Rito.objects.filter(tracking_merge=tracking_no, date__year__icontains=self.request.query_params.get('year'))
            return queryset
        else:
            if self.request.query_params.get('status'):
                queryset = Rito.objects.filter(status=self.request.query_params.get('status'),
                                               date__year__icontains=self.request.query_params.get('year'))
                return queryset
            else:
                keyword = self.request.query_params.get('keyword')
                passengers = Ritopeople.objects.filter(
                    Q(name__pi__user__last_name__icontains=keyword) |
                    Q(name__pi__user__first_name__icontains=keyword) |
                    Q(name__id_number=keyword) |
                    Q(detail__place__icontains=keyword) |
                    Q(detail__purpose__icontains=keyword) |
                    Q(detail__expected_output__icontains=keyword)
                ).values_list('detail__rito_id')

                queryset = Rito.objects.filter(
                    id__in=passengers,
                    status__in=[2, 3, 5],
                    date__year__icontains=self.request.query_params.get('year')
                )

                return queryset
