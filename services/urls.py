from django.urls import path
from .views import  ServiceTypeListView
from .views import ServiceTypeDetailView

urlpatterns = [

    path('service-types/', ServiceTypeListView.as_view(), name='service-type-list'),
    path('service-types/<int:pk>/', ServiceTypeDetailView.as_view(), name='service-type-detail'),
]