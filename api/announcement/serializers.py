from rest_framework import serializers

from frontend.models import PortalAnnouncements


class AnnouncementSerializers(serializers.ModelSerializer):
    published_by = serializers.SerializerMethodField()
    datetime = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)
    is_active = serializers.IntegerField()

    class Meta:
        model = PortalAnnouncements
        fields = ['id', 'title', 'caption', 'published_by', 'datetime', 'is_active', 'is_urgent',
                  'announcement_type', 'uploaded_by_id']

    @staticmethod
    def get_published_by(obj):
        return obj.uploaded_by.pi.user.get_fullname