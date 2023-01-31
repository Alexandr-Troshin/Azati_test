from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .permissions import IsOwner
from .serializers import CustomUserCreateSerializer, CustomUserRetrieveSerializer,\
                            CustomUserUpdateFundsSerializer


User = get_user_model()


class CustomUsersCreateViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny, )
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer


class CustomUsersRetrieveViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр баланса пользователя."""
    permission_classes = [IsOwner, ]

    def get_queryset(self):
        return User.objects.filter(pk=self.request.parser_context['kwargs']['pk'])\
                            .filter(username=self.request.user)

    serializer_class = CustomUserRetrieveSerializer


class CustomUsersUpdateFundsViewSet(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    """Пополнение баланса пользователя. Товар income_stock дополняется income_qty"""
    permission_classes = [IsOwner, ]

    def get_queryset(self):
        return User.objects.filter(pk=self.request.parser_context['kwargs']['pk'])\
                                    .filter(username=self.request.user).first()

    serializer_class = CustomUserUpdateFundsSerializer

    def update(self, request, *args, **kwargs):
        serializer = CustomUserUpdateFundsSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        income_stock = serializer.validated_data.get('income_stock')
        income_qty = serializer.validated_data.get('income_qty')
        current_user = self.get_queryset()
        if income_stock in current_user.balance_of_funds:
            current_user.balance_of_funds[income_stock] += income_qty
        else:
            current_user.balance_of_funds[income_stock] = income_qty
        current_user.save()

        return Response({'message': f'{income_stock} increased on {income_qty}'},
                        status=status.HTTP_202_ACCEPTED)
