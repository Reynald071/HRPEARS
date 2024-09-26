from django.urls import path

from backend.settings.views import portal_settings, portal_api_logs, portal_configuration, portal_configuration_delete, \
    portal_permission, portal_configuration_update, update_portal_permission, delete_portal_permission, \
    delete_portal_user_permission, patch_notes, edit_patch_notes

urlpatterns = [
    path('settings/', portal_settings, name='portal_settings'),
    path('api/logs/', portal_api_logs, name='portal_api_logs'),
    path('configuration/', portal_configuration, name='portal_configuration'),
    path('configuration/delete/', portal_configuration_delete, name='portal_configuration_delete'),
    path('configuration/update/', portal_configuration_update, name='portal_configuration_update'),
    path('permission/', portal_permission, name='portal_permission'),
    path('permission/update/<int:pk>', update_portal_permission, name='update_portal_permission'),
    path('permission/delete/', delete_portal_permission, name='delete_portal_permission'),
    path('permission/user/remove/', delete_portal_user_permission, name='delete_portal_user_permission'),
    path('patch-notes/', patch_notes, name='patch_notes'),
    path('patch-notes/update/<int:pk>', edit_patch_notes, name='edit_patch_notes')
]