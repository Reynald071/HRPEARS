from django.urls import path

from backend.libraries.gamification.views import gamify_levels, GamifyLevelsUpdate, gamify_activities, \
    GamifyActivitiesUpdate

urlpatterns = [
    path('levels/', gamify_levels, name='gamify-levels'),
    path('levels/update/<int:pk>', GamifyLevelsUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'gamification', 'sub_sub_title': 'levels'}),
         name='gamify-levels-update'),
    path('activities/', gamify_activities, name='gamify-activities'),
    path('activities/update/<int:pk>', GamifyActivitiesUpdate.as_view(
        extra_context={'title': 'libraries', 'sub_title': 'gamification', 'sub_sub_title': 'activities'}),
         name='gamify-activities-update'),
]
