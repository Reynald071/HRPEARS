from django.db.models import Q
from datetime import date
from backend.models import Aoa, Section
from dateutil import relativedelta
from frontend.models import Address, Educationbackground, Civilservice, \
    Workexperience, Civilstatus, Province, City, Brgy, Eligibility, Additional, Bloodtype


def get_bloodtype(pi_id):
    if pi_id is None:
        return ''
    else:
        bt = Bloodtype.objects.filter(id=pi_id).first()
        return bt.name if bt else ""


def get_civil_status(cs_id):
    if cs_id is None:
        return ''
    else:
        civil_status = Civilstatus.objects.filter(Q(id=cs_id)).first()
        if civil_status.name != 'Solo Parent':
            return civil_status.name
        else:
            return ''


def get_solo_parent(pi_id):
    if pi_id is None:
        return ''
    else:
        solo = Additional.objects.filter(pi_id=pi_id).last()
        return solo.answers if solo else ""


def get_section(sec_id):
    if sec_id is None:
        return ''
    else:
        section = Section.objects.filter(id=sec_id).first()
        return section.sec_name


def get_division(div_id):
    if div_id is None:
        return ''
    else:
        div = Section.objects.filter(id=div_id).first()
        return div.div.div_name


def get_aoa(aoa_id):
    if aoa_id is None:
        return ''
    else:
        aoa = Aoa.objects.filter(id=aoa_id).first()
        if aoa and aoa.name != 'Field Office X':
            return aoa.name
        else:
            return ''


def get_age(bdate):
    today = date.today()
    if bdate is None:
        return '0'
    else:
        age = relativedelta.relativedelta(today, bdate)
        return age.years


def get_senior(bdate):
    today = date.today()
    if bdate is None:
        return ''
    else:
        age = relativedelta.relativedelta(today, bdate)
        return 'Senior Citizen' if age.years >= 60 else ''


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
        return str(city.name) + ', ' + get_prov(city.prov_code_id)  if city else ""


def get_brgy(brgy):
    if brgy is None:
        return ''
    else:
        data = Brgy.objects.filter(id=brgy).first()
        return data.name if data else ""


def get_residentialadd(ids):
    if ids is None:
        return ''
    else:
        add = Address.objects.filter(pi_id=ids).first()
        return str(add.ra_house_no) + ', ' + str(add.ra_street) + ', ' + str(add.ra_village) + ', ' + get_brgy(add.ra_brgy) + ', ' + get_city(add.ra_city) if add else ""
        

def get_permanentadd(ids):
    if ids is None:
        return ''
    else:
        add = Address.objects.filter(pi_id=ids).first()
        return str(add.pa_house_no) + ', ' + str(add.pa_street) + ', ' + str(add.pa_village) + ', ' + get_brgy(add.pa_brgy) + ', ' + get_city(add.pa_city) if add else ""


def entry_first_indswd(ids):
    if ids is None:
        return ''
    else:
        woe = Workexperience.objects.filter(Q(pi_id=ids) & (Q(company__icontains='DSWD') | Q(
            company__icontains='Department of Social Welfare and Development'))).order_by('we_from').first()
        return woe.we_from if woe else ''


def filledup(ids):
    if ids is None:
        return ''
    else:
        woe = Workexperience.objects.filter(Q(pi_id=ids) & (Q(company__icontains='DSWD') | Q(
            company__icontains='Department of Social Welfare and Development'))).order_by('we_from').last()
        return woe.we_from if woe else ''


def get_civilservice(ids):
    if ids is None:
        return ''
    else:
        civilservice = Civilservice.objects.all().filter(pi_id =ids)
        for row in civilservice:
            eligibility = Eligibility.objects.all().filter(Q(id = row.el_id) & (~Q(el_name__icontains = 'RA 1080')) 
                                                            & (~Q(el_name__icontains = 'social worker')), (~Q(el_name__icontains = 'social work'))
                                                            & (~Q(el_name__icontains = 'LET')), (~Q(el_name__icontains = 'LICENSED PROFESSIONAL TEACHER')))
            for data in eligibility:
                return data.el_name if data else ""


def get_ra(ids):
    if ids is None:
        return ''
    else:
        ra = Civilservice.objects.filter(pi_id=ids)
        for row in ra:
            eligibility = Eligibility.objects.all().filter(Q(id=row.el_id) & (Q(el_name__icontains='RA 1080'))
                                                            &(~Q(el_name__icontains='social work')))
            for data in eligibility:
                return data.el_name if data else ""


def get_let(ids):
    if ids is None:
        return ''
    else:
        let = Civilservice.objects.filter(pi_id=ids)
        for row in let:
            eligibility = Eligibility.objects.all().filter(Q(id = row.el_id) & (Q(el_name__icontains = 'LET') | Q(el_name__icontains = 'LICENSED PROFESSIONAL TEACHER')))
            for data in eligibility:
                return data.el_name if data else ""


def getlevelof_elig(ids):
    if ids is None:
        return ''
    else:
        level = Civilservice.objects.filter(pi_id=ids).first()
        if level:
            elig = Eligibility.objects.filter(id = level.el_id).first()
            if elig.el_level == 1:
                return '1st Level'
            elif elig.el_level == 2:
                return '2nd Level'
            elif elig.el_level == 3:
                return '3rd Level' 
            else:
                return ""
            return elig if elig else ""


def geteducation_status(ids):
    if ids is None:
        return ''
    else:
        collegegrad = Educationbackground.objects.filter(Q(pi_id = ids) & Q(units_earned__icontains = 'Graduate') & (Q(level_id = 3) | Q(level_id = 5))).first()
        undergrad = Educationbackground.objects.filter(Q(pi_id = ids) & (Q(units_earned__icontains = 'n/a') | Q(units_earned__icontains = 'unit'))  & Q(level_id = 3)).first()
        highgrad = Educationbackground.objects.filter(Q(pi_id = ids) & Q(units_earned__icontains = 'Graduate') & Q(level_id = 2)).first()
        vocational = Educationbackground.objects.filter(Q(pi_id = ids) & Q(units_earned__icontains = 'Graduate') & Q(level_id = 4)).first()
        elem = Educationbackground.objects.filter(Q(pi_id = ids) & Q(units_earned__icontains = 'Graduate') & Q(level_id = 1)).first()
        if collegegrad:
            return 'College Graduate'
        elif highgrad:
            return 'High School Graduate'
        elif vocational:
            return 'Vocational Graduate'
        elif elem:
            return 'Elementary Graduate'
        elif undergrad:
            return 'Undergrad'
        else:
            return ""


def get_masters(ids):
    if ids is None:
        return ''
    else:
        masters = Educationbackground.objects.filter(Q(pi_id = ids) & Q(level_id = 5) & (Q(units_earned__icontains = 'master') | Q(degree__degree_name__icontains = 'master')))
        for row in masters:
            return row.degree.degree_name if row else ""


def get_firstdegree(ids):
    if ids is None:
        return ''
    else:
        masters = Educationbackground.objects.all().filter(Q(pi_id = ids) & (Q(units_earned__icontains = 'Graduate') | Q(units_earned__icontains = 'n/a') | Q(units_earned__icontains = 'unit')) 
                                                & Q(level_id = 3))[0:1]
        for row in masters:
            return row.degree.degree_name if row else ""


def get_lastdegree(ids):
    if ids is None:
        return ''
    else:
        masters = Educationbackground.objects.all().filter(Q(pi_id = ids) & (Q(units_earned__icontains = 'Graduate') | Q(units_earned__icontains = 'n/a') | Q(units_earned__icontains = 'unit')) 
                                                & Q(level_id = 3))[1:2]
        for row in masters:
            return row.degree.degree_name if row else ""


def get_otherdegree(ids):
    if ids is None:
        return ''
    else:
        masters = Educationbackground.objects.filter(Q(pi_id = ids) & Q(level_id = 4)).first()
        return masters.degree.degree_name if masters else ""