from django.urls import path

from accounts.views import ProfileDetailView, ProfileEditView

urlpatterns = [
    path('profile/', ProfileDetailView.as_view(), name='profile'),
    path('profile-edit/', ProfileEditView.as_view(), name='profile_edit'),
]
