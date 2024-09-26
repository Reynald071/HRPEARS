import re
from datetime import datetime, date, timedelta, time
from time import mktime
import urllib

from cryptography.fernet import Fernet
from django import template
from django.db.models import Q, F, Count
from django.utils.dateparse import parse_date
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from backend.awards.models import Badges, Nominees
from backend.convocation.models import ConvocationAttendance
from backend.documents.models import DtsTransaction, DtsDivisionCc
from backend.ipcr.models import IPC_Rating, IPC_AdjectivalRating
from backend.libraries.grievance.models import GrievanceRecordsOfAction
from backend.libraries.leave.models import LeavePermissions, LeaveApplication, CTDOUtilization
from backend.models import Rcompliance, Empstatus, Empprofile, AuthUserUserPermissions, Designation, WfhTime, Position, \
    PayrollPayeeGroupEmployee, PayrollEmployee, PayrollColumnGroupColumns, PayrollColumn, PayrollMainColumns, Section, \
    DirectoryDetails, DirectoryContact, DirectoryDetailType, DtrPin, DRNTracker
from backend.pas.accomplishment.models import DTRAssignee
from backend.pas.document_tracking.models import DocsTrackingStatus
from backend.pas.payroll.models import PasEmpPayrollIncharge
from backend.pas.service_record.models import PasServiceRecordData
from backend.pas.transmittal.models import TransmittalTransaction
from frontend.models import Ritopeople, Bloodtype, Brgy, City, Province, Locatorslip, Outpassdetails, Workhistory, \
    PasAccomplishmentOutputs, Degree, Organization, Honors, School, Trainingtitle, Eligibility, Hobbies, Nonacad, \
    TravelOrder, Address, PortalAnnouncements, PortalConfiguration, DeskServicesTransaction, DeskServicesAttachment, \
    Additional, Civilservice, Rito, Workexperience, Deductionnumbers
from dateutil import relativedelta

from frontend.pas.accomplishment.models import Dtr

register = template.Library()


@register.filter()
def check_permission(user, permission):
    if user.user_permissions.filter(codename=permission).exists():
        return True
    return False


@register.simple_tag
def generate_token(value):
    data = urlsafe_base64_encode(force_bytes(value))
    return data


@register.simple_tag
def force_token_decryption(value):
    data = force_str(urlsafe_base64_decode(value))
    return data


@register.simple_tag
def convert_string_to_crypto(value):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    crypto = fernet.encrypt(value.encode()).decode('utf-8')

    return crypto


@register.simple_tag
def convert_crypto_to_string(value):
    key = Fernet.generate_key()
    fernet = Fernet(key)
    original = fernet.decrypt(value).decode()

    return original


@register.simple_tag
def ritopeople(id):
    people = Ritopeople.objects.filter(detail_id=id)
    return people


@register.simple_tag
def getcompliance(user_id, req_id):
    compliance = Rcompliance.objects.filter(Q(user_id=user_id) & Q(rreq_id=req_id)).first()
    return compliance


@register.simple_tag
def getbloodtype(pk):
    bt = Bloodtype.objects.filter(id=pk).first()
    return bt


@register.simple_tag
def getbrgy(pk):
    brgy = Brgy.objects.filter(id=pk).first()
    return brgy


@register.simple_tag
def getcity(pk):
    city = City.objects.filter(code=pk).first()
    return city


@register.simple_tag
def getprovince(pk):
    prov = Province.objects.filter(id=pk).first()
    return prov


@register.simple_tag
def getrange(max, min):
    total = max - min
    return total


@register.filter(name='times')
def times(number):
    return range(int(str(number)))


@register.simple_tag
def getappstatus(pk):
    appstatus = Empstatus.objects.filter(id=pk).first()
    return appstatus


@register.simple_tag
def locatorslips(id):
    ls = Locatorslip.objects.filter(outpass_id=id).first()
    return ls


@register.simple_tag
def getemployee(id):  # by id number
    empname = Empprofile.objects.filter(id_number=id).first()
    return empname


@register.simple_tag
def getemployeebyempid(id):
    empname = Empprofile.objects.filter(id=id).first()
    if empname:
        return empname
    return None


@register.simple_tag
def getemployeebyuserid(id):
    empname = Empprofile.objects.filter(pi__user_id=id).first()
    if empname:
        return empname
    return None


@register.simple_tag
def getweek(date):  # string ang date
    mydate = parse_date(date)
    indexofday = mydate.weekday()
    newdate = mydate
    for i in range(indexofday):
        newdate = newdate - timedelta(days=1)

    enddate = newdate + timedelta(days=4)
    d = [newdate, enddate]
    return d


@register.simple_tag
def getdatesinweek(date):  # string ang date
    f = [parse_date(date)]
    startdate = parse_date(date)
    for i in range(4):
        newdate = startdate + timedelta(days=1)
        f.append(newdate)
        startdate = newdate

    return f


@register.simple_tag
def isbetween(time, time_range):
    if time_range[1] < time_range[0]:
        return time >= time_range[0] or time <= time_range[1]
    return time_range[0] <= time <= time_range[1]


@register.simple_tag
def date_isbetween(date, date_range):
    return date_range[0] <= date <= date_range[1]


@register.simple_tag
def getnumberofhours(start, id, format):
    start = getweek(start)
    start = start[0]
    timeconsumed = 0
    for i in range(5):
        thisdate = Outpassdetails.objects.filter(Q(date=str(start.strftime('%Y-%m-%d'))), Q(outpass__in_behalf_of=id),
                                                 Q(outpass__status=2), Q(nature=2)).first()

        if thisdate is not None:
            if thisdate.time_returned is None:
                timeconsumed = timeconsumed + 7201
            else:
                minusfive = isbetween(datetime.combine(date.today(), datetime.strptime("17:00:00", "%H:%M:%S").time())
                                      .time(), (thisdate.time_out, thisdate.time_returned))
                minusnoon1 = isbetween(datetime.combine(date.today(), datetime.strptime("12:00:00", "%H:%M:%S").time())
                                       .time(), (thisdate.time_out, thisdate.time_returned))
                minusnoon2 = isbetween(datetime.combine(date.today(), datetime.strptime("12:59:00", "%H:%M:%S").time())
                                       .time(), (thisdate.time_out, thisdate.time_returned))

                if minusnoon1 and not minusnoon2:
                    thisdate.time_returned = datetime.strptime("12:00:00", "%H:%M:%S").time()

                if minusfive:
                    thisdate.time_returned = datetime.strptime("17:00:00", "%H:%M:%S").time()

                timediff = datetime.combine(date.today(), thisdate.time_returned) - datetime.combine(date.today(),
                                                                                                     thisdate.time_out)
                timeconsumed = timeconsumed + timediff.total_seconds()

                if minusnoon1 and minusnoon2:
                    timeconsumed = timeconsumed - 3600

        start = start + timedelta(days=1)
    if timeconsumed > 7200:
        remainingtime = 0
    else:
        remainingtime = 7200 - timeconsumed

    if format == 1:
        e = [timedelta(seconds=timeconsumed), timedelta(seconds=remainingtime)]
    else:
        e = [timeconsumed, remainingtime]

    return e


@register.simple_tag
def getnumberofhoursfordate(start, id, format):
    timeconsumed = 0
    thisdate = Outpassdetails.objects.filter(Q(date=str(start)), Q(outpass__in_behalf_of=id),
                                             Q(outpass__status=2), Q(nature=2)).first()
    if thisdate is not None:
        if thisdate.time_returned is None:
            timeconsumed = 7201
        else:
            minusfive = isbetween(datetime.combine(date.today(), datetime.strptime("17:00:00", "%H:%M:%S").time())
                                  .time(), (thisdate.time_out, thisdate.time_returned))
            minusnoon1 = isbetween(datetime.combine(date.today(), datetime.strptime("12:00:00", "%H:%M:%S").time())
                                   .time(), (thisdate.time_out, thisdate.time_returned))
            minusnoon2 = isbetween(datetime.combine(date.today(), datetime.strptime("12:59:00", "%H:%M:%S").time())
                                   .time(), (thisdate.time_out, thisdate.time_returned))

            if minusnoon1 and not minusnoon2:
                thisdate.time_returned = datetime.strptime("12:00:00", "%H:%M:%S").time()

            if minusfive:
                thisdate.time_returned = datetime.strptime("17:00:00", "%H:%M:%S").time()

            timediff = datetime.combine(date.today(), thisdate.time_returned) - datetime.combine(date.today(),
                                                                                                 thisdate.time_out)
            timeconsumed = timeconsumed + timediff.total_seconds()

            if minusnoon1 and minusnoon2:
                timeconsumed = timeconsumed - 3600

    start = start + datetime.timedelta(days=1)

    if timeconsumed > 7200:
        remainingtime = 0
    else:
        remainingtime = 7200 - timeconsumed

    if format == 1:
        g = [timedelta(seconds=timeconsumed), timedelta(seconds=remainingtime)]
    else:
        g = [timeconsumed, remainingtime]

    return g


@register.simple_tag
def get_userpermission(user_id, permission_id):
    permission = AuthUserUserPermissions.objects.filter(user_id=user_id, permission_id=permission_id)
    if permission:
        return True
    else:
        return False


@register.simple_tag
def getcurrenttime(dt, tm):
    x = datetime.combine(dt, tm)
    return [x, datetime.now()]


@register.simple_tag
def formatdate(dt, tm):
    z = datetime.combine(dt, datetime.strptime(tm, '%H:%M:%S').time())
    return datetime.strftime(z, '%Y/%m/%d %H:%M:%S')


@register.simple_tag
def getactivebadges():
    badges = Badges.objects.all()
    return badges


@register.simple_tag
def count_empstatus(pk):
    total = Empprofile.objects.filter(empstatus_id=pk).count()
    return total


@register.simple_tag
def award_has_winner(pk):
    total = Nominees.objects.filter(Q(awards_id=pk), Q(is_winner=1))
    return total.count() if total else None


@register.simple_tag
def check_leavepermission(id, empstatus_id):
    check = LeavePermissions.objects.filter(leavesubtype_id=id, empstatus_id=empstatus_id).first()
    if check:
        return True
    else:
        return False


@register.simple_tag
def generate_countersignatories(emp, highest_position):
    ta = PortalConfiguration.objects.filter(key_name='Travel Administrator').first()
    employee = Empprofile.objects.filter(id=ta.key_acronym.split(',')[0]).first()
    highd = Designation.objects.filter(name=highest_position).first()
    highest = Empprofile.objects.filter(id=highd.emp_id).first()

    first = get_initials(
        highest.pi.user.first_name + ' ' + highest.pi.user.middle_name + ' ' + highest.pi.user.last_name) + ' / '

    second = ta.key_acronym.split(',')[1] + " / "
    third = ta.key_acronym.split(',')[2] + " / "

    fourth = get_initials(
        employee.pi.user.first_name + ' ' + employee.pi.user.middle_name + ' ' + employee.pi.user.last_name)

    countersignatories = first.upper() + second.upper() + third + fourth
    return countersignatories


@register.simple_tag
def get_initials(name):
    name_initials = ''
    name = re.split('-| ', name)

    for e in name:
        name_initials = name_initials + get_first(e)

    return name_initials.lower()


@register.simple_tag
def get_first(word):
    return word[:1]


@register.simple_tag
def getworkhistory(we_id):
    data = Workhistory.objects.filter(we_id=we_id).first()
    return data


@register.filter(name='age')
def age(bday):
    age = date.today() - parse_date(bday)
    return age.days


@register.simple_tag
def getdtrtime(empid, date, type):
    travel = Ritopeople.objects.values_list('detail__rito_id', flat=True).\
        filter(name_id=empid,
               detail__inclusive_to__gte=datetime.strftime(date, '%Y-%m-%d'),
               detail__inclusive_from__lte=datetime.strftime(date, '%Y-%m-%d')
                ).first()

    to = TravelOrder.objects.values_list('rito__tracking_no', flat=True).filter(rito_id=travel, status=2).first()
    if to:
        dtr = DtrPin.objects.filter(emp_id=empid).first()
        if dtr:
            data = Dtr.objects.using('amscoa').filter(Q(employeeid=dtr.pin_id),
                                                      Q(date=datetime.strftime(date, '%Y-%m-%d')),
                                                      Q(status=type)).values_list('time', flat=True).first()
            if data:
                return [time.strftime(data, '%I:%M %p'), '']
            else:
                return ['OB', to]
    else:
        dtr = DtrPin.objects.filter(emp_id=empid).first()
        if dtr:
            data = Dtr.objects.using('amscoa').filter(Q(employeeid=dtr.pin_id), Q(date=datetime.strftime(date, '%Y-%m-%d')), Q(status=type)).values_list('time', flat=True).first()
            if data:
                return [time.strftime(data, '%I:%M %p'), '']
            else:
                type_list = {"0": "1", "2": "2", "3": "3", "1": "4"}
                tym = WfhTime.objects.filter(Q(emp_id=empid), Q(datetime__date=date), Q(type_id=type_list[str(type)]))
                if tym:
                    employee_time = tym.values_list('datetime', flat=True).order_by('datetime').first()
                    if tym.first().ip_address == "192.168.34.5":
                        if tym.first().emp.position.name == "OJT":
                            return [datetime.strftime(employee_time, '%I:%M %p'), '']
                        else:
                            return [datetime.strftime(employee_time, '%I:%M %p'), 'WFH']
                    else:
                        return [datetime.strftime(employee_time, '%I:%M %p'), '']
                else:
                    return ['', '']
        else:
            type_list = {"0": "1", "2": "2", "3": "3", "1": "4"}
            tym = WfhTime.objects.filter(Q(emp_id=empid), Q(datetime__date=date), Q(type_id=type_list[str(type)]))
            if tym:
                employee_time = tym.values_list('datetime', flat=True).order_by('datetime').first()
                if tym.first().ip_address == "192.168.34.5":
                    if tym.first().emp.position.name == "OJT":
                        return [datetime.strftime(employee_time, '%I:%M %p'), '']
                    else:
                        return [datetime.strftime(employee_time, '%I:%M %p'), 'WFH']
                else:
                    return [datetime.strftime(employee_time, '%I:%M %p'), '']

            else:
                return ['', '']


@register.simple_tag
def get_accomplishment_report(emp_id, start_date, end_date):
    accomplishment = PasAccomplishmentOutputs.objects.filter(emp_id=emp_id,
                                                             date_period__range=[start_date, end_date]).order_by(
        'date_period')
    return accomplishment


@register.simple_tag
def count_possible_merges(model, q, id):
    thismodel = None
    if model == 'degree':
        thismodel = Degree.objects.annotate(name=F('degree_name')).annotate(acronym=F('degree_acronym')) \
            .filter(~Q(id=id)).values_list('name', flat=True)
    elif model == 'organization':
        thismodel = Organization.objects.annotate(name=F('org_name')).filter(~Q(id=id)).values_list('name', flat=True)
    elif model == 'honors':
        thismodel = Honors.objects.annotate(name=F('hon_name')).filter(~Q(id=id)).values_list('name', flat=True)
    elif model == 'schools':
        thismodel = School.objects.annotate(name=F('school_name')).filter(~Q(id=id)).values_list('name', flat=True)
    elif model == 'trainingtitles':
        thismodel = Trainingtitle.objects.annotate(name=F('tt_name')).filter(~Q(id=id)).values_list('name', flat=True)
    elif model == 'eligibilities':
        thismodel = Eligibility.objects.annotate(name=F('el_name')).filter(~Q(id=id)).values_list('name', flat=True)
    elif model == 'positions':
        thismodel = Position.objects.filter(~Q(id=id)).values_list('name', flat=True)
    elif model == 'hobbies':
        thismodel = Hobbies.objects.annotate(name=F('hob_name')).filter(~Q(id=id)).values_list('name', flat=True)
    elif model == 'nonacads':
        thismodel = Nonacad.objects.annotate(name=F('na_name')).filter(~Q(id=id)).values_list('name', flat=True)

    results = False
    if q.lower() in thismodel:
        results = True
    else:
        for el in thismodel:
            if el.lower() in re.split('[ \t\n\r\f,.;!?"()"\\\'/]', q.lower()) or q.lower() in el.lower():
                results = True

    return results


@register.simple_tag
def parseSrc(src):
    return urllib.parse.quote(src).replace('%20', '+')


@register.simple_tag
def get_payeegroup_members(payeegroup_id):
    payees = PayrollPayeeGroupEmployee.objects.filter(payeegroup_id=payeegroup_id).values('emp_id')
    numberofpayees = len(payees)
    allpayees = Empprofile.objects.order_by('?').filter(id__in=payees)
    if numberofpayees > 7:
        allpayees = Empprofile.objects.order_by('?').filter(id__in=payees)[:7]

    return [allpayees, numberofpayees, numberofpayees - 7]


@register.simple_tag
def get_columngroup_members(columngroup_id):
    columns = PayrollColumnGroupColumns.objects.filter(columngroup_id=columngroup_id).values('column_id')
    numberofcolumns = len(columns)
    allcolumns = PayrollColumn.objects.order_by('?').filter(id__in=columns)
    if numberofcolumns > 7:
        allcolumns = PayrollColumn.objects.order_by('?').filter(id__in=columns)[:7]

    return [allcolumns, numberofcolumns, numberofcolumns - 7]


@register.simple_tag
def get_number_of_payees_in_payroll(payroll_id):
    payees = PayrollEmployee.objects.filter(payroll_id=payroll_id)
    return len(payees)


@register.simple_tag
def get_number_of_columns_in_payroll(payroll_id):
    columns = PayrollMainColumns.objects.filter(payroll_id=payroll_id)
    return len(columns)


@register.simple_tag
def get_server_time():
    return int(mktime(datetime.now().timetuple()))


@register.simple_tag
def jinja_hack(keyword):
    return '{{ ' + keyword + ' }}' if keyword else None


@register.simple_tag
def check_to_exist(rito_id):
    check = TravelOrder.objects.filter(rito_id=rito_id).first()
    if check:
        return True
    else:
        return False


@register.simple_tag
def strip(str):
    return str.strip()


@register.simple_tag
def age(bdate):
    today = date.today()
    if bdate is None:
        return '0'
    else:
        age = relativedelta.relativedelta(today, bdate)
        return age.years


def get_prov(prov):
    if prov is None:
        return ''
    else:
        data = Province.objects.filter(id=prov).first()
        return data.name if data else ""


def get_city(code):
    if code is None:
        return ''
    else:
        city = City.objects.filter(code=code).first()
        return str(city.name) + ', ' + get_prov(city.prov_code_id) if city else ""


def get_brgy(brgy):
    if brgy is None:
        return ''
    else:
        data = Brgy.objects.filter(id=brgy).first()
        return data.name if data else ""


@register.simple_tag
def get_residentialadd(ids):
    if ids is None:
        return ''
    else:
        add = Address.objects.filter(pi_id=ids).first()
        return str(add.ra_house_no) + ', ' + str(add.ra_street) + ', ' + str(add.ra_village) + ', ' + get_brgy(
            add.ra_brgy) + ', ' + get_city(add.ra_city) if add else ""


@register.simple_tag
def get_section(sec_id):
    if sec_id is None:
        return ''
    else:
        section = Section.objects.filter(id=sec_id).first()
        return section.sec_name


@register.simple_tag
def get_division(div_id):
    if div_id is None:
        return ''
    else:
        div = Section.objects.filter(id=div_id).first()
        return div.div.div_acronym


@register.simple_tag
def get_date_duration_from_now(dt, id, max):
    startdate = dt
    cntr = 0
    while startdate < datetime.now():
        weeknum = startdate.weekday()
        if weeknum < 5:
            cntr += 1
        startdate = startdate + timedelta(days=1)
    if cntr > max:
        PortalAnnouncements.objects.filter(id=id).update(is_active=False)
    return cntr


@register.simple_tag
def get_name(emp_id):
    return Empprofile.objects.filter(id=emp_id).first()


@register.simple_tag
def is_past_due(date):
    return date.today() < date


@register.simple_tag
def get_address(prov, city, brgy, others=None):
    p = Province.objects.filter(id=prov).first()
    c = City.objects.filter(id=city).first()
    b = Brgy.objects.filter(id=brgy).first()
    if b:
        return b.city_code.prov_code.name + ', ' + b.city_code.name + ', ' + b.name
    elif c:
        return c.prov_code.name + ', ' + c.name
    elif p:
        return p.name
    else:
        return others


@register.simple_tag
def get_grievance_trail(grievance_id):
    trail = GrievanceRecordsOfAction.objects.filter(gquery_id=grievance_id).order_by('-id')
    return trail


@register.simple_tag
def get_tracking_trail(document_id):
    trail = DtsTransaction.objects.filter(document_id=document_id, action__in=[0, 1, 2, 3]).order_by('-date_saved',
                                                                                                     '-action')
    return trail


@register.simple_tag
def get_cc(document_id):
    cc = DtsTransaction.objects.filter(document_id=document_id, action__in=[4]).order_by('-date_saved')
    return cc


@register.simple_tag
def get_cc_divs(document_id):
    cc_divs = DtsDivisionCc.objects.filter(document_id=document_id).order_by('-document__date_saved')
    return cc_divs


@register.simple_tag
def getDocumentCurrentStatus(doc_info_id):
    status = DocsTrackingStatus.objects.filter(doc_info_id=doc_info_id).last()
    if status:
        return status.trail.name


@register.simple_tag
def getDirectoryDetails(dtype, contact):
    return list(DirectoryDetails.objects.filter(dtype_id=dtype, dcontact_id=contact).values_list('description',
                                                                                                 flat=True).order_by(
        'description'))


@register.simple_tag
def getDirectoryDetailsIndividual(dtype, contact):
    return DirectoryDetails.objects.filter(dtype_id=dtype, dcontact_id=contact).order_by('description')


@register.simple_tag
def getAllContacts():
    return DirectoryContact.objects.filter(status=1).order_by('last_name', 'first_name')


@register.simple_tag
def getDetailTypes():
    return DirectoryDetailType.objects.filter(status=1).order_by('type')


@register.simple_tag
def nl2br(string):
    return string.replace('\r\n', '<br>')


@register.simple_tag
def replace_string(value, new_value):
    return value.replace("Separated", new_value)


@register.simple_tag
def get_directory_entries_per_orgtype(orgtype, search=None):
    return DirectoryContact.objects.filter((Q(company__icontains=search) |
                                           Q(job_title__icontains=search) |
                                           Q(ext__name__icontains=search) |
                                           Q(first_name__icontains=search) |
                                           Q(last_name__icontains=search) |
                                           Q(middle_name__icontains=search)),
                                           Q(orgtype_id=orgtype)).count()


@register.simple_tag
def get_services_transaction(services_id):
    return DeskServicesTransaction.objects.filter(services_id=services_id)


@register.simple_tag
def get_services_attachment(services_id):
    return DeskServicesAttachment.objects.filter(services_id=services_id)


@register.simple_tag
def get_employee_reports(**kwargs):
    total = []
    if kwargs['empstatus'] == "Regular":
        reports = Workhistory.objects.filter(
            we__company__icontains="DEPARTMENT OF SOCIAL WELFARE AND DEVELOPMENT, FIELD OFFICE CARAGA",
            we__we_from__lte=kwargs['date'],
            emp__pi__gender__icontains=kwargs['gender'],
            emp__empstatus__name__icontains=kwargs['empstatus']).values('emp_id', 'emp__pi_id', 'emp__pi__dob').annotate(
        dcount=Count('emp_id'))
    else:
        reports = Workhistory.objects.filter(
            we__company__icontains="DEPARTMENT OF SOCIAL WELFARE AND DEVELOPMENT, FIELD OFFICE CARAGA",
            we__we_to__lte=kwargs['date'],
            emp__pi__gender__icontains=kwargs['gender'],
            emp__empstatus__name__icontains=kwargs['empstatus']).values('emp_id', 'emp__pi_id', 'emp__pi__dob').annotate(
            dcount=Count('emp_id'))

    if kwargs['value'] == "Solo Parent":
         for row in reports:
            check = Additional.objects.filter(pi_id=row['emp__pi_id']).last()
            if check:
                if check.answers:
                    total.append(check.answers)
    elif kwargs['value'] == "PWD":
        for row in reports:
            check = Additional.objects.filter(pi_id=row['emp__pi_id']).values_list('answers', flat=True)
            try:
                if list(check)[-2]:
                    total.append(list(check)[-2])
            except IndexError:
                pass
    elif kwargs['value'] == "SC":
        for row in reports:
            today = date.today()
            age = relativedelta.relativedelta(today, row['emp__pi__dob'])
            if age.years >= 60:
                total.append(row['emp__pi_id'])
    elif kwargs['value'] == "ID":
        for row in reports:
            check = Additional.objects.filter(pi_id=row['emp__pi_id']).values_list('answers', flat=True)
            try:
                if list(check)[-3]:
                    total.append(list(check)[-3])
            except IndexError:
                pass
    elif kwargs['value'] == "RSW":
        for row in reports:
            check = Civilservice.objects.filter(pi_id=row['emp__pi_id'], course__name='Social Workers').first()
            if check:
                total.append(check.id)

    return len(total)


@register.simple_tag
def get_to_tracking_merge_number(tracking_merge):
    rito = Rito.objects.filter(tracking_merge=tracking_merge)
    return rito if rito else None


@register.simple_tag
def get_transmittal_trail(id):
    return TransmittalTransaction.objects.filter(trans_id=id).order_by('-id')


@register.simple_tag
def get_ipcr_rating(emp_id, year, semester):
    check = IPC_Rating.objects.filter(emp_id=emp_id, year=year, semester=semester)
    return check.first() if check else "Not Available"


@register.simple_tag
def get_adjectival_rating(rating, year):
    if rating:
        check = IPC_AdjectivalRating.objects.filter(year=year, start_average__lte=rating, end_average__gte=rating)
        if check:
            return check.first().remarks
        else:
            return None
    else:
        return "Not Available"


@register.simple_tag
def get_annual_ipc_rating(first_sem, second_sem):
    if first_sem and second_sem:
        total = first_sem + second_sem
        return total / 2
    else:
        return first_sem if first_sem else second_sem


@register.simple_tag
def track_drn(emp_id, value):
    check = DRNTracker.objects.filter(emp_id=emp_id, value=value)
    return check.first().drn if check else None


@register.simple_tag
def service_record_data(wh_id):
    data = PasServiceRecordData.objects.filter(wh_id=wh_id)
    if data:
        return data.first()


@register.simple_tag
def get_acronym(stng):
    oupt = stng[0]

    for i in range(1, len(stng)):
        if stng[i - 1] == ' ':
            oupt += stng[i]

    oupt = oupt.upper()
    return oupt


@register.simple_tag
def get_doc_version(id):
    return PortalConfiguration.objects.filter(id=id).first().key_acronym


@register.simple_tag
def get_latest_workexperience(pi_id):
    data = Workexperience.objects.filter(pi_id=pi_id).order_by('-we_from').first().we_from
    return data


@register.simple_tag
def get_person_administering_oath(name):
    data = PortalConfiguration.objects.filter(key_name=name).first().key_acronym
    return data


@register.simple_tag
def get_total_by_division(id, value):
    data = Empprofile.objects.filter(Q(section__div_id=id) &
                                     Q(pi__user__is_active=1) &
                                     Q(aoa__name__icontains=value) &
                                     ~Q(position__name__icontains='OJT')).count()
    return data


@register.simple_tag
def get_total_convocation_by_division(id, date, type):
    data = ConvocationAttendance.objects.filter(date=date, emp__section__div_id=id, status=type, emp__pi__user__is_active=1).count()
    return data


@register.simple_tag
def get_attendance_percentage(total, overall):
    percentage = total / overall * 100
    return percentage


@register.simple_tag
def get_time_in_and_out(date, type, emp_id):
    data = ConvocationAttendance.objects.filter(date=date, emp_id=emp_id, status=type)
    return data.first().time if data else ''


@register.simple_tag
def get_deduction_number(pi_id):
    return Deductionnumbers.objects.filter(pi_id=pi_id).first()


@register.simple_tag
def get_total_leavesubtype_per_status(leavesubtype_id, current_year):
    total_leave_pending = LeaveApplication.objects.filter(date_of_filing__year=current_year,
                                                          status=0, leavesubtype_id=leavesubtype_id).count()
    total_leave_approved = LeaveApplication.objects.filter(date_of_filing__year=current_year,
                                                           status=1, leavesubtype_id=leavesubtype_id).count()
    total_leave_canceled = LeaveApplication.objects.filter(date_of_filing__year=current_year,
                                                           status=2, leavesubtype_id=leavesubtype_id).count()

    return [total_leave_pending, total_leave_approved, total_leave_canceled]


@register.filter(name='get_first_val')
def get_first_val(value, key):
    return value.split(key)[0]


@register.simple_tag
def get_dtr_assigned(assigned_id):
    return DTRAssignee.objects.filter(assigned_id=assigned_id)


@register.simple_tag
def get_date_interval_in_days(date_one, date_two):
    if date_one and date_two:
        difference = date_one - date_two

        days = difference.days

        if days >= 0:
            return days
        else:
            return None
    else:
        return None


@register.simple_tag
def get_to_approved_and_uploaded_date(tracking_no):
    travel = TravelOrder.objects.filter(rito__tracking_no=tracking_no).first()

    if travel:
        return [travel.date, travel.date_uploaded]
    else:
        return [None, None]


@register.simple_tag
def get_color_coding(employee_id):
    check = PasEmpPayrollIncharge.objects.filter(emp_id=employee_id)
    if check:
        return check.first().payroll_incharge.color
    else:
        return None


@register.simple_tag
def check_coc_utilization(cocactualbal_id):
    check = CTDOUtilization.objects.filter(cocactualbal_id=cocactualbal_id)
    if check:
        return "Prev. Balance"
    else:
        return None


@register.simple_tag
def check_coc_balances(ctdoreq_id, cocactualbal_id):
    coc = CTDOUtilization.objects.filter(ctdoreq_id=ctdoreq_id, cocactualbal_id=cocactualbal_id).first()
    if coc:
        return True
    else:
        return None


@register.simple_tag
def total_coc_balances(current_balance, ctdoreq_id, month_earned, type):
    coc = CTDOUtilization.objects.filter(ctdoreq_id=ctdoreq_id, cocactualbal__cocbal__month_earned=month_earned).first()
    if coc:
        if type == "days":
            return int(current_balance) + int(coc.days)
        elif type == "hours":
            return int(current_balance) + int(coc.hours)
        elif type == "minutes":
            return int(current_balance) + int(coc.minutes)
    else:
        return int(current_balance)


@register.filter
def dates_range(start, end):
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    date_generated = [start_date + timedelta(days=x) for x in range(0, (end_date-start_date).days + 1)]
    return date_generated


@register.filter
def split(value, key):
    return value.split(key)


@register.simple_tag
def get_rito_pending(emp_id):
    pending_ritos = Rito.objects.filter(
        Q(emp__section__div__div_chief_id=emp_id) &
        ~Q(status__in=[1, 3, 4, 5])
    )
    return pending_ritos.count()
