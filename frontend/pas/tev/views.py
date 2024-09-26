from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from backend.models import Empprofile


@login_required
def track_tev(request):
    id_number = Empprofile.objects.filter(id=request.session['emp_id']).first()
    context = {
        'tab_title': 'Track TEV',
        'current_year': datetime.now().year,
        'id_number': id_number.id_number
    }
    return render(request, 'frontend/pas/tev/track_tev.html', context)