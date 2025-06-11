from django.urls import path
from .views import *

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/toggle-status/', ToggleUserStatusView.as_view(), name='toggle-user-status'),
    path('technicians/', TechnicianListView.as_view(), name='technician-list'),
    path('technicians/<int:user_id>/', TechnicianDetailView.as_view(), name='technician-detail'),
]