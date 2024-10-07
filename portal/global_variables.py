from datetime import datetime
from functools import wraps

from django.http import HttpResponseForbidden
from pymongo import MongoClient

# Active Directory LDAP Connection

try:
    BASE_DN = "OU=Clients,OU=FO Caraga,DC=ENTDSWD,DC=LOCAL"
    AD_SERVER = "ldap://172.16.10.10:389"
    AD_USER = "CN=Active Directory Reader Account,OU=Service Accounts,OU=Restricted,OU=FO Caraga,DC=ENTDSWD,DC=LOCAL"
    AD_PASSWORD = "dswd123$"
except Exception as e:
    BASE_DN = "OU=Clients,OU=FO Caraga,DC=ENTDSWD,DC=LOCAL"
    AD_SERVER = "ldap://172.16.10.10:389"
    AD_USER = "CN=Active Directory Reader Account,OU=Service Accounts,OU=Restricted,OU=FO Caraga,DC=ENTDSWD,DC=LOCAL"
    AD_PASSWORD = "dswd123$"


# MongoDB
cluster = MongoClient('mongodb://172.31.240.127:27017')
db = cluster["portal"]


def count_leave_days(first_date, second_date):
    date_of_filing = datetime.strptime(str(first_date), "%Y-%m-%d %H:%M:%S")
    start_date = datetime.strptime(str(second_date), "%Y-%m-%d")
    days = (start_date - date_of_filing).days + 1
    return abs(days)


def any_permission_required(*perms):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check if user has any of the required permissions
            if any(request.user.has_perm(perm) for perm in perms):
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden()
        return _wrapped_view
    return decorator