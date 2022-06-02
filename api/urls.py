from django.urls import path

from .views import RegistrationStatus, SimilarDomains

urlpatterns = [
    path("registrationStatus", RegistrationStatus.as_view()),
    path("similarDomains", SimilarDomains.as_view()),
]
