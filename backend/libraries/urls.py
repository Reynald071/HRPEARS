from django.urls import path, include

from .directory.views import detailtype, DirectoryDetailTypeUpdate
from .documents.views import sop_class, SopClassUpdate, docs_201_type, Docs201TypeUpdate, issuances_type,\
    IssuancesTypeUpdate, dl_class, DlClassUpdate
from .tracking.views import doctype, DtsDoctypeUpdate
from .grievance.views import classification, GrievanceClassificationUpdate, GrievanceMediaUpdate, media, \
    GrievanceStatusUpdate, status
from .leave.views import leave_type, LeavetypeUpdate, leave_subtype, LeavesubtypeUpdate, leave_spent, LeavespentUpdate
from .pis.views import bloodtype, BloodtypeUpdate, civilstatus, CivilstatusUpdate, hobbies, HobbiesUpdate, \
    degree, DegreeUpdate, educationlevel, EducationlevelUpdate, eligibility, EligibilityUpdate, honors, HonorsUpdate, \
    school, SchoolUpdate, brgy, BrgyUpdate, city, CityUpdate, province, ProvinceUpdate, countries, CountryUpdate, \
    organization, OrganizationUpdate, nonacad, NonacadUpdate, trainingtitle, TrainingtitleUpdate, trainingtype, \
    TrainingtypeUpdate, find_merges, merge_degree, merge_organization, merge_honors, merge_schools, \
    merge_trainingtitles, merge_eligibilities, merge_positions, merge_hobbies, merge_nonacads
from .hrppms.views import fundsource, FundsourceUpdate, aoa, AoaUpdate, project, ProjectUpdate, empstatus,\
    EmpstatusUpdate, position, PositionUpdate, mode_accession, mode_accessionUpdate, mode_separation,\
    mode_separationUpdate

urlpatterns = [
    path('directory/detail-types/', detailtype, name='detail-type'),
    path('directory/detail-types/update/<int:pk>', DirectoryDetailTypeUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'directory', 'sub_sub_title': 'detailtype'}),
        name='detail-type-update'),


]

