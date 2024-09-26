import os
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from backend.models import Empprofile, AuthUser

class CovidAssistance(models.Model):
    emp = models.ForeignKey(Empprofile, on_delete=models.CASCADE)
    caseofemp = models.CharField(max_length=50, blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    provision = models.CharField(max_length=50, blank=True, null=True, default="0")

    class Meta:
        db_table = 'hrws_covid_assistance'


class vest_db(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING, to_field='id_number')
    no_of_days = models.CharField(max_length=50, blank=True, null=True)
    date_borrowed = models.DateTimeField(blank=True, null=True)
    date_returned = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True, default="0")

    class Meta:
        db_table = 'hrws_vestdb'


class Sweap_membership(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    encodedby = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    dateadded = models.DateTimeField(blank=True, null=True, default=timezone.now)
    attachment = models.FileField(upload_to='sweap_attachment/', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'hrws_sweap_membership'

class Sweap_mem_committee(models.Model):
    mem = models.ForeignKey('Sweap_membership', models.DO_NOTHING)
    committee = models.ForeignKey('Committee', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hrws_sweap_mem_committee'

class Sweap_mem_benes(models.Model):
    mem = models.ForeignKey('Sweap_membership', models.DO_NOTHING)
    full_name = models.CharField(max_length=50, blank=True, null=True)
    relationship = models.CharField(max_length=50, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hrws_sweap_mem_benes'

class type_of_assistance(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    status = models.BooleanField()
    uploadedby_id = models.ForeignKey('AuthUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'hrws_type_of_assistance'


class Committee(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    status = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'hrws_committee'


class activity_db(models.Model):
    activity = models.CharField(max_length=50, blank=True, null=True)
    user_id = models.CharField(max_length=11, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hrws_activity'


class item_db(models.Model):
    item = models.CharField(max_length=50, blank=True, null=True)
    activity = models.ForeignKey(activity_db, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    inventory = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'hrws_activity_item'


class intervention(models.Model):
    emp = models.ForeignKey(Empprofile, on_delete=models.CASCADE)
    date = models.DateTimeField(blank=True, null=True)
    activity = models.ForeignKey(activity_db, on_delete=models.CASCADE)
    item = models.ForeignKey(item_db, on_delete=models.CASCADE)
    total = models.CharField(max_length=11, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'hrws_intervention'


class sweap_assistance(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING, to_field='id_number')
    typeofassistant = models.CharField(max_length=255, blank=True, null=True)
    particular = models.CharField(max_length=255, blank=True, null=True)
    amount_excess = models.CharField(max_length=255, blank=True, null=True)
    amount_extended = models.CharField(max_length=255, blank=True, null=True)
    relationship = models.CharField(max_length=255, blank=True, null=True)
    share_contrib = models.IntegerField(blank=True, default="0")
    period_applied = models.DateTimeField(blank=True, null=True)
    entry = models.IntegerField(blank=True,default="0")

    class Meta:
        managed = False
        db_table = 'hrws_sweap_assistance'


class sweap_gratuity(models.Model):
    emp = models.ForeignKey(Empprofile, on_delete=models.CASCADE)
    type_of_assistance = models.CharField(max_length=50, blank=True, null=True)
    date_emp_start = models.DateTimeField(blank=True, null=True)
    date_emp_end = models.DateTimeField(blank=True, null=True)
    emp_yearinservice = models.CharField(max_length=255, blank=True, null=True)
    share_contrib = models.CharField(max_length=255,blank=True, null=True)
    amount_recieved = models.IntegerField(blank=True, default="0")

    class Meta:
        managed = False
        db_table = 'hrws_sweap_gratuity'


class grievance_db(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.CharField(max_length=255, blank=True, null=True)
    files = models.FileField(blank=True)
    class Meta:
        managed = False
        db_table = 'hrws_grievance_db'


# THIS IS FOR EMPLOYEEE ASSISTANCE #
class type_of_request(models.Model):
    category = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hrws_type_of_request'


class category_request(models.Model):
    toa = models.ForeignKey(type_of_request, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hrws_category_of_request'


class doucument_attached(models.Model):
    category = models.ForeignKey(category_request, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hrws_document_attached'


class employee_assistance_sop(models.Model):
    emp = models.ForeignKey(Empprofile, on_delete=models.CASCADE)
    rq_date = models.DateTimeField(blank=True, null=True)
    informant = models.CharField(max_length=255, blank=True, null=True)
    informant_contact = models.CharField(max_length=255, blank=True, null=True)
    brief_request = models.CharField(max_length=255, blank=True, null=True)
    cr_financial = models.ForeignKey(category_request, related_name="cr_financial", on_delete=models.CASCADE)
    cr_fa_others = models.CharField(max_length=255,blank=True,null=True)
    cr_financial_others = models.CharField(max_length=255, blank=True, null=True)
    cr_mental = models.ForeignKey(category_request, related_name="cr_mental", on_delete=models.CASCADE)
    cr_other = models.ForeignKey(category_request, on_delete=models.CASCADE)
    docx_valid_id = models.CharField(max_length=255, blank=True, null=True)
    docx_barangay_cert = models.CharField(max_length=255, blank=True, null=True)
    docx_case_study = models.CharField(max_length=255, blank=True, null=True)
    docx_clinical_abstract = models.CharField(max_length=255, blank=True, null=True)
    docx_host_bill = models.CharField(max_length=255, blank=True, null=True)
    docx_prescription = models.CharField(max_length=255, blank=True, null=True)
    docx_lab_request = models.CharField(max_length=255, blank=True, null=True)
    docx_showing = models.CharField(max_length=255, blank=True, null=True)
    docx_police_blotter = models.CharField(max_length=255, blank=True, null=True)
    docx_funeral_contract = models.CharField(max_length=255, blank=True, null=True)
    docx_death_cert = models.CharField(max_length=255, blank=True, null=True)
    docx_permit_to_transfer = models.CharField(max_length=255, blank=True, null=True)
    memo_voluntaryContrib = models.CharField(max_length=255, blank=True, null=True)
    endorsement_letter = models.CharField(max_length=255, blank=True, null=True)
    result_of_interview = models.CharField(max_length=255, blank=True, null=True)
    other_docx = models.CharField(max_length=255, blank=True,null=True)
    action_provided = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    officer_in_charge = models.CharField(max_length=255, blank=True, null=True)
    date_approved = models.CharField(max_length=255,blank=True, null=True)
    unit_quantity = models.CharField(max_length=255,blank=True,null=True)
    date_received = models.CharField(max_length=255,blank=True, null=True)
    date_endorse_cis = models.CharField(max_length=255,blank=True, null=True)
    dateadded = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'hrws_emp_assistance'


class emp_assistance_attachment(models.Model):
    emp_assistance = models.ForeignKey(employee_assistance_sop, on_delete=models.CASCADE)
    attachment_data = models.FileField(blank=True, upload_to='CIS/')
    class Meta:
        managed = False
        db_table = 'hrws_emp_assistance_attachment'


@receiver(models.signals.post_delete, sender=emp_assistance_attachment)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.attachment_data:
        if os.path.isfile(instance.attachment_data.path):
            os.remove(instance.attachment_data.path)


class commorbid(models.Model):
    Commorbidity = models.CharField(max_length=255,blank=True,null=True)
    class Meta:
        managed = False
        db_table = 'hrws_commorbid'

class health_profile(models.Model):
    emp = models.ForeignKey(Empprofile, on_delete=models.CASCADE)
    category = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hrws_health_profile'

class health_profile_data(models.Model):
    health_profile = models.ForeignKey(health_profile, on_delete=models.CASCADE)
    emp_commorbid = models.ForeignKey(commorbid, on_delete=models.CASCADE)
    systolic_bs = models.CharField(max_length=255, blank=True, null=True)
    diastolic_bs = models.CharField(max_length=255, blank=True, null=True)
    bs = models.CharField(max_length=255, blank=True, null=True)
    oxemeter = models.CharField(max_length=255, blank=True, null=True)
    result = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    date = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hrws_healthprof_data'

class incident_data_db(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'hrws_incidents'

class incidentreport_db(models.Model):
    emp = models.ForeignKey(Empprofile, on_delete=models.CASCADE)
    category = models.ForeignKey(incident_data_db, on_delete=models.CASCADE)
    date = models.DateTimeField(blank=True, null=True)
    remarks = models.CharField(max_length=50, blank=True, null=True, default="0")

    class Meta:
        db_table = 'hrws_incidentreport'

class ir_attachment_db(models.Model):
    incident_report = models.ForeignKey(employee_assistance_sop, on_delete=models.CASCADE)
    attachment_data = models.FileField(blank=True,upload_to='IRDB/')
    class Meta:
        managed = False
        db_table = 'hrws_irdb_attachment'
