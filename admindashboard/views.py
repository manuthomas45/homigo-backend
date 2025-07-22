from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from users.models import User
from .serializers import UserSerializer
from technicians.models import TechnicianDetails
from technicians.serializers import TechnicianDetailsSerializer
from admindashboard.permissions import IsAdminRole
from django.db.models import Q
from technicians.models import ServiceCategory
from services.serializers import ServiceCategorySerializer
import logging
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser,FormParser
from django.db import IntegrityError  

logger=logging.getLogger('homigo')

class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        try:
            search_query = request.query_params.get('search', '')
            users = User.objects.filter(role='user')
            if search_query:
                users = users.filter(
                    Q(firstName__icontains=search_query) |
                    Q(lastName__icontains=search_query) |
                    Q(email__icontains=search_query)
                )
            serializer = UserSerializer(users, many=True)
            # print("Serialized Users Data:", serializer.data)
            return Response(
                {"success": True, "users": serializer.data},
                status=status.HTTP_200_OK
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

class ToggleUserStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, role='user')
            if user.status not in ['active', 'blocked']:
                user.status = 'active'  # Set a default status if not set
                user.save()
            user.status = 'blocked' if user.status == 'active' else 'active'
            user.save()
            serializer = UserSerializer(user)
            return Response(
                {
                    "success": True,
                    "message": f"User status updated to {user.status}",
                    "user": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"success": False, "error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"success": False, "error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TechnicianListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        try:
            search_query = request.query_params.get('search', '')
            technicians = User.objects.filter(role='technician')
            if search_query:
                technicians = technicians.filter(
                    Q(firstName__icontains=search_query) |
                    Q(lastName__icontains=search_query) |
                    Q(email__icontains=search_query)
                )
            serializer = UserSerializer(technicians, many=True)
            return Response(
                {"success": True, "technicians": serializer.data},
                status=status.HTTP_200_OK
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
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request, user_id):
        try:
            technician_details = TechnicianDetails.objects.get(user__id=user_id, user__role='technician')
            serializer = TechnicianDetailsSerializer(technician_details)
            return Response(
                {"success": True, "technician": serializer.data},
                status=status.HTTP_200_OK
            )
        except TechnicianDetails.DoesNotExist:
            return Response(
                {"success": False, "error": "Technician details not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"success": False, "error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, user_id):
        try:
            technician_details = TechnicianDetails.objects.get(user__id=user_id, user__role='technician')
            technician_details.is_verified = not technician_details.is_verified
            technician_details.save()
            serializer = TechnicianDetailsSerializer(technician_details)
            return Response(
                {
                    "success": True,
                    "message": f"Technician verification status updated to {technician_details.is_verified}",
                    "technician": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except TechnicianDetails.DoesNotExist:
            return Response(
                {"success": False, "error": "Technician details not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"success": False, "error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, user_id):
        try:
            technician_details = TechnicianDetails.objects.get(user__id=user_id, user__role='technician')
            # Toggle status: if 'blocked', set to 'active'; otherwise, set to 'blocked'
            technician_details.status = 'blocked' if technician_details.status != 'blocked' else 'active'
            technician_details.save()
            serializer = TechnicianDetailsSerializer(technician_details)
            return Response(
                {
                    "success": True,
                    "message": f"Technician status updated to {technician_details.status}",
                    "technician": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except TechnicianDetails.DoesNotExist:
            return Response(
                {"success": False, "error": "Technician details not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"success": False, "error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


class ServiceCategoryListView(APIView):
    # permission_classes = [IsAuthenticated, IsAdminRole]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        try:
            service_categories = ServiceCategory.objects.all()
            serializer = ServiceCategorySerializer(service_categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching service categories: {str(e)}")
            return Response(
                {"error": "Failed to fetch service categories"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        try:
            # The serializer will automatically handle the file from request.FILES
            serializer = ServiceCategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            logger.error(f"Serializer validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # except IntegrityError as e:
        #     logger.error(f"Error creating service category: {str(e)}")
        #     return Response(
        #         {"error": {"name": ["Name already exists"]}},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        except Exception as e:
            logger.error(f"Error creating service category: {str(e)}")
            return Response(
                {"error": "Failed to create service category"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ServiceCategoryDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    parser_classes = [MultiPartParser, FormParser]

    def delete(self, request, pk):
        try:
            logger.info(f"{pk}")
            service_category = ServiceCategory.objects.get(pk=pk)
            service_category.delete()
            return Response(
                {"message": "Service category deleted successfully."}, 
                status=status.HTTP_204_NO_CONTENT
            )
        except ServiceCategory.DoesNotExist:
            return Response(
                {"error": "Service category not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting service category: {str(e)}")
            return Response(
                {"error": "Failed to delete service category"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, pk):
        try:
            category = get_object_or_404(ServiceCategory, pk=pk)
            
            # The serializer will automatically handle the file from request.FILES
            serializer = ServiceCategorySerializer(
                category, 
                data=request.data, 
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            logger.error(f"Serializer validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except ServiceCategory.DoesNotExist:
            return Response(
                {"error": "Service category not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating service category: {str(e)}")
            return Response(
                {"error": "Failed to update service category"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )