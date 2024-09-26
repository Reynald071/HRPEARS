from django.urls import path

from backend.pas.clearance.views import clearance_content, get_clearance_content, view_clearance_layout, get_credentials

urlpatterns = [
    path('content/', clearance_content, name='clearance_content'),
    path('content/get', get_clearance_content, name='get_clearance_content'),
    path('content/layout/<int:emp_id>/<int:id>', view_clearance_layout, name='view_clearance_layout'),
    path('content/credentials/get/<int:emp_id>', get_credentials, name='get_credentials')
]