from django.contrib.auth import get_user_model

from rest_framework import permissions, viewsets
from rest_framework.response import Response

from api.v1.serializers.user_serializer import CustomUserSerializer, BalanceSerializer

from users.models import Balance


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ["get", "head", "options"]
    permission_classes = (permissions.IsAdminUser,)


class BalanceViewSet(viewsets.ModelViewSet):
    serializer_class = BalanceSerializer
    permission_classes = [permissions.IsAdminUser]  # Доступ только для администраторов
    
    def get_queryset(self):
        return Balance.objects.all()

    def put(self, request):
        data = request.data

        try:
            instance = Balance.objects.get(user=data.get('user'))
        except:
            return Response({'error':'Object not exist!'})

        serializer = BalanceSerializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.update(validated_data=request.data, instance=instance)
        return Response({'Balance': serializer.data})
