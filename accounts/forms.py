from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileForm(forms.ModelForm):
    profile_image = forms.ImageField(required=False, widget=forms.FileInput())
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 6}))

    clear_profile_image = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(), initial=False, label='Clear:'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = self.instance.profile
        if profile:
            self.fields['profile_image'].initial = profile.profile_image
            self.fields['birth_date'].initial = profile.birth_date
            self.fields['bio'].initial = profile.bio

    def save(self, commit=True):
        profile = self.instance.profile
        if self.cleaned_data['clear_profile_image']:
            profile.profile_image.delete()
            profile.profile_image = None
        else:
            profile.profile_image = self.cleaned_data['profile_image'] or None
        profile.birth_date = self.cleaned_data['birth_date'] or None
        profile.bio = self.cleaned_data['bio']
        if commit:
            profile.save()
            self.instance.save()
        return self.instance
