from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import ServiceCategory, TechnicianDetails
from .serializers import ServiceCategorySerializer, TechnicianDetailsSerializercreate,TechnicianDetailsSerializer
from users.serializers import *
import logging
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