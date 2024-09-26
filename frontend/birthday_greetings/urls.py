from django.urls import path

from frontend.birthday_greetings.views import birthday_greetings

urlpatterns = [
    path('birthday-greetings/<str:pk>', birthday_greetings, name='birthday_greetings')
]
