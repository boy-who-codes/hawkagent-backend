from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import RegisterSerializer, UserSerializer
from .models import User
import uuid

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()
        
        # We will always print a reset link to the console for testing purposes, 
        # even if the user doesn't exist, to prevent confusion.
        token = uuid.uuid4().hex
        reset_link = f"http://localhost:3000/reset-password?token={token}&email={email}"
        
        print("\n" + "="*50)
        print("🔔 NEW PASSWORD RESET REQUEST")
        print(f"For User: {email} (Exists: {bool(user)})")
        print(f"Reset Link: {reset_link}")
        print("="*50 + "\n")
            
        # Always return success to prevent user enumeration
        return Response({'message': 'If an account exists, a reset link has been sent to the console.'})
