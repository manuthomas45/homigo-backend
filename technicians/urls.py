from django.urls import path
from .views import *

urlpatterns = [
    path('technician-register/', TechnicianRegisterView.as_view(), name='technician-register'),
    path('services/', ServiceCategoryListView.as_view(), name='service-category-list'),
    path('details/', TechnicianDetailView.as_view(), name='technician-details'),
    path('user-details/', TechnicianUserDetailView.as_view(), name='technician-user-details'),
    path('bookings/available/', TechnicianBookingsView.as_view(), name='technician-available-bookings'),
    path('bookings/accepted/', TechnicianAcceptedBookingsView.as_view(), name='technician-accepted-bookings'),
    path('bookings/<int:booking_id>/accept/', AcceptBookingView.as_view(), name='accept-booking'),
    path('bookings/<int:booking_id>/complete/', CompleteBookingView.as_view(), name='complete-booking'),
    path('wallet/', TechnicianWalletView.as_view(), name='technician-wallet'),

]