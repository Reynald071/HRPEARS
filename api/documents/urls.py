from django.urls import path

from api.documents.views import Document201Views, DocumentIssuancesViews, RSOAttachmentViews

urlpatterns = [
    path('201-files/', Document201Views.as_view(), name='api_docs_201'),
    path('issuances/', DocumentIssuancesViews.as_view(), name='api_issuances'),
    path('rso/attachment/', RSOAttachmentViews.as_view(), name='api_rso')
]