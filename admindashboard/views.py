from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from .serializers import UserSerializer

class CustomerListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            # Filter customers where role='user' AND isVerified=True
            customers = User.objects.filter(role='user', isVerified=True)
            # Use the serializer to convert the queryset to JSON
            serializer = UserSerializer(customers, many=True)
            return Response({"customers": serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": "Something went wrong while fetching customers.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
