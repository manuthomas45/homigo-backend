from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import ServiceCategory, TechnicianDetails
from .serializers import ServiceCategorySerializer, TechnicianDetailsSerializercreate,TechnicianDetailsSerializer
from users.serializers import *
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from booking.models import Booking
from technicians.models import TechnicianDetails
logger=logging.getLogger('homigo')

class ServiceCategoryListView(generics.ListAPIView):
    
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticated]

class TechnicianRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Check if user is already a technician
            if request.user.role == 'technician':
                return Response(
                    {
                        "success": False,
                        "error": "You are already registered as a technician"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if user already has TechnicianDetails
            if TechnicianDetails.objects.filter(user=request.user).exists():
                return Response(
                    {
                        "success": False,
                        "error": "Technician details already exist for this user"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate and save technician details
            serializer = TechnicianDetailsSerializercreate(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                # Serialize the updated user data
                user_serializer = UserSerializer(request.user)
                return Response(
                    {
                        "success": True,
                        "message": "Successfully registered as a technician",
                        "user": user_serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {
                    "success": False,
                    "error": "Validation failed",
                    "details": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": "An unexpected error occurred",
                    "details": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class TechnicianDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if the user has the technician role
        if request.user.role != 'technician':
            return Response({"error": "Unauthorized: User is not a technician"}, status=status.HTTP_403_FORBIDDEN)

        try:
            # Fetch the technician detail for the authenticated user
            technician_detail = TechnicianDetails.objects.get(user=request.user)
            serializer = TechnicianDetailsSerializer(technician_detail)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TechnicianDetails.DoesNotExist:
            return Response({"error": "Technician details not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TechnicianUserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if the user has the technician role
        if request.user.role != 'technician':
            return Response({"error": "Unauthorized: User is not a technician"}, status=status.HTTP_403_FORBIDDEN)

        try:
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def put(self, request):
        if request.user.role != 'technician':
            return Response({"error": "Unauthorized: User is not a technician"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = request.user
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class TechnicianBookingsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Check if user is a technician
            try:
                technician = TechnicianDetails.objects.get(user=request.user)
            except TechnicianDetails.DoesNotExist:
                return Response({'error': 'User is not a technician'}, status=status.HTTP_403_FORBIDDEN)
            
            # Get search query if provided
            search_query = request.GET.get('search', '')
            
            # CATEGORY VALIDATION: Only show bookings that match technician's category
            available_bookings_query = Booking.objects.filter(
                technician__isnull=True,
                status__in=['pending', 'booked'],
                category=technician.category,  # ✅ This ensures same category
                service_type__category=technician.category  # ✅ Double check service_type category matches
            ).select_related('user', 'service_type', 'category', 'address')
            
            if search_query:
                available_bookings_query = available_bookings_query.filter(
                    Q(user__firstName__icontains=search_query) |
                    Q(user__lastName__icontains=search_query) |
                    Q(service_type__name__icontains=search_query) |
                    Q(address__city__icontains=search_query)
                )
            
            bookings = []
            for booking in available_bookings_query.order_by('-id'):
                # ✅ Additional validation check
                if booking.category.id != technician.category.id or booking.service_type.category.id != technician.category.id:
                    continue  # Skip this booking if categories don't match
                    
                booking_data = {
                    'id': booking.id,
                    'customer_name': f"{booking.user.firstName} {booking.user.lastName}",
                    'customer_email': booking.user.email,
                    'city': booking.address.city,
                    'amount': str(booking.amount),
                    'booking_date': booking.booking_date.strftime('%Y-%m-%d') if booking.booking_date else None,
                    'service_type': booking.service_type.name,
                    'category': booking.category.name,
                    'status': booking.status,
                    'technician_category': technician.category.name,  # ✅ Add for debugging
                    'address': {
                        'id': booking.address.id,
                        'address': booking.address.address,
                        'city': booking.address.city,
                        'state': booking.address.state,
                        'pincode': booking.address.pincode,
                        'phone_number': booking.address.phone_number,
                    }
                }
                bookings.append(booking_data)
            
            return Response({
                'success': True,
                'bookings': bookings,
                'technician_category': technician.category.name  # ✅ Add for frontend reference
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Technician Bookings Error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class TechnicianAcceptedBookingsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Check if user is a technician
            try:
                technician = TechnicianDetails.objects.get(user=request.user)
            except TechnicianDetails.DoesNotExist:
                return Response({'error': 'User is not a technician'}, status=status.HTTP_403_FORBIDDEN)
            
            # Get search query if provided
            search_query = request.GET.get('search', '')
            
            # Get accepted bookings (technician assigned, status confirmed)
            accepted_bookings_query = Booking.objects.filter(
                technician=technician,
                status='confirmed'
            ).select_related('user', 'service_type', 'category', 'address')
            
            if search_query:
                accepted_bookings_query = accepted_bookings_query.filter(
                    Q(user__firstName__icontains=search_query) |
                    Q(user__lastName__icontains=search_query) |
                    Q(service_type__name__icontains=search_query) |
                    Q(address__city__icontains=search_query)
                )
            
            bookings = []
            for booking in accepted_bookings_query.order_by('-id'):
                booking_data = {
                    'id': booking.id,
                    'customer_name': f"{booking.user.firstName} {booking.user.lastName}",
                    'customer_email': booking.user.email,
                    'city': booking.address.city,
                    'amount': str(booking.amount),
                    'booking_date': booking.booking_date.strftime('%Y-%m-%d') if booking.booking_date else None,
                    'service_type': booking.service_type.name,
                    'category': booking.category.name,
                    'status': booking.status,
                    'address': {
                        'id': booking.address.id,
                        'address': booking.address.address,
                        'city': booking.address.city,
                        'state': booking.address.state,
                        'pincode': booking.address.pincode,
                        'phone_number': booking.address.phone_number,
                    }
                }
                bookings.append(booking_data)
            
            return Response({
                'success': True,
                'bookings': bookings
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Technician Accepted Bookings Error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AcceptBookingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, booking_id):
        try:
            # Check if user is a technician
            try:
                technician = TechnicianDetails.objects.get(user=request.user)
            except TechnicianDetails.DoesNotExist:
                return Response({'error': 'User is not a technician'}, status=status.HTTP_403_FORBIDDEN)
            
            # Get the booking
            try:
                booking = Booking.objects.get(id=booking_id)
            except Booking.DoesNotExist:
                return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # ✅ COMPREHENSIVE CATEGORY VALIDATION
            print(f"Technician Category: {technician.category.name} (ID: {technician.category.id})")
            print(f"Booking Category: {booking.category.name} (ID: {booking.category.id})")
            print(f"Service Type Category: {booking.service_type.category.name} (ID: {booking.service_type.category.id})")
            
            # Check if all categories match
            if booking.category.id != technician.category.id:
                return Response({
                    'error': f'Category mismatch: Booking category ({booking.category.name}) does not match technician category ({technician.category.name})'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if booking.service_type.category.id != technician.category.id:
                return Response({
                    'error': f'Service category mismatch: Service type category ({booking.service_type.category.name}) does not match technician category ({technician.category.name})'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if booking is available (no technician assigned)
            if booking.technician is not None:
                return Response({'error': 'Booking already assigned to another technician'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if booking is in correct status
            if booking.status not in ['pending', 'booked']:
                return Response({'error': 'Booking is not available for acceptance'}, status=status.HTTP_400_BAD_REQUEST)
            
            # ✅ Final validation before assignment
            if not self.validate_category_match(booking, technician):
                return Response({
                    'error': 'Category validation failed: Technician cannot accept this booking'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Assign technician and update status
            booking.technician = technician
            booking.status = 'confirmed'
            booking.save()
            
            return Response({
                'success': True,
                'message': 'Booking accepted successfully',
                'booking': {
                    'id': booking.id,
                    'status': booking.status,
                    'technician_id': technician.id,
                    'category_match_confirmed': True
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Accept Booking Error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def validate_category_match(self, booking, technician):
        """
        ✅ Helper method to validate category matching
        """
        try:
            # Check if booking category matches technician category
            booking_category_match = booking.category.id == technician.category.id
            
            # Check if service type category matches technician category  
            service_category_match = booking.service_type.category.id == technician.category.id
            
            # Both must match
            return booking_category_match and service_category_match
            
        except Exception as e:
            print(f"Category validation error: {str(e)}")
            return False

class CompleteBookingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, booking_id):
        try:
            # Check if user is a technician
            try:
                technician = TechnicianDetails.objects.get(user=request.user)
            except TechnicianDetails.DoesNotExist:
                return Response({'error': 'User is not a technician'}, status=status.HTTP_403_FORBIDDEN)
            
            # Get the booking (must be assigned to this technician)
            try:
                booking = Booking.objects.get(id=booking_id, technician=technician)
            except Booking.DoesNotExist:
                return Response({'error': 'Booking not found or not assigned to you'}, status=status.HTTP_404_NOT_FOUND)
            
            # ✅ Additional category validation for completion
            if not self.validate_category_match(booking, technician):
                return Response({
                    'error': 'Category validation failed: Cannot complete this booking'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if booking is in confirmed status
            if booking.status != 'confirmed':
                return Response({'error': 'Booking is not in confirmed status'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update status to completed
            booking.status = 'completed'
            booking.save()
            
            return Response({
                'success': True,
                'message': 'Booking marked as completed successfully',
                'booking': {
                    'id': booking.id,
                    'status': booking.status
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Complete Booking Error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def validate_category_match(self, booking, technician):
        """
        ✅ Helper method to validate category matching
        """
        try:
            booking_category_match = booking.category.id == technician.category.id
            service_category_match = booking.service_type.category.id == technician.category.id
            return booking_category_match and service_category_match
        except Exception as e:
            print(f"Category validation error: {str(e)}")
            return False
        

class WalletView(APIView):
    