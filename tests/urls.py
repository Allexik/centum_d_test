from django.urls import path
from .views import TestListView, TestDetailView, TestCreateView, TestUpdateView, TestDeleteView, TestPassView, \
    TestResultsView, TestResultView, TestCommentView

urlpatterns = [
    path('', TestListView.as_view(), name='test_list'),
    path('<int:pk>/', TestDetailView.as_view(), name='test_detail'),
    path('create/', TestCreateView.as_view(), name='test_create'),
    path('<int:pk>/edit/', TestUpdateView.as_view(), name='test_update'),
    path('<int:pk>/delete/', TestDeleteView.as_view(), name='test_delete'),
    path('<int:pk>/comment/', TestCommentView.as_view(), name='test_comment'),
    path('<int:pk>/pass/', TestPassView.as_view(), name='test_pass'),
    path('results/', TestResultsView.as_view(), name='test_results'),
    path('results/<int:pk>/', TestResultView.as_view(), name='test_result'),
]
