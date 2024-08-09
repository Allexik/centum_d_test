from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from tests.models import Test
from tests.forms import TestForm, QuestionFormSet, AnswerFormSet


class TestListView(ListView):
    model = Test
    template_name = 'pages/test_list.html'


class TestDetailView(DetailView):
    model = Test
    template_name = 'pages/test_detail.html'


class TestCreateView(CreateView):
    model = Test
    form_class = TestForm
    template_name = 'pages/test_form.html'

    def get_success_url(self):
        return reverse_lazy('test_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['question_formset'] = QuestionFormSet(self.request.POST)
            data['answer_formsets'] = [
                AnswerFormSet(self.request.POST, prefix=f'questions-{question_form.prefix.split('-')[1]}-answers')
                for question_form in data['question_formset']
            ]
        else:
            data['question_formset'] = QuestionFormSet()
            data['answer_formsets'] = [
                AnswerFormSet(prefix=f'questions-{question_form.prefix.split('-')[1]}-answers')
                for question_form in data['question_formset']
            ]
        data['empty_question_form'] = QuestionFormSet().empty_form
        data['template_answer_formset'] = AnswerFormSet(
            prefix=f'questions-__question_prefix__-answers'
        )
        data['template_question_prefix'] = 'questions-__question_prefix__'
        return data

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        question_formset = context['question_formset']
        answer_formsets = context['answer_formsets']

        form.instance.user = self.request.user
        instance = form.save()

        if question_formset.is_valid():
            question_formset.instance = instance
            question_formset.save()

            for i, question_form in enumerate(question_formset):
                answer_formset = answer_formsets[i]
                if question_form.cleaned_data.get('DELETE') is False:
                    if answer_formset.is_valid():
                        answer_formset.instance = question_form.instance
                        answer_formset.save()
                    else:
                        transaction.set_rollback(True)
                        return self.render_to_response({
                            **context,
                            'form': form,
                        })

            self.object = instance
            return redirect(self.get_success_url())
        else:
            transaction.set_rollback(True)
            return self.render_to_response({
                **context,
                'form': form,
            })


class TestUpdateView(UpdateView):
    model = Test
    form_class = TestForm
    template_name = 'pages/test_form.html'

    def get_success_url(self):
        return reverse_lazy('test_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['question_formset'] = QuestionFormSet(self.request.POST, instance=self.object)
            initial_questions_count = int(data['question_formset'].management_form.cleaned_data['INITIAL_FORMS'])
            data['answer_formsets'] = [
                AnswerFormSet(
                    self.request.POST,
                    instance=question_form.instance if index < initial_questions_count else None,
                    prefix=f'questions-{question_form.prefix.split('-')[1]}-answers'
                )
                for index, question_form in enumerate(data['question_formset'])
            ]
        else:
            data['question_formset'] = QuestionFormSet(instance=self.object)
            data['answer_formsets'] = [
                AnswerFormSet(
                    instance=question_form.instance,
                    prefix=f'questions-{question_form.prefix.split('-')[1]}-answers'
                )
                for question_form in data['question_formset']
            ]
        data['empty_question_form'] = QuestionFormSet().empty_form
        data['template_answer_formset'] = AnswerFormSet(
            prefix=f'questions-__question_prefix__-answers'
        )
        data['template_question_prefix'] = 'questions-__question_prefix__'
        return data

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        question_formset = context['question_formset']
        answer_formsets = context['answer_formsets']

        instance = form.save()

        if question_formset.is_valid():
            question_formset.instance = instance
            question_formset.save()

            for i, question_form in enumerate(question_formset):
                answer_formset = answer_formsets[i]
                if question_form.cleaned_data.get('DELETE') is False:
                    if answer_formset.is_valid():
                        answer_formset.instance = question_form.instance
                        answer_formset.save()
                    else:
                        transaction.set_rollback(True)
                        return self.render_to_response({
                            **context,
                            'form': form,
                        })

            self.object = instance
            return redirect(self.get_success_url())
        else:
            transaction.set_rollback(True)
            return self.render_to_response({
                **context,
                'form': form,
            })


class TestDeleteView(DeleteView):
    model = Test
    template_name = 'pages/test_confirm_delete.html'
    success_url = reverse_lazy('test_list')
