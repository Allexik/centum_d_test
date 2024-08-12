from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView

from accounts.forms import UserProfileForm
from tests.models import Test, Result

User = get_user_model()


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'pages/profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        tests = Test.objects.filter(user=self.request.user).order_by('-created_at')[:8]
        results = Result.objects.filter(user=self.request.user).order_by('-created_at')[:8]

        user = User.objects.prefetch_related(
            Prefetch('tests', queryset=tests, to_attr='latest_tests'),
            Prefetch('results', queryset=results, to_attr='latest_results')
        ).get(pk=self.request.user.pk)

        user.test_count = Test.objects.filter(user=user).count()
        user.result_count = Result.objects.filter(user=user).count()

        return user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'pages/profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user
