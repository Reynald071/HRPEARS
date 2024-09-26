from django.db import models
from django.contrib import admin
from backend.models import PositionVacancy
from frontend.models import Civilstatus, Province, City, Brgy


class AppStatus(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        verbose_name = "Application Status"
        verbose_name_plural = "Application Status"
        db_table = 'app_status'


class JobApplication(models.Model):
    tracking_no = models.CharField(max_length=50, blank=True, null=True)
    vacancy = models.ForeignKey(PositionVacancy, models.DO_NOTHING)
    date_of_app = models.DateTimeField(blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    extension = models.CharField(max_length=50, blank=True, null=True)
    sex = models.IntegerField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    civil_status = models.ForeignKey(Civilstatus, models.DO_NOTHING)
    email = models.CharField(max_length=255, blank=True, null=True)
    contact_no = models.CharField(max_length=11, blank=True, null=True)
    course = models.CharField(max_length=255, blank=True, null=True)
    work_exp = models.CharField(max_length=500, blank=True, null=True)
    province = models.ForeignKey(Province, models.DO_NOTHING)
    city = models.ForeignKey(City, models.DO_NOTHING)
    brgy = models.ForeignKey(Brgy, models.DO_NOTHING)
    zip_code = models.CharField(max_length=50, blank=True, null=True)
    street = models.CharField(max_length=500, blank=True, null=True)
    tor = models.FileField(upload_to='applications/tor/%Y/%m', blank=True, null=True)
    app_letter = models.FileField(upload_to='applications/app-letter/%Y/%m', blank=True, null=True)
    pds = models.FileField(upload_to='applications/pds/%Y/%m', blank=True, null=True)
    we_sheet = models.FileField(upload_to='applications/we-sheet/%Y/%m', blank=True, null=True)
    cert_training = models.FileField(upload_to='applications/cert-training/%Y/%m', blank=True, null=True)
    cert_employment = models.FileField(upload_to='applications/cert-employment/%Y/%m', blank=True, null=True)
    ipcr = models.FileField(upload_to='applications/ipcr/%Y/%m', blank=True, null=True)
    app_status = models.ForeignKey(AppStatus, models.DO_NOTHING, default=1)
    is_rejected = models.IntegerField(blank=True, default=0)
    remarks = models.TextField(blank=True, null=True)

    @property
    def get_fullname(self):
        return "{} {} {}{}".format(
            self.first_name.title(), self.middle_name[:1] + "." if self.middle_name else '',
            self.last_name.title(), ' ' + self.extension if self.extension else ''
        )

    class Meta:
        managed = False
        db_table = 'job_applications'


class AppEligibility(models.Model):
    app = models.ForeignKey(JobApplication, models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    rating = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    place = models.CharField(max_length=500, blank=True, null=True)
    license_number = models.CharField(max_length=500, blank=True, null=True)
    license_dov = models.DateField(blank=True, null=True)
    attachment = models.FileField(upload_to='applications/eligibility/%Y/%m', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'app_eligibility'

