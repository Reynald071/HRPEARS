from django.urls import path

from api.personnel.leave.views import LeaveViews, LeaveAdminViews, CTDOViews, LeaveCertificationTransactionViews, \
    CTDOAdminViews, CTDOBalanceViews

urlpatterns = [
    path("application/", LeaveViews.as_view(), name='api_leave'),
    path("application/admin/", LeaveAdminViews.as_view(), name='api_leave_admin'),
    path("ctdo/", CTDOViews.as_view(), name='api_ctdo'),
    path("ctdo/admin/", CTDOAdminViews.as_view(), name='api_ctdo_admin'),
    path('certification/transaction/', LeaveCertificationTransactionViews.as_view(), name='api_lv_certification_transaction'),
    path('coc/balance/', CTDOBalanceViews.as_view(), name='api_coc_balance')
]