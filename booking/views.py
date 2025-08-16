import stripe
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
from .models import Booking
from .serializers import BookingSerializer
from django.contrib.auth.models import User
from technicians.models import ServiceCategory
import traceback
import json
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': data.get('service_name'),
                            'description': f"Category: {data.get('category_name')} | Date: {data.get('booking_date')}",
                        },
                        'unit_amount': int(float(data.get('amount')) * 100),  # Convert to paise
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=data.get('success_url') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=data.get('cancel_url'),
                customer_email=request.user.email,
                metadata={
                    'service_type_id': str(data.get('service_type_id')),
                    'category_id': str(data.get('category_id')), 
                    'user_id': str(request.user.id),
                    'address_id': str(data.get('address_id')),
                    'booking_date': data.get('booking_date'),
                    'category_name': data.get('category_name'),
                    'service_name': data.get('service_name'),
                    'amount': str(data.get('amount')), 
                }
            )
            
            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            }, status=status.HTTP_200_OK)
            
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class CreatePaymentIntentView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         amount = int(float(request.data.get('amount')) * 100)  # Convert to cents
#         try:
#             payment_intent = stripe.PaymentIntent.create(
#                 amount=amount,
#                 currency='inr',
#                 payment_method_types=['card'],
#                 description=f"Booking for {request.data.get('service_name')}",
#                 receipt_email=request.user.email,
#             )
#             return Response({
#                 'clientSecret': payment_intent['client_secret'],
#                 'paymentIntentId': payment_intent['id']
#             }, status=status.HTTP_200_OK)
#         except stripe.error.StripeError as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        session_id = request.data.get("session_id")
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=400)
        try:
            # Retrieve the Stripe session using session_id
            session = stripe.checkout.Session.retrieve(session_id)

            print("="*50)
            print("STRIPE SESSION DEBUG")
            print(f"Session ID: {session_id}")
            print(f"Payment Status: {session.payment_status}")
            print(f"Amount Total: {session.amount_total}")
            print(f"Metadata: {session.metadata}")
            print("="*50)

            # Extract booking data from Stripe metadata
            metadata = session.metadata

            if session.payment_status != "paid":
                return Response({'error': 'Payment not completed.'}, status=status.HTTP_400_BAD_REQUEST)
            
            category_name = metadata.get('category_name')
            category = ServiceCategory.objects.filter(name=category_name).first()

            if not category:
                return Response({'error': f"ServiceCategory with name '{category_name}' not found."}, status=400)
            
            data = {
                'category': category.id,
                'service_type': metadata.get('service_type_id'),
                'address': metadata.get('address_id'),
                'amount': float(session.amount_total) / 100,  # Stripe stores in paisa
                'booking_date': metadata.get('booking_date'),
                'status': 'booked',
                'user': request.user.id  # Set current user
            }

            print(f"Booking Data from Stripe: {data}")
            serializer = BookingSerializer(data=data)

            if serializer.is_valid():
                booking = serializer.save()
                print(f"Booking created successfully: {booking}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print("Validation failed")
                print(serializer.errors)
                return Response({'errors': serializer.errors, 'received_data': data}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            return Response({'error': f"Stripe error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            traceback.print_exc()
            return Response({'error': f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch bookings for the authenticated user with related data
            bookings = Booking.objects.filter(user=request.user).select_related(
                'category', 'service_type', 'address', 'technician__user'
            )

            # Construct response data manually
            bookings_data = []
            for booking in bookings:
                booking_data = {
                    'id': booking.id,
                    'category': {
                        'name': booking.category.name if booking.category else 'N/A'
                    },
                    'service_type': {
                        'name': booking.service_type.name if booking.service_type else 'N/A'
                    },
                    'address': {
                        'address': booking.address.address if booking.address else 'N/A',
                        'city': booking.address.city if booking.address else 'N/A',
                        'state': booking.address.state if booking.address else 'N/A',
                        'pincode': booking.address.pincode if booking.address else 'N/A',
                        'phone_number': booking.address.phone_number if booking.address else 'N/A'
                    },
                    'status': booking.status or 'N/A',
                    'amount': str(booking.amount) if booking.amount is not None else '0.00',
                    'booking_date': booking.booking_date.strftime('%Y-%m-%d') if booking.booking_date else 'N/A',
                    'technician': None
                }
                if booking.technician:
                    booking_data['technician'] = {
                        'user': {
                            'firstName': booking.technician.user.firstName if booking.technician.user else 'N/A',
                            'lastName': booking.technician.user.lastName if booking.technician.user else 'N/A',
                            'email': booking.technician.user.email if booking.technician.user else 'N/A',
                            'phoneNumber': booking.technician.user.phoneNumber if booking.technician.user else 'N/A'
                        },
                        'city': booking.technician.city if booking.technician else 'N/A',
                        'is_verified': booking.technician.is_verified if booking.technician else False
                    }
                bookings_data.append(booking_data)

            # Include wallet_balance in the response
            response_data = {
                'wallet_balance': str(request.user.wallet_balance) if request.user.wallet_balance is not None else '0.00',
                'bookings': bookings_data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"User Bookings Error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            # Fetch the booking for the authenticated user
            booking = Booking.objects.get(pk=pk, user=request.user)
            
            # Check if booking has an assigned technician
            if booking.technician is not None:
                return Response(
                    {"error": "Cannot cancel booking with an assigned technician"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if booking is already cancelled or completed
            if booking.status in ['cancelled', 'completed']:
                return Response(
                    {"error": "Booking cannot be cancelled"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use transaction to ensure atomicity
            with transaction.atomic():
                # Update booking status
                booking.status = 'cancelled'
                booking.save()
                
                # Add booking amount to user's wallet balance
                if booking.amount is not None:
                    try:
                        amount = Decimal(str(booking.amount))  # Ensure amount is Decimal
                        booking.user.wallet_balance += amount
                        booking.user.save(update_fields=['wallet_balance'])
                    except (ValueError, TypeError):
                        return Response(
                            {"error": "Invalid booking amount"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
            return Response(
                {"message": "Booking cancelled successfully and amount added to wallet"},
                status=status.HTTP_200_OK
            )
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found or you do not have permission"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to cancel booking: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Complaint, Booking
from .serializers import ComplaintSerializer
from django.db import transaction

class SubmitComplaintView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            with transaction.atomic():
                booking_id = request.data.get('booking')
                booking = Booking.objects.get(id=booking_id, user=request.user, status='completed')
                if not booking:
                    return Response({"error": "Invalid or incomplete booking"}, status=status.HTTP_400_BAD_REQUEST)
                
                data = {
                    'booking': booking.id,
                    'user': request.user.id,
                    'technician': booking.technician.id if booking.technician else None,
                    'category': booking.category.id,
                    'service_type': booking.service_type.id,
                    'title': request.data.get('title'),
                    'description': request.data.get('description')
                }
                
                serializer = ComplaintSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message": "Complaint submitted successfully"}, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found or not completed"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)