from django.db import models
from django.utils import timezone

from backend.models import Empprofile, Division


class TransmittalOld(models.Model):
    tracking_id = models.AutoField(primary_key=True)
    id_number = models.CharField(max_length=20, blank=True, null=True)
    emp_status = models.IntegerField(blank=True, null=True)
    document_name = models.CharField(max_length=200, blank=True, null=True)
    transaction_type = models.CharField(max_length=100, blank=True, null=True)
    date_received = models.DateField(blank=True, null=True)
    date_document = models.CharField(max_length=300, blank=True, null=True)
    forwarded_to = models.CharField(max_length=200, blank=True, null=True)
    details = models.CharField(max_length=500, blank=True, null=True)
    date_added = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transmittal_old'


class TransmittalNew(models.Model):
    tracking_no = models.CharField(max_length=100, blank=True, null=True)
    document_name = models.ForeignKey('TransmittalType', models.DO_NOTHING)
    document_date = models.DateField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)

    @property
    def get_latest_status(self):
        return TransmittalTransaction.objects.filter(trans_id=self.id).order_by('-id').first()

    class Meta:
        managed = False
        db_table = 'transmittal_new'


class TransmittalTransaction(models.Model):
    trans = models.ForeignKey('TransmittalNew', on_delete=models.CASCADE)
    status = models.IntegerField(blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    forwarded_to = models.ForeignKey(Division, models.DO_NOTHING, blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    date_approved = models.DateTimeField(blank=True, null=True)

    @property
    def get_status(self):
        if self.status == 0:
            return "<span class='label label-default'>Incoming</span>"
        elif self.status == 1:
            return "<span class='label label-primary'>Outgoing</span>"
        elif self.status == 2:
            return "<span class='label label-success'>Approved</span>"
        elif self.status == 3:
            return "<span class='label label-danger'>Disapproved</span>"
        elif self.status == 4:
            return "<span class='label label-warning'>Returned</span>"

    class Meta:
        managed = False
        db_table = 'transmittal_transaction'


class TransmittalType(models.Model):
    name = models.CharField(max_length=1024, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(Empprofile, models.DO_NOTHING)

    class Meta:
        db_table = 'transmittal_type'