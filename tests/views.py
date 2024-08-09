from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from tests.models import Test, Result
from tests.forms import TestForm, QuestionFormSet, AnswerFormSet
from tests.utils.views import OwnerRequiredMixin


class TestListView(ListView):
    model = Test
    template_name = 'pages/test_list.html'


class TestDetailView(DetailView):
    model = Test
    template_name = 'pages/test_detail.html'


class TestCreateView(LoginRequiredMixin, CreateView):
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


class TestUpdateView(OwnerRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Test
    form_class = TestForm
    template_name = 'pages/test_form.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('test_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['question_formset'] = QuestionFormSet(self.request.POST, instance=self.object)
            initial_question_count = int(data['question_formset'].management_form.cleaned_data['INITIAL_FORMS'])
            data['answer_formsets'] = [
                AnswerFormSet(
                    self.request.POST,
                    instance=question_form.instance if index < initial_question_count else None,
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


class TestDeleteView(OwnerRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Test
    template_name = 'pages/test_confirm_delete.html'
    success_url = reverse_lazy('test_list')


class TestPassView(LoginRequiredMixin, DetailView):
    model = Test
    template_name = 'pages/test_pass.html'

    def get_success_url(self, result_pk):
        return reverse_lazy('test_result', kwargs={'pk': result_pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.all()
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        questions = self.object.questions.prefetch_related('answers')
        score = 0

        for question in questions:
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                selected_answer = question.answers.get(id=selected_answer_id)
                if selected_answer.is_correct:
                    score += 1

        result_instance = Result.objects.create(
            user=request.user,
            test=self.object,
            score=score,
            question_count=questions.count(),
        )

        self.object.passes_number += 1
        self.object.save()

        return redirect(self.get_success_url(result_instance.pk))


class TestResultsView(LoginRequiredMixin, ListView):
    model = Result
    template_name = 'pages/test_results.html'
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class TestResultView(OwnerRequiredMixin, LoginRequiredMixin, DetailView):
    model = Result
    template_name = 'pages/test_result.html'

