from django.db import models
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from backend.models import Empprofile
from backend.pas.transmittal.models import TransmittalType


def generate_token(value):
    data = urlsafe_base64_encode(force_bytes(value))
    return data


class TrackerPackageCC(models.Model):
    package = models.ForeignKey('TrackerPackage', on_delete=models.CASCADE)
    cc = models.ForeignKey(Empprofile, models.DO_NOTHING)
    datetime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tracker_package_cc'


class TrackerPackageItemHistory(models.Model):
    package = models.ForeignKey('TrackerPackage', on_delete=models.CASCADE)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    forwarded = models.ForeignKey(Empprofile, models.DO_NOTHING, related_name='forwarded')
    status = models.ForeignKey('TrackerStatus', models.DO_NOTHING)
    datetime = models.DateTimeField(default=timezone.now)
    notes = models.CharField(max_length=1024, blank=True, null=True)
    viewed = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tracker_package_item_history'


class TrackerPackage(models.Model):
    tracking_no = models.CharField(max_length=255, blank=True, null=True)
    doctype = models.ForeignKey(TransmittalType, models.DO_NOTHING)
    date_created = models.DateTimeField(default=timezone.now)
    createdby = models.ForeignKey(Empprofile, models.DO_NOTHING)
    latest_status = models.ForeignKey('TrackerStatus', models.DO_NOTHING)
    latest_docholder = models.ForeignKey(Empprofile, models.DO_NOTHING, related_name='latest_docholder')
    remarks = models.CharField(max_length=255, blank=True, null=True)

    @property
    def convert_crypto(self):
        return generate_token(self.id)

    @property
    def get_latest_status(self):
        status = TrackerPackageItemHistory.objects.filter(package_id=self.id).order_by('-datetime')

        if status:
            return status.first()

    class Meta:
        managed = False
        db_table = 'tracker_package'


class TrackerPackageItem(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    document_date = models.DateField(blank=True, null=True)
    other_info = models.CharField(max_length=1024, blank=True, null=True)
    leave_tracking_no = models.CharField(max_length=255, blank=True, null=True)
    package = models.ForeignKey('TrackerPackage', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'tracker_package_item'


class TrackerStatus(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tracker_status'


class TrackerDraft(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    tracking_number = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(Empprofile, models.DO_NOTHING, related_name='tracker_created_by')
    type = models.IntegerField(blank=True, null=True)

    @property
    def get_details(self):
        from backend.libraries.leave.models import LeaveApplication
        leave = LeaveApplication.objects.filter(tracking_no=self.tracking_number)

        if leave:
            return [leave.first().leavesubtype.name, leave.first().get_inclusive()]
        else:
            from backend.libraries.leave.models import CTDORequests
            ctdo = CTDORequests.objects.filter(tracking_no=self.tracking_number)

            if ctdo:
                return ['CTDO', ctdo.first().get_inclusive()]
            else:
                return ['CTDO', None]

    class Meta:
        managed = False
        db_table = 'tracker_draft'


class TrackerAnnouncements(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    dates = models.CharField(max_length=1024, blank=True, null=True)
    details = models.CharField(max_length=1024, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    created_by = models.ForeignKey(Empprofile, models.DO_NOTHING, related_name='tracker_announcement_created_by')
    date_created = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tracker_announcements'


class TrackerSMSType(models.Model):
    type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tracker_sms_type'