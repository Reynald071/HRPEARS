from django_mysql.models.functions import SHA1
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from api.announcement.serializers import AnnouncementSerializers
from backend.templatetags.tags import check_permission
from frontend.models import PortalAnnouncements


class AnnouncementPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if check_permission(request.user, 'announcements') or check_permission(request.user, 'superadmin'):
            return True
        else:
            return False


class AnnouncementView(generics.ListAPIView):
    serializer_class = AnnouncementSerializers
    permission_classes = [IsAuthenticated, AnnouncementPermissions]

    def get_queryset(self):
        if self.request.user.is_superuser:
            if self.request.query_params.get('status'):
                queryset = PortalAnnouncements.objects.filter(is_active=self.request.query_params.get('status'))\
                    .order_by('is_active', 'is_urgent', 'datetime')
                return queryset
            else:
                queryset = PortalAnnouncements.objects.order_by('is_active', 'is_urgent', 'datetime')
                return queryset
        else:
            if self.request.query_params.get('status'):
                queryset = PortalAnnouncements.objects.annotate(hash=SHA1('uploaded_by_id')).filter(
                    hash=self.request.query_params.get('employee_id'),
                    is_active=self.request.query_params.get('status')).order_by('is_active', 'is_urgent', 'datetime')
                return queryset
            else:
                queryset = PortalAnnouncements.objects.annotate(hash=SHA1('uploaded_by_id'))\
                    .filter(hash=self.request.query_params.get('employee_id'))\
                    .order_by('is_active', 'is_urgent', 'datetime')
                return queryset