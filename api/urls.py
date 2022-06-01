from django.urls import path

from .views import RegistrationStatus

urlpatterns = [
    path("registrationStatus", RegistrationStatus.as_view()),
]
