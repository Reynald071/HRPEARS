from django.urls import path

from frontend.pas.profile.views import print_pds_pageone, print_pds_pagetwo, print_pds_pagethree, print_pds_pagefour, \
    print_pds_pagefive

urlpatterns = [
    path('print/1/<int:pk>', print_pds_pageone, name='print_pds_pageone'),
    path('print/2/<int:pk>', print_pds_pagetwo, name='print_pds_pagetwo'),
    path('print/3/<int:pk>', print_pds_pagethree, name='print_pds_pagethree'),
    path('print/4/<int:pk>', print_pds_pagefour, name='print_pds_pagefour'),
    path('print/5/<int:pk>', print_pds_pagefive, name='print_pds_pagefive'),
]