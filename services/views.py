from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ServiceType
from .serializers import ServiceTypeSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
import logging

logger = logging.getLogger('homigo')
from admindashboard.permissions import IsAdminRole

class ServiceTypeListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        try:
            service_types = ServiceType.objects.all().select_related('category')
            serializer = ServiceTypeSerializer(service_types, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching service types: {str(e)}")
            return Response(
                {"error": "Failed to fetch service types", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        try:
            logger.info("Received POST data: %s", request.data)
            serializer = ServiceTypeSerializer(data=request.data)
            
            if serializer.is_valid():
                try:
                    instance = serializer.save()
                    if instance is None:
                        raise Exception("Serializer.save() returned None")
                    
                    # Return the serialized data of the created instance
                    response_serializer = ServiceTypeSerializer(instance)
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                    
                except IntegrityError as e:
                    logger.error(f"Integrity error creating service type: {str(e)}")
                    return Response(
                        {"non_field_errors": ["The combination of category and name must be unique."]},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                logger.error(f"Serializer validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error creating service type: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to create service type", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ServiceTypeDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, pk):
        try:
            service_type = get_object_or_404(ServiceType, pk=pk)
            serializer = ServiceTypeSerializer(service_type, data=request.data, partial=True)
            
            if serializer.is_valid():
                try:
                    updated_instance = serializer.save()
                    # Return the serialized data of the updated instance
                    response_serializer = ServiceTypeSerializer(updated_instance)
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                    
                except IntegrityError as e:
                    logger.error(f"Integrity error updating service type: {str(e)}")
                    return Response(
                        {"non_field_errors": ["The combination of category and name must be unique."]},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                logger.error(f"Serializer validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except ServiceType.DoesNotExist:
            return Response({"error": "Service type not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating service type: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to update service type", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        try:
            service_type = get_object_or_404(ServiceType, pk=pk)
            service_type.delete()
            return Response({"message": "Service type deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except ServiceType.DoesNotExist:
            return Response({"error": "Service type not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting service type: {str(e)}", exc_info=True)
            return Response({"error": "Failed to delete service type"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)