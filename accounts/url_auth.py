from django.urls import path
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from administration.models import ActivityLog
from administration.services import log_activity
from .serializers import CustomTokenObtainPairSerializer
from .views import AuthApiView, LogoutView, RegisterView


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        log_activity(request, ActivityLog.EventType.LOGIN, actor=serializer.user,
                     metadata={'method': 'password'})
        return Response(serializer.validated_data)


urlpatterns = [
    path('', AuthApiView.as_view(), name='auth-api'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
