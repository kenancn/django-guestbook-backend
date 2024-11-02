from django.urls import path
from .views import GuestbookViewSet

urlpatterns = [
    path('entries/', GuestbookViewSet.as_view({'post': 'create', 'get': 'list'}), name='entries'),
    path('users-data/', GuestbookViewSet.as_view({'get': 'users_data'}), name='users-data'),
] 