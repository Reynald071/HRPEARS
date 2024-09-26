from django.db import models
from django.utils import timezone

from backend.models import Empprofile



class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_type_id = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    firstname = models.CharField(max_length=60, blank=True, null=True)
    lastname = models.CharField(max_length=60, blank=True, null=True)
    middle = models.CharField(max_length=10, blank=True, null=True)
    contact = models.CharField(max_length=13, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    access = models.CharField(max_length=100, blank=True, null=True)
    date_reg = models.DateTimeField(blank=True, null=True)
    flag = models.IntegerField(blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class EmployeeInfo(models.Model):
    employee_id = models.AutoField(primary_key=True)
    personal_id = models.IntegerField(blank=True, null=True)
    position_id = models.IntegerField(blank=True, null=True)
    project_id = models.IntegerField(blank=True, null=True)
    id_number = models.CharField(max_length=8, blank=True, null=True)
    item_number = models.CharField(max_length=150, blank=True, null=True)
    account_number = models.CharField(max_length=11, blank=True, null=True)
    lastname = models.CharField(max_length=60, blank=True, null=True)
    firstname = models.CharField(max_length=60, blank=True, null=True)
    middlename = models.CharField(max_length=60, blank=True, null=True)
    extention = models.CharField(max_length=3, blank=True, null=True)
    civil_status = models.CharField(max_length=10, blank=True, null=True)
    contact_no = models.CharField(max_length=20, blank=True, null=True)
    step_increment = models.CharField(max_length=10, blank=True, null=True)
    salary_grade = models.CharField(max_length=10, blank=True, null=True)
    salary_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fund_charge = models.CharField(max_length=100, blank=True, null=True)
    date_registered = models.DateField(blank=True, null=True)
    date_appointed = models.DateField(blank=True, null=True)
    date_effectivity = models.DateField(blank=True, null=True)
    employ_status = models.IntegerField(blank=True, null=True)
    is_remarks = models.CharField(max_length=50, blank=True, null=True)
    is_status = models.CharField(max_length=50, blank=True, null=True)
    is_note = models.TextField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    is_primary = models.IntegerField(blank=True, null=True)
    section = models.CharField(max_length=100, blank=True, null=True)
    area_level = models.CharField(max_length=100, blank=True, null=True)
    payroll_incharge_id = models.CharField(max_length=50, blank=True, null=True)
    is_dempcc = models.IntegerField(blank=True, null=True)
    uid = models.ForeignKey(Users, models.DO_NOTHING)
    date_entry = models.DateField(blank=True, null=True)
    projectid_cures = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee_info'


class LibSupplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=500)
    category = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100)
    philgeps = models.CharField(max_length=100, blank=True, null=True)
    tin = models.CharField(max_length=100, blank=True, null=True)
    mobile = models.CharField(max_length=100, blank=True, null=True)
    telephone = models.CharField(max_length=100, blank=True, null=True)
    owner = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    account_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    date_added = models.DateTimeField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_supplier'


class LibOthersPayee(models.Model):
    others_payee_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lib_others_payee'


class Config(models.Model):
    config_id = models.AutoField(primary_key=True)
    field_handler = models.CharField(db_column='_handler', max_length=60, blank=True,
                                     null=True)  # Field renamed because it started with '_'.
    field_value = models.CharField(db_column='_value', max_length=250, blank=True,
                                   null=True)  # Field renamed because it started with '_'.

    class Meta:
        managed = False
        db_table = '_config'


class Transactions(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    dv_no = models.CharField(unique=True, max_length=12, blank=True, null=True)
    dv_date = models.DateField(default=timezone.now)
    payee = models.CharField(max_length=200, blank=True, null=True)
    modepayment = models.TextField(blank=True, null=True)
    amt_certified = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amt_journal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amt_budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    approval_date = models.CharField(max_length=25, default=None)
    remarks = models.CharField(max_length=50, blank=True, null=True)
    recon = models.IntegerField(blank=True, null=True)
    alobs_no = models.CharField(max_length=12, blank=True, null=True)
    alobs_item = models.SmallIntegerField(blank=True, null=True)
    prov_id = models.IntegerField(blank=True, null=True)
    mun_id = models.IntegerField(blank=True, null=True)
    brgy_id = models.IntegerField(blank=True, null=True)
    userlog = models.CharField(max_length=20, blank=True, null=True)
    scaned_voucher = models.CharField(max_length=25, blank=True, null=True)
    submit_coa = models.DateField(blank=True, null=True)
    accountable = models.CharField(max_length=90, blank=True, null=True)
    projectsrc_id = models.IntegerField(blank=True, null=True)
    payee_table_name = models.CharField(max_length=50, blank=True, null=True)
    payee_id = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions'


class TransPayeename(models.Model):
    trans_payee_id = models.AutoField(primary_key=True)
    transaction = models.ForeignKey(Transactions, models.DO_NOTHING, unique=True)
    dv_no = models.CharField(max_length=12, blank=True, null=True)
    dv_yr = models.IntegerField(blank=True, null=True)
    dv_month = models.IntegerField(blank=True, null=True)
    dv_sequence = models.IntegerField(blank=True, null=True)
    check_id = models.IntegerField(blank=True, null=True)
    is_cancel = models.IntegerField(blank=True, null=True)
    is_multiple = models.IntegerField(blank=True, null=True)
    validate_budget = models.IntegerField(blank=True, null=True)
    check_issued = models.DateField(blank=True, null=True)
    check_released = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trans_payeename'


class ProjectSrc(models.Model):
    projectsrc_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    cluster_id = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    is_primary = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'project_src'


class InfimosHistoryTracking(models.Model):
    dv_no = models.CharField(max_length=100, blank=True, null=True)
    payee = models.CharField(max_length=200, blank=True, null=True)
    projectsrc_id = models.IntegerField(blank=True, null=True)
    empstatus = models.CharField(max_length=100, blank=True, null=True)
    project = models.CharField(max_length=100, blank=True, null=True)
    purpose = models.CharField(max_length=100, blank=True, null=True)
    filter_dates = models.CharField(max_length=150, blank=True, null=True)
    date_from = models.CharField(max_length=100, blank=True, null=True)
    date_to = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    amount_certified = models.FloatField(blank=True, null=True)
    accountable = models.CharField(max_length=100, blank=True, null=True)
    emp = models.ForeignKey(Empprofile, models.DO_NOTHING)

    def get_payroll_latest_status(self):
        from backend.pas.payroll.models import PayrollTimelineWorkFlow
        payroll = PayrollTimelineWorkFlow.objects.filter(dv_no=self.dv_no).order_by('-id')
        if payroll:
            return {
                'assignee': payroll.first().assignee.pi.user.get_fullname,
                'status': payroll.first().timeline.description
            }
        else:
            return {
                'assignee': '',
                'status': ''
            }

    def get_payroll_type(self):
        from backend.pas.payroll.models import PayrollTimelineWorkFlow
        payroll = PayrollTimelineWorkFlow.objects.filter(dv_no=self.dv_no, timeline_id=1).first()
        if payroll:
            return payroll.type
        else:
            return None

    class Meta:
        managed = False
        db_table = 'infimos_history_tracking'

