from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Technician
from .serializers import TechnicianSerializer, TechnicianLoginSerializer, TechnicianResponseSerializer

class TechnicianRegisterView(APIView):
    def post(self, request):
        serializer = TechnicianSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Technician registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)