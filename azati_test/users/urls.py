from django.urls import path, include
from .views import CustomUsersCreateViewSet, CustomUsersRetrieveViewSet, \
                    CustomUsersUpdateFundsViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
#    path('', include('djoser.urls')),

    path('register/', CustomUsersCreateViewSet.as_view({'post': 'create'}), name="register"),
    path('user/<int:pk>/', CustomUsersRetrieveViewSet.as_view({'get': 'retrieve'}),
                                                                name="user_detail"),
    path('user/<int:pk>/updatefunds/', CustomUsersUpdateFundsViewSet.as_view({'post': 'update'}),
                                                                            name="user_update_funds"),
    path('br/', include('rest_framework.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]