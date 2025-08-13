from django.urls import path
from .views import *

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/toggle-status/', ToggleUserStatusView.as_view(), name='toggle-user-status'),
    path('technicians/', TechnicianListView.as_view(), name='technician-list'),
    path('technicians/<int:user_id>/', TechnicianDetailView.as_view(), name='technician-detail'),
    path('service-categories/',ServiceCategoryListView.as_view(), name='service-category-list'),
    path('service-categories/<int:pk>/', ServiceCategoryDetailView.as_view(),name='service-category-detail'),
    path('bookings/', AdminBookingsView.as_view(), name='admin-bookings'),
    path('bookings/<int:booking_id>/update-status/', UpdateBookingStatusView.as_view(), name='update-booking-status'),
    path('wallet/', AdminWalletView.as_view(), name='admin-wallet'),

]