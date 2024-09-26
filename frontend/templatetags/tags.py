import hashlib
import os
import re
from pathlib import Path
from django.conf import settings

import numpy as np
from datetime import date, datetime, timedelta

from django import template
from django.db.models import Q, Sum
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from backend.awards.models import Nominees, Deliberation, AwEligibilityChecklist
from backend.calendar.models import CalendarShared
from backend.documents.models import DtsTransaction, DtsDrn, DtsAttachment, DtsDocument
from backend.iso.models import IsoDownloadhistory
from backend.libraries.gamification.models import GamifyCurrentLevel, GamifyLevels, GamifyPoints, GamifyActivities
from backend.libraries.grievance.models import GrievanceRecordsOfAction

from backend.libraries.leave.models import LeaveCredits, LeaveRandomDates, LeaveApplication, \
    CTDORandomDates, CTDORequests
from backend.models import Division, Designation, WfhTime, Empprofile, Section
from backend.pas.payroll.models import PayrollColumns
from frontend.models import TravelOrder, Training, Workexperience, Rito, Ritopeople, Faqs, PortalConfiguration, \
    DeskServicesTransactionAttachment, DeskServicesAdInfo, Quotes, PasAccomplishmentOutputs
from frontend.pas.overtime.models import OvertimeEmployee

register = template.Library()


@register.simple_tag
def payroll_type_value(value):
    try:
        if value == "":
            return [True, 0]
        else:
            float(value)
            return [True, value]
    except ValueError:
        return [False, value]


@register.simple_tag
def payroll_column_type(value):
    try:
        return PayrollColumns.objects.filter(attribute=value).first().column_type_id
    except Exception as e:
        return None


@register.simple_tag
def get_signatory(emp_id):
    signatory = ""
    signatory_pos = ""
    signatory_sl = ""
    signatory_sl_pos = ""
    signatory_sl_div_id_number = ""

    designation = Designation.objects.filter(emp_id=emp_id).first()

    if designation:
        config = PortalConfiguration.objects.filter(id=5).first()
        signatory = config.key_acronym
        signatory_pos = config.key_name
        signatory_sl = config.key_acronym
        signatory_sl_pos = config.key_name
    else:
        div_head = Division.objects.filter(div_chief_id=emp_id).first()

        if div_head:
            head = Empprofile.objects.filter(id=div_head.designation.emp_id).first()
            signatory = "{}, {}".format(head.pi.user.get_fullname.upper(), head.position.acronym)
            signatory_pos = div_head.designation.name
            signatory_sl = "{}, {}".format(head.pi.user.get_fullname.upper(), head.position.acronym)
            signatory_sl_pos = div_head.designation.name
            signatory_sl_div_id_number = head.id_number
        else:
            employee = Empprofile.objects.filter(id=emp_id).first()

            section = Section.objects.filter(Q(sec_head_id=emp_id), Q(is_alternate=0)).first()

            if section:
                # Division Chief
                division = Division.objects.filter(id=employee.section.div.id).first()
                division_chief = Empprofile.objects.filter(id=division.div_chief_id).first()
                signatory = "{}, {}".format(division_chief.pi.user.get_fullname.upper(),
                                            division_chief.position.acronym)

                designation = Designation.objects.filter(emp_id=division.div_chief_id).first()

                signatory_pos = "Chief, {}".format(division.div_name) if not designation else "{}".format(division.div_name)

                signatory_sl = "{}, {}".format(division_chief.pi.user.get_fullname.upper(),
                                               division_chief.position.acronym)
                signatory_sl_pos = "Chief, {}".format(division.div_name) if not designation else "{}".format(division.div_name)
                signatory_sl_div_id_number = division_chief.id_number
            else:
                if employee.section:
                    # Division Chief
                    division = Division.objects.filter(id=employee.section.div.id).first()
                    division_chief = Empprofile.objects.filter(id=division.div_chief_id).first()
                    signatory = "{}, {}".format(division_chief.pi.user.get_fullname.upper(),
                                                division_chief.position.acronym)

                    designation = Designation.objects.filter(emp_id=division.div_chief_id).first()

                    signatory_pos = "Chief, {}".format(division.div_name) if not designation else "{}".format(division.div_name)

                    # Section Head
                    section = Section.objects.filter(id=employee.section_id).first()
                    section_head = Empprofile.objects.filter(id=section.sec_head_id).first()
                    signatory_sl = "{}, {}".format(section_head.pi.user.get_fullname.upper(),
                                                   section_head.position.acronym)
                    signatory_sl_pos = "{}, {}".format("OIC" if section.is_alternate else "Head", section.sec_name)
                    signatory_sl_div_id_number = division_chief.id_number
                else:
                    signatory = ''
                    signatory_pos = ''
                    signatory_sl = ''
                    signatory_sl_pos = ''
                    signatory_sl_div_id_number = ''

    return {'signatory': signatory, 'signatory_pos': signatory_pos, 'signatory_sl': signatory_sl,
            'signatory_sl_pos': signatory_sl_pos, 'signatory_sl_div_id_number': signatory_sl_div_id_number}


@register.simple_tag
def transform_to_duration_date(datefrom, dateto, dateto_isexclusive="false", return_interval="false", shorten=False):
    try:
        if "true" in return_interval:
            delta = dateto - datefrom
        if "true" in dateto_isexclusive:
            dateto = dateto - timedelta(days=1)
        str = None
        if datefrom and dateto:
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] if shorten else \
                ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                 'November', 'December']
            if datefrom.day == dateto.day and datefrom.month == dateto.month and datefrom.year == dateto.year:
                str = '{} {}, {}'.format(months[datefrom.month - 1], datefrom.day, datefrom.year)
            elif datefrom.month == dateto.month and datefrom.year == dateto.year:
                str = '{} {} - {}, {}'.format(months[datefrom.month - 1], datefrom.day, dateto.day, datefrom.year)
            elif datefrom.year == dateto.year:
                str = '{} {} - {} {}, {}'.format(months[datefrom.month - 1], datefrom.day, months[dateto.month - 1],
                                                 dateto.day, datefrom.year)
            else:
                str = '{} {}, {} - {} {}, {}'.format(months[datefrom.month - 1], datefrom.day, datefrom.year,
                                                     months[dateto.month - 1], dateto.day, dateto.year)

        return delta.days if "true" in return_interval else str
    except Exception as e:
        pass


@register.simple_tag
def check_to_status(rito_id):
    checked = TravelOrder.objects.filter(Q(rito_id=rito_id)).first()
    if checked:
        return [True, checked.status,
                checked.id, checked.date, checked.approved_by_id]
    return [False]


@register.simple_tag
def check_to_approved(tracking_no):
    check_merge = Rito.objects.filter(tracking_merge=tracking_no).first()
    if check_merge:
        check = TravelOrder.objects.filter(Q(rito__tracking_merge=tracking_no) & Q(status=2)).first()
        if check:
            return True
        else:
            return False
    else:
        check = TravelOrder.objects.filter(Q(rito__tracking_no=tracking_no) & Q(status=2)).first()
        if check:
            return True
        else:
            return False


@register.simple_tag
def travel_order_attachment(tracking_no):
    check_merge = Rito.objects.filter(tracking_merge=tracking_no)
    if check_merge:
        to = TravelOrder.objects.filter(rito__tracking_merge=tracking_no).first()
        return to
    else:
        to = TravelOrder.objects.filter(rito__tracking_no=tracking_no).first()
        if to:
            return to
        else:
            return False


@register.simple_tag
def check_to_attachment(rito_id):
    checked = TravelOrder.objects.filter(Q(rito_id=rito_id) & ~Q(attachment='')).first()
    if checked:
        return [True, checked.attachment]
    return False


@register.simple_tag
def check_pagefive(pk):
    date_today = date.today()
    fiveyear_interval_date = datetime.now() - timedelta(days=5 * 365)
    work = Workexperience.objects.filter(pi_id=pk).order_by('-we_to')[30:]
    training = Training.objects.filter(pi_id=pk,
                                       tr_to__range=[fiveyear_interval_date.strftime("%Y-%m-%d"), date_today]).order_by(
        '-tr_to')[20:]
    data = [training.count, work.count]
    return data


@register.simple_tag
def get_extension(string):
    extension = os.path.splitext(string)
    return extension


@register.filter(name='md5')
def md5_string(value):
    return hashlib.md5(str(value).encode()).hexdigest()


@register.simple_tag
def get_feedbackavg(total_rate, avg):
    if total_rate == 0:
        return 0
    return float("{0:.2f}".format(total_rate / avg))


@register.filter(name='to_int')
def to_int(num):
    try:
        x = int(num)
    except ValueError:
        x = num
    return x


@register.filter(name='to_middleinitial')
def to_middleinitial(middlename):
    if middlename != '' and middlename is not None:
        return middlename[0:1].upper() + '.'
    return ''


@register.simple_tag
def get_numberofnominees(pk):
    noms = Nominees.objects.filter(awards_id=pk)
    return noms.count()


@register.simple_tag
def get_eligibility_checklist(eligibility_id, nominees_id):
    check = AwEligibilityChecklist.objects.filter(nominees_id=nominees_id, eligibility_id=eligibility_id)
    return True if check else False


@register.simple_tag
def days_until(start_date, end_date):
    if start_date == end_date:
        total = 1
    else:
        total = np.busday_count(start_date, end_date, weekmask=[1, 1, 1, 1, 1, 0, 0]) + 1
    return total


@register.simple_tag
def get_leavecredits(value, emp_id):
    leave_credits = LeaveCredits.objects.filter(emp_id=emp_id, leavetype__name=value).first()
    return leave_credits


# Checking of how many people in Travel Request
@register.simple_tag
def get_to_people(pk):
    pass
    # details = Ritodetails.objects.filter(rito_id=pk)
    # total = []
    # for row in details:
    #     people = Ritopeople.objects.filter(detail_id=row.id).count()
    #     total.append(people)
    #
    # return sum(total)


@register.simple_tag
def check_division(id):
    div_acronym = Division.objects.values_list('div_acronym', flat=True).get(div_chief_id=id)
    return div_acronym


@register.simple_tag
def check_designation(id):
    div_acronym = Designation.objects.values_list('name', flat=True).get(emp_id=id)
    return div_acronym


@register.simple_tag
def get_dtr_status(emp_id, type_id):
    check = WfhTime.objects.filter(user_id=emp_id, type_id=type_id)
    return check


@register.simple_tag
def get_faqs():
    faq = Faqs.objects.all()
    return faq


@register.simple_tag
def check_leavecredits(leavetype_id, emp_id):
    check = LeaveCredits.objects.filter(leavetype_id=leavetype_id, emp_id=emp_id).first()
    if check:
        if check.leave_total > 0:
            return True
    else:
        return False


@register.simple_tag
def get_grade_of_nominee(nominee_id, criteria_id, emp_id):
    grade = Deliberation.objects.filter(Q(nominee_id=nominee_id), Q(criteria_id=criteria_id), Q(graded_by_id=emp_id)) \
        .first()
    return grade.grade if grade else ''


@register.simple_tag
def get_remarks_of_nominee(nominee_id, emp_id):
    remarks = Deliberation.objects.filter(Q(nominee_id=nominee_id), Q(graded_by_id=emp_id)) \
        .first()
    return remarks.remarks if remarks else ''


@register.simple_tag
def get_grade_for_consolidation(graded_by_id, nominee_id):
    b = Deliberation.objects.values('nominee_id') \
        .filter(Q(graded_by_id=graded_by_id), Q(nominee_id=nominee_id)) \
        .annotate(total_grade=Sum('grade'))
    c = 0
    for a in b:
        c = a['total_grade']
    return c if b else ''


@register.simple_tag
def get_grade_for_consolidation(graded_by_id, nominee_id):
    x = Deliberation.objects.values('graded_by_id', 'nominee_id') \
        .filter(Q(nominee_id=nominee_id)) \
        .annotate(total_grade=Sum('grade'))

    grades = list()
    for a in x:
        grades.append(a['total_grade'])
    uniques = set(grades)
    maxnum = 0
    minnum = 0
    if len(uniques) > 2:
        maxnum = max(uniques)
        minnum = min(uniques)

    b = Deliberation.objects.values('nominee_id') \
        .filter(Q(graded_by_id=graded_by_id), Q(nominee_id=nominee_id)) \
        .annotate(total_grade=Sum('grade'))
    c = 0
    for a in b:
        c = a['total_grade']

    if maxnum == c or minnum == c:
        return '<strike class="text-danger">&nbsp;<span class="text-danger">{}</span>&nbsp;</strike>'.format(
            c) if b else ''
    else:
        return '<span class="text-success bold">{}</span>'.format(c) if b else ''


@register.simple_tag
def get_average_grade_for_consolidation(nominee_id):
    b = Deliberation.objects.values('graded_by_id', 'nominee_id') \
        .filter(Q(nominee_id=nominee_id)) \
        .annotate(total_grade=Sum('grade'))

    grades = list()
    total = 0
    for a in b:
        grades.append(a['total_grade'])
    uniques = set(grades)
    if len(uniques) > 2:
        maxnum = max(uniques)
        minnum = min(uniques)
        try:
            while True:
                grades.remove(maxnum)
        except ValueError:
            pass

        try:
            while True:
                grades.remove(minnum)
        except ValueError:
            pass

    for g in grades:
        total += g

    if len(grades) == 0:
        divisor = 1
    else:
        divisor = len(grades)

    ave = total / divisor
    return "{:.2f}".format(ave)


@register.simple_tag
def get_top_three_for_consolidation(nominees):
    nominee = []
    average = []
    top_three = dict()
    for nom in nominees:
        b = Deliberation.objects.values('graded_by_id', 'nominee_id') \
            .filter(Q(nominee_id=nom.id)) \
            .annotate(total_grade=Sum('grade'))

        grades = list()
        total = 0
        for a in b:
            grades.append(a['total_grade'])
        uniques = set(grades)
        if len(uniques) > 2:
            maxnum = max(uniques)
            minnum = min(uniques)
            try:
                while True:
                    grades.remove(maxnum)
            except ValueError:
                pass

            try:
                while True:
                    grades.remove(minnum)
            except ValueError:
                pass

        for g in grades:
            total += g

        if len(grades) == 0:
            divisor = 1
        else:
            divisor = len(grades)

        ave = total / divisor
        top_three.update({nom.id: "{:.2f}".format(ave)})

    y = set(top_three.values())
    x = sorted(y, reverse=True)[:3]
    return x


@register.simple_tag
def getNumberOfDownloads(isoform):
    return IsoDownloadhistory.objects.filter(form_id=isoform).count()


@register.filter
def filename(value):
    return os.path.basename(value.file.name)


@register.simple_tag
def getStaffInRitoDetails(detail_id):
    people = Ritopeople.objects.filter(detail_id=detail_id).order_by('name__id_number')
    others = 0
    tresh = 5
    listofpeople = list()
    if people.count() > tresh:
        others = people.count() - tresh
        people = people[:tresh]
    for p in people:
        if '{} {}'.format(p.name.pi.user.first_name.title(), p.name.pi.user.last_name.title()) not in listofpeople:
            listofpeople.append('{} {}'.format(p.name.pi.user.first_name.title(), p.name.pi.user.last_name.title()))
    return '{}'.format(', '.join(
        listofpeople)) if others == 0 else '{} and <span data-toggle="tooltip" data-html="true" data-placement="top" title="{}">{}</span> others..'.format(
        ', '.join(listofpeople), getStaffInRitoDetailOthers(detail_id), others)


@register.simple_tag
def getStaffInRitoDetailOthers(detail_id):
    people = Ritopeople.objects.filter(detail_id=detail_id).order_by('name__id_number')
    tresh = 5
    listofpeople = list()
    if people.count() > tresh:
        people = people[tresh:]
        for p in people:
            if '{} {}'.format(p.name.pi.user.first_name.title(), p.name.pi.user.last_name.title()) not in listofpeople:
                listofpeople.append('{} {}'.format(p.name.pi.user.first_name.title(), p.name.pi.user.last_name.title()))
    return '{}'.format(', '.join(listofpeople))


@register.simple_tag
def getStaffInRito(rito_id):
    people = Ritopeople.objects.filter(detail__rito_id=rito_id).order_by('name__id_number')
    others = 0
    tresh = 5
    listofpeople = list()
    if people.count() > tresh:
        others = people.count() - tresh
        people = people[:tresh]
    for p in people:
        if '{} {}'.format(p.name.pi.user.first_name.title(), p.name.pi.user.last_name.title()) not in listofpeople:
            listofpeople.append('{} {}'.format(p.name.pi.user.first_name.title(), p.name.pi.user.last_name.title()))
    return '{}'.format(', '.join(
        listofpeople)) if others == 0 else '{} and <span data-toggle="tooltip" data-html="true" data-placement="top" title="{}">{}</span> others..'.format(
        ', '.join(listofpeople), getStaffInRitoOthers(rito_id), others)


@register.simple_tag
def getStaffInRitoOthers(rito_id):
    people = Ritopeople.objects.filter(detail__rito_id=rito_id).order_by('name__id_number')
    tresh = 5
    listofpeople = list()
    if people.count() > tresh:
        people = people[tresh:]
        for p in people:
            if '{} {}'.format(p.name.pi.user.first_name.title(), p.name.pi.user.last_name.title()) not in listofpeople:
                listofpeople.append('{} {}'.format(p.name.pi.user.first_name.title(), p.name.pi.user.last_name.title()))
    return '{}'.format(', '.join(listofpeople))


@register.simple_tag
def get_leave_dates(leaveapp_id):
    dates = LeaveRandomDates.objects.filter(leaveapp_id=leaveapp_id)

    if dates:
        if dates.count() != 1:
            random_dates = []
            for row in dates:
                random_dates.append(row.date.strftime("%B %d, %Y"))

            text = "{} and {}".format(", ".join(str(row) for row in random_dates[:-1]), random_dates[-1])
            return text
        else:
            random_dates = []
            for row in dates:
                random_dates.append(row.date.strftime("%B %d, %Y"))

            text = "{}".format(random_dates[0])
            return text
    else:
        leave = LeaveApplication.objects.filter(id=leaveapp_id).first()
        return leave.remarks


@register.simple_tag
def get_ctdo_dates(ctdo_id):
    dates = CTDORandomDates.objects.filter(ctdo_id=ctdo_id)

    if dates:
        if dates.count() != 1:
            random_dates = []
            for row in dates:
                random_dates.append(row.date.strftime("%B %d, %Y"))

            text = "{} and {}".format(", ".join(str(row) for row in random_dates[:-1]), random_dates[-1])
            return text
        else:
            random_dates = []
            for row in dates:
                random_dates.append(row.date.strftime("%B %d, %Y"))

            text = "{}".format(random_dates[0])
            return text


@register.simple_tag
def get_leave_total_days(leaveapp_id):
    dates = LeaveRandomDates.objects.filter(leaveapp_id=leaveapp_id)
    if dates:
        return dates.count()
    else:
        leave = LeaveApplication.objects.filter(id=leaveapp_id).first()
        days = re.findall('\d*\.?\d+', leave.remarks)
        total = 0.0
        for row in days:
            total = total + float(row)
        return total


@register.simple_tag
def get_dts_inbox_for_me(emp_id):
    return DtsTransaction.objects.filter(trans_to_id=emp_id, action__in=[1, 2], action_taken=None).count()


@register.simple_tag
def get_grievances_for_me(emp_id):
    return GrievanceRecordsOfAction.objects.filter(emp_id=emp_id, date_completed=None).count()


@register.simple_tag
def get_empstatus(emp_id):
    emp = Empprofile.objects.filter(id=emp_id).first()
    form_three = [3, 4, 6]
    if emp.empstatus_id in form_three:
        return 3
    else:
        return 2


@register.simple_tag
def getHash(string):
    return hashlib.sha1(str(string).encode('utf-8')).hexdigest()


@register.simple_tag
def get_number_of_downloadables_in_class(downloadables, classes):
    return downloadables.filter(classes_id=classes).count()


@register.simple_tag
def count_total_status_pending(type):
    if type == "leave":
        return LeaveApplication.objects.filter(status=0).count()
    elif type == 'ctdo':
        return CTDORequests.objects.filter(status=0).count()
    elif type == 'travel':
        return Rito.objects.filter(status=2).count() + TravelOrder.objects.filter(status=1).count()


@register.simple_tag
def add_or_remove_days_from_date(start_date, operation, number_of_days):
    return start_date + timedelta(days=number_of_days) if operation == '+' else \
        start_date - timedelta(days=number_of_days)


@register.simple_tag
def is_calendar_shared_to_me(calendar_type_id, user_id):
    is_shared = CalendarShared.objects.filter(type_id=calendar_type_id, emp_id=user_id).first()
    return is_shared if is_shared else False


@register.simple_tag
def get_ot_people(detail_id):
    return OvertimeEmployee.objects.filter(detail_id=detail_id)


@register.simple_tag
def generateDRN(document_id, drn_id, is_new=False):
    today = date.today()
    if drn_id:
        drns = DtsDrn.objects.filter(id=drn_id)
        drn = drns.first()
        if is_new:
            last_drn_series_number = DtsDrn.objects.filter(~Q(id=drn_id)).order_by('document__date_saved', 'id').last()
            new_drn_series_number = (int(last_drn_series_number.series) + 1 if last_drn_series_number else 1) \
                if today.year == drn.document.date_saved.year else 1
            drns.update(series=new_drn_series_number)
        else:
            new_drn_series_number = int(drn.series)
        series_number = str(new_drn_series_number)
        filled_series_number = series_number.zfill(6)
        return 'CARAGA-{}-{}-{}-{}-{}-{}'.format('{}-{}'.format(drn.division.div_acronym,
                                                         drn.section.sec_acronym) if
                                          drn.section and drn.section.sec_acronym
                                          else drn.division.div_acronym,
                                          drn.doctype.code, str(drn.document.date_saved.year)[-2:],
                                          drn.document.date_saved.month, filled_series_number,
                                          drn.category.code)
    else:
        return DtsDocument.objects.get(id=document_id).tracking_no


@register.simple_tag
def get_dt_attachment(document_id):
    return DtsAttachment.objects.filter(transaction__document_id=document_id)


@register.simple_tag
def typeahead_with_picture():
    return Empprofile.objects.filter(pi__user__is_active=1)


@register.simple_tag
def get_services_attachment(id):
    return DeskServicesTransactionAttachment.objects.filter(transaction_id=id)


@register.simple_tag
def get_services_additional_info(id):
    return DeskServicesAdInfo.objects.filter(services_id=id)


@register.simple_tag
def random_quotes(type_id):
    quotes = Quotes.objects.filter(type_id=type_id).values_list('quotes', flat=True).order_by("?").first()
    return quotes


@register.simple_tag
def gamify_get_user_level(emp_id):
    emp = Empprofile.objects.get(id=emp_id)
    current_user_level = GamifyCurrentLevel.objects.filter(emp_id=emp_id)
    if current_user_level:
        current_level = GamifyLevels.objects.filter(status=True, id=current_user_level.first().level_id).first()
    else:
        current_level = GamifyLevels.objects.filter(status=True, id=1).order_by('value').first()
    all_points_earned = GamifyPoints.objects.filter(emp_id=emp_id).aggregate(points=Sum('activity__points'))
    value_of_excess_points_earned = ((all_points_earned['points'] if all_points_earned['points'] else 0) - \
                                    ((current_level.value / 2) * (1 + current_level.value) * 100) + \
                                    (current_level.value * 100)) / current_level.value
    return [current_level, value_of_excess_points_earned, emp if emp else None]


@register.simple_tag
def get_position(emp_id):
    emp = Empprofile.objects.filter(id=emp_id).first()
    return emp.position.name if emp else ''


@register.simple_tag
def gamify_get_all_levels():
    return GamifyLevels.objects.filter(status=True)


@register.simple_tag
def gamify(activity_id, emp_id, current_date=date.today()):
    activity = GamifyActivities.objects.filter(status=True, id=activity_id)
    if activity.first().limit_per_day == 0:  # unlimited
        has_gained_points = True
        gained_points = activity.first().points
        GamifyPoints.objects.create(
            activity=activity.first(),
            emp_id=emp_id
        )
    else:  # limited
        daily_gained_points_for_this_activity = GamifyPoints.objects.filter(activity_id=activity_id,
                                                                            emp_id=emp_id,
                                                                            datetime__date=current_date).count()
        if daily_gained_points_for_this_activity < activity.first().limit_per_day:  # padayon kay less pa
            has_gained_points = True
            gained_points = activity.first().points
            GamifyPoints.objects.create(
                activity=activity.first(),
                emp_id=emp_id
            )
        else:
            has_gained_points = False
            gained_points = 0

    current_user_level = gamify_get_user_level(emp_id)
    if current_user_level[1] >= 100:
        gamify_level_up(emp_id)

    return [has_gained_points, gained_points]


@register.simple_tag
def gamify_level_up(emp_id):
    current_level = GamifyCurrentLevel.objects.filter(emp_id=emp_id)
    if current_level:
        current_level.update(
            level_id = (current_level.first().level_id + 1) if current_level.first().level_id < 10 \
            else current_level.first().level_id
        )
    else:
        GamifyCurrentLevel.objects.create(
            emp_id=emp_id,
            level_id=2
        )


@register.simple_tag
def check_if_weekend(date):
    if date.weekday() > 4:
        return True
    else:
        return False


@register.simple_tag
def get_accomplishment_report_data(date, emp_id):
    return PasAccomplishmentOutputs.objects.values('place_visited', 'output').filter(emp_id=emp_id, date_period=date).first()


@register.filter
def index(indexable, i):
    return indexable[i]


@register.simple_tag
def get_page_range(page, range):
    start = page * range
    end = start + range
    return [str("{}:{}".format(start, end)), start]


@register.simple_tag
def get_certificate_link(url, pk_training, pk_id):
    return str("{}/{}/{}".format(url, pk_training, pk_id))


@register.simple_tag
def get_convocation_link(url, token):
    return str("{}/{}".format(url, token))


@register.simple_tag
def check_if_deadline(deadline_at, today):
    deadline_at_formatted = datetime.strptime(deadline_at, '%B %d, %Y').date()
    if today <= deadline_at_formatted:
        return True
    else:
        return False


@register.simple_tag
def encode_url_base64(pk):
    data = urlsafe_base64_encode(force_bytes(pk))
    return data


@register.simple_tag
def get_card_color(count):
    colors = ["indigo", "maroon", "lightblue", "orange", "navy",
              "purple", "teal", "fuchsia", "olive", "pink"]
    return colors[count % len(colors)]


@register.simple_tag
def getempbyuser(user_id):
    return Empprofile.objects.filter(pi__user_id=user_id).first()


@register.simple_tag
def checkiffileexists(filepath):
    return Path(os.path.realpath('{}{}'.format(settings.BASE_DIR, filepath))).exists()
