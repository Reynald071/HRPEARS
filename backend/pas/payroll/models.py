import os
from django.db import models
from django.dispatch import receiver
from django.utils import timezone

from backend.models import Empprofile, InfimosPurpose, PayrollIncharge


class PayrollEmployeeGroup(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    upload_by_id = models.IntegerField(blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'payroll_employee_group'


class PayrollEmployees(models.Model):
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    upload_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    empgroup = models.ForeignKey(PayrollEmployeeGroup, models.DO_NOTHING)
    is_per_day = models.BooleanField()

    class Meta:
        db_table = 'payroll_employees'


class PayrollColumnGroup(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    created_by_id = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'payroll_column_group'


class PayrollColumnType(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    upload_by_id = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'payroll_column_type'


class PayrollColumns(models.Model):
    attribute = models.CharField(max_length=255, blank=True, null=True)
    upload_by_id = models.IntegerField(blank=True, null=True)
    column_type = models.ForeignKey(PayrollColumnType, models.DO_NOTHING)
    is_active = models.BooleanField(blank=True, null=True)
    order = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    is_computed = models.BooleanField(blank=True, null=True)
    is_hidden = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payroll_columns'


class PayrollGroup(models.Model):
    column_group = models.ForeignKey(PayrollColumnGroup, models.DO_NOTHING)
    column = models.ForeignKey(PayrollColumns, models.DO_NOTHING)

    class Meta:
        db_table = 'payroll_group'


class PayrollOrder(models.Model):
    purpose = models.ForeignKey(InfimosPurpose, models.DO_NOTHING)
    period_from = models.DateField(blank=True, null=True)
    period_to = models.DateField(blank=True, null=True)
    upload_by_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    payroll_status = models.IntegerField(blank=True, null=True)
    empstatus = models.ForeignKey('PayrollEmployeeGroup', models.DO_NOTHING)
    auto_calculate = models.BooleanField()

    class Meta:
        db_table = 'payroll_order'


class PayrollTransaction(models.Model):
    payroll = models.ForeignKey(PayrollOrder, models.DO_NOTHING)
    column = models.ForeignKey(PayrollColumns, models.DO_NOTHING)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)
    value = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payroll_transaction'


class PayrollTemplate(models.Model):
    payroll = models.ForeignKey(PayrollOrder, models.DO_NOTHING)
    column = models.ForeignKey(PayrollColumns, models.DO_NOTHING)

    class Meta:
        db_table = 'payroll_template'


class PayrollTaxComputation(models.Model):
    id = models.IntegerField(primary_key=True)
    four_seven = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    five_zero = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    five_two = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    five_three = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    five_four = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    five_six = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    five_seven = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    five_eight = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    six_three = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    quarter = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    emp_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payroll_tax_computation'


class PayrollMovs(models.Model):
    mov_type = models.ForeignKey('PayrollMovsType', models.DO_NOTHING)
    year = models.IntegerField(blank=True, null=True)
    file = models.FileField(upload_to="payroll/%Y/%m")
    uploaded_by = models.ForeignKey(Empprofile, models.DO_NOTHING)
    date_uploaded = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'payroll_movs'


@receiver(models.signals.post_delete, sender=PayrollMovs)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


class PayrollMovsType(models.Model):
    name = models.CharField(max_length=1024, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    type = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'payroll_movs_type'


class PasEmpPayrollIncharge(models.Model):
    payroll_incharge = models.ForeignKey(PayrollIncharge, models.DO_NOTHING)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pas_emp_payroll_incharge'


class PayrollTimeline(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payroll_timeline'


class PayrollTimelineWorkFlow(models.Model):
    timeline = models.ForeignKey('PayrollTimeline', models.DO_NOTHING)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    assignee = models.ForeignKey(Empprofile, models.DO_NOTHING)
    date_transmitted = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    date_returned = models.DateTimeField(blank=True, null=True)
    dv_no = models.CharField(max_length=255, blank=True, null=True)
    is_lock = models.IntegerField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    date_received = models.DateTimeField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)

    def get_forward_status(self):
        check = PayrollTimelineWorkFlow.objects.filter(timeline_id=self.timeline_id + 1, dv_no=self.dv_no)

        if check:
            return check.first()

    class Meta:
        managed = False
        db_table = 'payroll_timeline_workflow'


class PayrollTimelineWorkflowComments(models.Model):
    dv_no = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    date_comment = models.TextField(blank=True, null=True)
    commentby = models.ForeignKey(Empprofile, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'payroll_timeline_workflow_comments'


class PayrollWorkflowTemplate(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payroll_workflow_template'


class PayrollWorkflowTemplateData(models.Model):
    pw_id = models.IntegerField(blank=True, null=True)
    column = models.ForeignKey('PayrollColumns', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'payroll_workflow_template_data'


class PayrollWorkflowDetails(models.Model):
    dv_no = models.CharField(max_length=255, blank=True, null=True)
    column = models.ForeignKey('PayrollColumns', models.DO_NOTHING)
    value = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payroll_workflow_details'