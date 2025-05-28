from django.urls import path
from .views import TechnicianRegisterView

urlpatterns = [
    path('register/', TechnicianRegisterView.as_view(), name='technician-register'),

]