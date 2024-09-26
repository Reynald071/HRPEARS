from django.db import models
from django.utils import timezone

from backend.models import ExtensionName, Empprofile
from frontend.models import Province, City, Brgy


class GrievanceClassification(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'grievance_classification'


class GrievanceMedia(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'grievance_media'


class GrievanceQuery(models.Model):
    tracking_no = models.CharField(max_length=64, blank=True, null=True)
    client_fname = models.CharField(max_length=255, blank=True, null=True)
    client_mname = models.CharField(max_length=255, blank=True, null=True)
    client_lname = models.CharField(max_length=255, blank=True, null=True)
    client_ext = models.ForeignKey(ExtensionName, models.DO_NOTHING)
    client_contactnumber = models.CharField(max_length=255, blank=True, null=True)
    client_prov_id = models.CharField(max_length=255, blank=True, null=True)
    client_citymun_id = models.CharField(max_length=255, blank=True, null=True)
    client_brgy_id = models.CharField(max_length=255, blank=True, null=True)
    client_address = models.CharField(max_length=1024, blank=True, null=True)
    client_message = models.TextField(blank=True, null=True)
    date_received = models.DateTimeField(blank=True, null=True)
    gmedia = models.ForeignKey('GrievanceMedia', models.DO_NOTHING)
    datetime = models.DateTimeField(default=timezone.now)
    is_confidential = models.BooleanField(default=True)

    @property
    def get_latest_status(self):
        return GrievanceRecordsOfAction.objects.filter(gquery_id=self.id).order_by('-datetime', '-id').first()

    @property
    def get_province_name(self):
        return Province.objects.filter(id=self.client_prov_id).first().name

    def get_client_address(self):
        if self.client_prov_id and self.client_citymun_id and self.client_brgy_id:
            return "{}, {}, {}".format(Province.objects.filter(id=self.client_prov_id).first().name, City.objects.filter(code=self.client_citymun_id).first().name,
                                       Brgy.objects.filter(id=self.client_brgy_id).first().name)
        elif self.client_prov_id and self.client_citymun_id:
            return "{}, {}".format(Province.objects.filter(id=self.client_prov_id).first().name,
                                       City.objects.filter(code=self.client_citymun_id).first().name)
        else:
            return "{}".format(Province.objects.filter(id=self.client_prov_id).first().name)

    def get_client_name(self):
        return "{} {}. {}".format(self.client_fname, self.client_mname[:1], self.client_lname) if self.client_mname else "{} {}".format(self.client_fname, self.client_lname)

    class Meta:
        managed = False
        db_table = 'grievance_query'


class GrievanceRecordsOfAction(models.Model):
    gclassification = models.ForeignKey('GrievanceClassification', models.DO_NOTHING)
    gquery = models.ForeignKey('GrievanceQuery', models.DO_NOTHING)
    gstatus = models.ForeignKey('GrievanceStatus', models.DO_NOTHING)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    date_started = models.DateTimeField(blank=True, null=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    action_taken_or_answer_to_query = models.TextField(blank=True, null=True)
    datetime = models.DateTimeField(default=timezone.now)

    @property
    def get_attachments(self):
        return GrievanceRoaAttachments.objects.filter(roa_id=self.id)

    class Meta:
        managed = False
        db_table = 'grievance_records_of_action'


class GrievanceRoaAttachments(models.Model):
    attachment = models.FileField(upload_to="grievance/%Y/%m/%d")
    roa = models.ForeignKey('GrievanceRecordsOfAction', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'grievance_roa_attachments'


class GrievanceStatus(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField()
    need_emp = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'grievance_status'
