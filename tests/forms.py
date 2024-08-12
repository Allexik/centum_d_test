from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import ngettext_lazy

from tests.models import Test, Question, Answer, Comment


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 1, 'required': True}),
        }


class AnswerForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ['letter', 'text', 'is_correct']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'required': True}),
            'letter': forms.HiddenInput(),
            'is_correct': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            index = self.prefix.split('-')[-1]
            self.fields['letter'].initial = Answer.LETTERS[int(index)][0]


class BaseQuestionFormSet(forms.BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        error_messages = kwargs.pop('error_messages', {})
        error_messages.setdefault('too_few_forms', ngettext_lazy(
            'Please submit at least %(num)d question.',
            'Please submit at least %(num)d questions.',
            'num'
        ))
        super().__init__(*args, **kwargs, error_messages=error_messages)
        for form in self.forms:
            form.empty_permitted = False


class BaseAnswerFormSet(forms.BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False

    def full_clean(self):
        super().full_clean()

        correct_answers = 0
        for form in self.forms:
            if form.cleaned_data.get('is_correct'):
                correct_answers += 1

        if correct_answers > 1:
            self._non_form_errors.append('Only one answer can be correct')
        elif correct_answers == 0:
            self._non_form_errors.append('At least one answer must be correct')


QuestionFormSet = inlineformset_factory(Test, Question, form=QuestionForm,
                                        formset=BaseQuestionFormSet,
                                        min_num=5, extra=0, can_delete=True,
                                        validate_min=True)
AnswerFormSet = inlineformset_factory(Question, Answer, form=AnswerForm,
                                      formset=BaseAnswerFormSet,
                                      min_num=4, max_num=4, extra=0, can_delete=False,
                                      validate_min=True, validate_max=True)


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'required': True}),
        }
