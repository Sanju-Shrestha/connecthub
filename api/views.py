from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import permissions
from .serializers import UserSerializer



class UserListAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):

        users = User.objects.all()

        serializer = UserSerializer(users, many=True, context={"request": request})

        return Response(serializer.data)