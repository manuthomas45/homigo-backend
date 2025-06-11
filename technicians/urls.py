from django.urls import path
from .views import *

urlpatterns = [
    path('technician-register/', TechnicianRegisterView.as_view(), name='technician-register'),
    path('services/', ServiceCategoryListView.as_view(), name='service-category-list'),
    path('details/', TechnicianDetailView.as_view(), name='technician-details'),
    path('user-details/', TechnicianUserDetailView.as_view(), name='technician-user-details'),

]