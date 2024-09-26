import os

from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.contrib import admin

from backend.models import Empprofile, AuthUser, Division, Section


class Docs201Files(models.Model):
    number_201_type = models.ForeignKey('Docs201Type', models.DO_NOTHING, db_column='201_type_id', blank=True,
                                        null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING, related_name='emp')
    file = models.FileField(upload_to='documents/%Y/%m')
    year = models.IntegerField(blank=True, null=True)
    upload_by = models.ForeignKey(Empprofile, models.DO_NOTHING, related_name='upload_by')
    name = models.TextField(blank=True, null=True)
    uploaded_on = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'docs_201_files'


class Docs201Type(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    class Meta:
        verbose_name = '201 Document Type'
        managed = False
        db_table = 'docs_201_type'


class DocsIssuancesFiles(models.Model):
    issuances_type = models.ForeignKey('DocsIssuancesType', models.DO_NOTHING)
    file = models.FileField(upload_to='documents/%Y/%m')
    year = models.IntegerField(blank=True, null=True)
    upload_by_id = models.IntegerField(blank=True, null=True)
    date_time = models.DateTimeField(default=timezone.now)

    @property
    def get_filename(self):
        return os.path.basename(self.file.name)

    class Meta:
        managed = False
        db_table = 'docs_issuances_files'


class DocsIssuancesType(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)

    @admin.display(boolean=True, description='Status')
    def display_status(self):
        return self.status == 1

    class Meta:
        verbose_name = 'Issuances Type'
        managed = False
        db_table = 'docs_issuances_type'


@receiver(models.signals.post_delete, sender=Docs201Files)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=Docs201Files)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Docs201Files.objects.get(pk=instance.pk).file
    except Docs201Files.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


@receiver(models.signals.post_delete, sender=DocsIssuancesFiles)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class DtsDoctypeClass(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    abbreviation = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dts_doctype_class'


class DtsDoctype(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField()
    upload_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    code = models.CharField(max_length=255)
    description = models.CharField(max_length=1024)
    doctype_class = models.ForeignKey('DtsDoctypeClass', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'dts_doctype'


class DtsDocorigin(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dts_docorigin'


class DtsDocument(models.Model):
    docorigin = models.ForeignKey('DtsDocorigin', models.DO_NOTHING)
    sender = models.CharField(max_length=255, blank=True, null=True, default=None)
    subject = models.TextField(blank=True, null=True)
    purpose = models.TextField(blank=True, null=True, default=None)
    document_date = models.DateField(blank=True, null=True, default=None)
    document_deadline = models.DateField(blank=True, null=True, default=None)
    date_saved = models.DateTimeField(default=timezone.now)
    other_info = models.TextField(blank=True, null=True, default=None)
    tracking_no = models.CharField(max_length=255, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    is_blank = models.BooleanField(default=False)
    generated_drn = models.CharField(max_length=100, null=True, default=None)
    drn = models.CharField(max_length=100, null=True, default=None)
    creator = models.ForeignKey(Empprofile, models.DO_NOTHING)
    doctype = models.ForeignKey('DtsDoctype', models.DO_NOTHING, blank=True, null=True)
    extracted_text = models.TextField(blank=True, null=True)

    @property
    def created_by(self):
        return DtsTransaction.objects.filter(action=0, document_id=self.id).first()

    @property
    def get_latest_status(self):
        return DtsTransaction.objects.filter(document_id=self.id, action__in=[1, 2, 3]).order_by('-date_saved',
                                                                                                 '-id').first()

    @property
    def has_attachment(self):
        transactions = DtsTransaction.objects.filter(document_id=self.id).values_list('id', flat=True)
        has_attachment = True if DtsAttachment.objects.filter(transaction_id__in=transactions) else False
        return has_attachment

    @property
    def has_attachment_and_subject(self):
        return '{}{}'.format('<i class="fas fa-paperclip"></i>&emsp;', self.subject)\
            if self.has_attachment else self.subject

    @property
    def get_my_drn(self):
        d = DtsDrn.objects.filter(document=self).first()
        return d if d else None

    @property
    def get_drn(self):
        drn = DtsDrn.objects.filter(document=self).first()
        if drn:
            new_drn_series_number = int(drn.series)
            series_number = str(new_drn_series_number)
            filled_series_number = series_number.zfill(6)
            generated_drn = '{}-{}-{}-{}-{}-{}'.format('{}-{}'.format(drn.division.div_acronym,
                                                                      drn.section.sec_acronym) if
                                                       drn.section and drn.section.sec_acronym
                                                       else drn.division.div_acronym,
                                                       drn.doctype.code, str(self.date_saved.year)[-2:],
                                                       self.date_saved.month, filled_series_number,
                                                       drn.category.code)

            if not drn.document.generated_drn:
                DtsDocument.objects.filter(id=self.id).update(generated_drn=generated_drn)

            return generated_drn
        else:
            return self.drn if self.drn else self.tracking_no

    class Meta:
        managed = False
        db_table = 'dts_document'


class DtsDrn(models.Model):
    document = models.ForeignKey('DtsDocument', models.DO_NOTHING)
    series = models.IntegerField(blank=True, null=True)
    category = models.ForeignKey('DtsCategory', models.DO_NOTHING)
    doctype = models.ForeignKey('DtsDoctype', models.DO_NOTHING)
    division = models.ForeignKey(Division, models.DO_NOTHING)
    section = models.ForeignKey(Section, null=True, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'dts_drn'


class DtsTransaction(models.Model):
    action = models.IntegerField(blank=True, null=True)
    trans_from = models.ForeignKey(Empprofile, models.DO_NOTHING, related_name='sender')
    trans_to = models.ForeignKey(Empprofile, models.DO_NOTHING, related_name='receiver')
    in_behalf_of = models.ForeignKey(Empprofile, models.DO_NOTHING,
                                     related_name='supposed_to_be_receiver', blank=True, null=True)
    trans_datestarted = models.DateTimeField(blank=True, null=True)
    trans_datecompleted = models.DateTimeField(blank=True, null=True)
    action_taken = models.TextField(blank=True, null=True)
    date_saved = models.DateTimeField(default=timezone.now)
    document = models.ForeignKey('DtsDocument', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'dts_transaction'


class DtsAttachment(models.Model):
    transaction = models.ForeignKey('DtsTransaction', models.DO_NOTHING)
    attachment = models.FileField(upload_to='document_tracking/', blank=True, null=True)
    uploaded_by = models.ForeignKey(Empprofile, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'dts_attachment'


class DtsDivisionCc(models.Model):
    document = models.ForeignKey('DtsDocument', models.DO_NOTHING)
    division = models.ForeignKey(Division, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'dts_division_cc'


class DtsCategory(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'dts_category'
