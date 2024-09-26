from django.urls import path

from backend.ipcr.views import ipcr_encoding, ipcr_file, generate_ipcr_ranking, ipcr_details, select_ipcr_file, \
    generate_performance_rating, generate_drn_for_ipcr, update_performance_rating_drn, ipcr_certification

urlpatterns = [
    path('', ipcr_encoding, name='ipcr_encoding'),
    path('details/<int:pk>', ipcr_details, name='ipcr_details'),
    path('file/select/<int:pk>', select_ipcr_file, name='select_ipcr_file'),
    path('generate/ranking/', generate_ipcr_ranking, name='generate_ipcr_ranking'),
    path('generate/performance-rating/', generate_performance_rating, name='generate_performance_rating'),
    path('generate/performance-rating/drn/', generate_drn_for_ipcr, name='generate_drn_for_ipcr'),
    path('file/<int:pk>', ipcr_file, name='ipcr_file'),
    path('update/performance-rating/drn/', update_performance_rating_drn, name='update_performance_rating_drn'),
    path('certification', ipcr_certification, name='ipcr_certification'),
]