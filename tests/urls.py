from django.urls import path
from .views import TestListView, TestDetailView, TestCreateView, TestUpdateView, TestDeleteView

urlpatterns = [
    path('', TestListView.as_view(), name='test_list'),
    path('<int:pk>/', TestDetailView.as_view(), name='test_detail'),
    path('create/', TestCreateView.as_view(), name='test_create'),
    path('<int:pk>/edit/', TestUpdateView.as_view(), name='test_update'),
    path('<int:pk>/delete/', TestDeleteView.as_view(), name='test_delete'),
]
