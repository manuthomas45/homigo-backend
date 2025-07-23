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

import json
from django.http import JsonResponse

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
            import traceback
            traceback.print_exc()
            return Response({'error': f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
