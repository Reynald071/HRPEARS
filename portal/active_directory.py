import ssl
from datetime import date, datetime
import ldap3
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from ldap3 import Server, ALL, Connection, MODIFY_REPLACE

from backend.models import Logs, PortalErrorLogs, PortalSuccessLogs
from portal import global_variables


def searchSamAccountName(username):
    USER = "{}@ENTDSWD.LOCAL".format(username)
    BASEDN = global_variables.BASE_DN
    s = Server(global_variables.AD_SERVER, get_info=ALL,
               use_ssl=False)

    c = Connection(s,
                   user=global_variables.AD_USER,
                   password=global_variables.AD_PASSWORD, auto_bind=True)

    SEARCHFILTER = '(&(userPrincipalName=' + USER + ')(objectClass=person))'
    USER_DN = ""
    USER_CN = ""
    c.search(search_base=BASEDN,
             search_filter=SEARCHFILTER,
             search_scope=ldap3.SUBTREE,
             attributes=['cn', 'givenName', 'userPrincipalName'],
             paged_size=5)

    for entry in c.response:
        if entry.get("dn") and entry.get("attributes"):
            if entry.get("attributes").get("userPrincipalName"):
                if entry.get("attributes").get("userPrincipalName") == USER:
                    USER_DN = entry.get("dn")
                    USER_CN = entry.get("attributes").get("cn")

    if USER_DN and USER_CN:
        return {"status": True, "connection": c, "userDN": USER_DN}
    else:
        return {"status": False}


@login_required
def get_password_countdown(request, username):
    USER = "{}@ENTDSWD.LOCAL".format(username)
    BASEDN = global_variables.BASE_DN
    s = Server(global_variables.AD_SERVER, get_info=ALL,
               use_ssl=False)

    c = Connection(s,
                   user=global_variables.AD_USER,
                   password=global_variables.AD_PASSWORD, auto_bind=True)

    SEARCHFILTER = '(&(userPrincipalName=' + USER + ')(objectClass=person))'
    USER_DN = ""
    USER_CN = ""
    c.search(search_base=BASEDN,
             search_filter=SEARCHFILTER,
             search_scope=ldap3.SUBTREE,
             attributes=['pwdLastSet', 'userAccountControl'],
             paged_size=5)

    password_last_set = ""
    user_account_control = ""

    for entry in c.response:
        password_last_set = entry.get("attributes").get("pwdLastSet")
        user_account_control = entry.get("attributes").get("userAccountControl")

    countdown_message = ''
    if user_account_control == 512:
        start_date = date.today()
        end_date = date(int(password_last_set.strftime('%Y')), int(password_last_set.strftime('%m')),
                        int(password_last_set.strftime('%d')))
        total = start_date - end_date
        total = 90 - total.days
        if 15 <= total <= 90:
            countdown_message = '<div class="alert alert-info"><strong>Caraga PORTAL</strong><br> Your password ' \
                                'expires in {} days.</div>'.format(total)
        elif 1 < total <= 14:
            countdown_message = '<div class="alert alert-warning"><strong>Caraga PORTAL</strong><br> Your password ' \
                                'expires in {} days. <a href="/my-profile/#settings">reset it now.</a></div>'\
                .format(total)
        elif total < 0:
            countdown_message = '<div class="alert alert-error"><strong>Caraga PORTAL</strong><br> Your password ' \
                                'expired {} days ago. <a href="/my-profile/#settings">reset it now.</a></div>'\
                .format(abs(total))
            # AuthUser.objects.filter(username=username).update(is_active=0)

    return JsonResponse({"countdown_message": countdown_message})


@login_required
@permission_required('auth.edit_employee')
def get_user_attribute(request, username):
    user = searchSamAccountName(username)

    if user["status"]:
        USER = "{}@ENTDSWD.LOCAL".format(username)
        BASEDN = global_variables.BASE_DN
        s = Server(global_variables.AD_SERVER, get_info=ALL,
                   use_ssl=False)

        c = Connection(s,
                       user=global_variables.AD_USER,
                       password=global_variables.AD_PASSWORD, auto_bind=True)

        SEARCHFILTER = '(&(userPrincipalName=' + USER + ')(objectClass=person))'
        USER_DN = ""
        USER_CN = ""
        c.search(search_base=BASEDN,
                 search_filter=SEARCHFILTER,
                 search_scope=ldap3.SUBTREE,
                 attributes=['*'],
                 paged_size=5)

        id_number = ""
        first_name = ""
        last_name = ""
        initials = ""
        display_name = ""
        telephone_number = ""
        email = ""
        job_title = ""
        department = ""
        ad_username = ""
        last_updated_on = ""
        password_last_set = ""
        user_account_control = ""

        for entry in c.response:
            id_number = entry.get("attributes").get("employeeID")
            first_name = entry.get("attributes").get("givenName")
            last_name = entry.get("attributes").get("sn")
            initials = entry.get("attributes").get("initials")
            display_name = entry.get("attributes").get("displayName")
            telephone_number = entry.get("attributes").get("telephoneNumber")
            email = entry.get("attributes").get("mail")
            job_title = entry.get("attributes").get("title")
            department = entry.get("attributes").get("department")
            ad_username = entry.get("attributes").get("sAMAccountName")
            last_updated_on = entry.get("attributes").get("whenChanged")
            password_last_set = entry.get("attributes").get("pwdLastSet")
            user_account_control = entry.get("attributes").get("userAccountControl")

        total = 0
        countdown_message = ''
        if user_account_control == 512:
            start_date = date.today()
            end_date = date(int(password_last_set.strftime('%Y')), int(password_last_set.strftime('%m')),
                            int(password_last_set.strftime('%d')))
            total = start_date - end_date
            total = 90 - total.days
            if 15 <= total <= 90:
                countdown_message = '<div class="alert alert-info"><strong>Caraga PORTAL</strong><br> Your password ' \
                                    'expires in {} days.</div>'.format(total)
            elif 1 <= total <= 14:
                countdown_message = '<div class="alert alert-warning"><strong>Caraga PORTAL</strong><br> Your password ' \
                                    'expires in {} day. <a href="/my-profile/#settings">reset it now.</a></div>'\
                    .format(total)

        return JsonResponse({"first_name": first_name, "id_number": id_number, "last_name": last_name, "initials": initials,
                             "display_name": display_name, "telephone_number": telephone_number, "email": email,
                             "job_title": job_title, "department": department, "username": ad_username,
                             "last_updated_on": last_updated_on.strftime('%b %d, %Y'),
                             "password_last_set": password_last_set.strftime('%Y-%m-%d'),
                             "user_account_control": user_account_control, "total_days": total,
                             "countdown_message": countdown_message})
    else:
        return JsonResponse({'error': True})


def create_ad_account(id_number, first_name, middle_name, last_name, display_name, username, email, contact_number, position, department, emp_id):
    try:
        s = Server(global_variables.AD_SERVER, get_info=ALL,
                   use_ssl=False)

        c = Connection(s,
                       user=global_variables.AD_USER,
                       password=global_variables.AD_PASSWORD, auto_bind=True)

        if middle_name:
            c.add('CN={},OU=New Accounts,OU=Clients,OU=FO Caraga,DC=ENTDSWD,DC=LOCAL'.format(str(display_name)),
                  attributes={'objectClass': ['User', 'posixGroup', 'top'],
                              'sn': last_name,
                              'cn': display_name,
                              'givenName': first_name,
                              'initials': middle_name[:1],
                              'gidNumber': emp_id,
                              'employeeID': id_number,
                              'displayName': display_name,
                              'userPrincipalName': username + '@ENTDSWD.LOCAL',
                              'sAMAccountName': username,
                              'mail': email,
                              'telephoneNumber': contact_number,
                              'title': position,
                              'department': department,
                              'company': 'DSWD Field Office Caraga',
                              'pwdLastSet': "-1"
                              })
        else:
            c.add('CN={},OU=New Accounts,OU=Clients,OU=FO Caraga,DC=ENTDSWD,DC=LOCAL'.format(str(display_name)),
                  attributes={'objectClass': ['User', 'posixGroup', 'top'],
                              'sn': last_name,
                              'cn': display_name,
                              'givenName': first_name,
                              'gidNumber': emp_id,
                              'employeeID': id_number,
                              'displayName': display_name,
                              'userPrincipalName': username + '@ENTDSWD.LOCAL',
                              'sAMAccountName': username,
                              'mail': email,
                              'telephoneNumber': contact_number,
                              'title': position,
                              'department': department,
                              'company': 'DSWD Field Office Caraga',
                              'pwdLastSet': "-1"
                              })

        if c.result['result'] == 19:
            PortalErrorLogs.objects.create(
                logs="AD Account Creation: {}".format(c.result),
                date_created=datetime.now(),
                emp_id=emp_id
            )
        else:
            PortalSuccessLogs.objects.create(
                logs="AD Account Creation: {}".format(c.result),
                date_created=datetime.now(),
                emp_id=emp_id,
                type='ad_creation'
            )

        user = searchSamAccountName(username)

        if user["status"]:
            enc_pwd = '"{}"'.format(id_number).encode('utf-16-le')
            user["connection"].modify(user["userDN"], {'unicodePwd': [(MODIFY_REPLACE, [enc_pwd])]})
            user["connection"].modify(user["userDN"], {'userAccountControl': [(MODIFY_REPLACE, [512])]})

            c.extend.microsoft.add_members_to_groups(user["userDN"], ["CN=CRG_SSLVPN_GRP_ACL,OU=Groups,OU=FO Caraga,DC=ENTDSWD,DC=LOCAL"])
            results = c.result

            Logs.objects.create(
                logs=results
            )

            return results
    except Exception as e:
        PortalErrorLogs.objects.create(
            logs="AD Account Creation: {}".format(e),
            date_created=datetime.now(),
            emp_id=emp_id
        )
