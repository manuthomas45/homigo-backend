from django.urls import path
from .views import *

urlpatterns = [
    path('technician-register/', TechnicianRegisterView.as_view(), name='technician-register'),
    path('services/', ServiceCategoryListView.as_view(), name='service-category-list'),

]