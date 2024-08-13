from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from tests.models import Test, Result, Comment
from tests.forms import TestForm, QuestionFormSet, AnswerFormSet, CommentForm
from tests.utils.views import OwnerRequiredMixin


class TestListView(ListView):
    model = Test
    template_name = 'pages/test_list.html'

    def get_queryset(self):
        search = self.request.GET.get('search')
        order_by = self.request.GET.get('order_by', '-created_at').split('__')[0]
        passes_number_min = self.request.GET.get('passes_number_min')
        passes_number_max = self.request.GET.get('passes_number_max')
        list_type = self.request.GET.get('list_type', 'all')

        queryset = super().get_queryset().order_by(order_by)
        if list_type == 'my':
            queryset = queryset.filter(user=self.request.user)
        if search:
            queryset = queryset.filter(name__icontains=search)
        if passes_number_min:
            queryset = queryset.filter(passes_number__gte=passes_number_min)
        if passes_number_max:
            queryset = queryset.filter(passes_number__lte=passes_number_max)

        return queryset

    def get(self, request, *args, **kwargs):
        if self.request.GET.get('list_type', 'all') == 'my' and not self.request.user.is_authenticated:
            query_params = self.request.GET.copy()
            query_params.pop('list_type')
            return redirect(f'{reverse_lazy("test_list")}?{query_params.urlencode()}')
        return super().get(request, *args, **kwargs)


class TestDetailView(DetailView):
    model = Test
    template_name = 'pages/test_detail.html'

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            Prefetch('comments', queryset=Comment.objects.order_by('-created_at')),
            'comments__user',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context


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
        data['active_question_count'] = len(data['question_formset']) - len(data['question_formset'].deleted_forms)
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
        return super().get_queryset().prefetch_related('questions__answers')

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
        data['active_question_count'] = len(data['question_formset']) - len(data['question_formset'].deleted_forms)
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


class TestCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def get(self, request, *args, **kwargs):
        return redirect('test_detail', pk=kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('test_detail', kwargs={'pk': self.object.test.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.test_id = self.kwargs['pk']
        return super().form_valid(form)


class TestPassView(LoginRequiredMixin, DetailView):
    model = Test
    template_name = 'pages/test_pass.html'

    def get_success_url(self, result_pk):
        return reverse_lazy('test_result', kwargs={'pk': result_pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.prefetch_related('answers')
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
        return (super().get_queryset()
                .filter(user=self.request.user)
                .select_related('test'))


class TestResultView(OwnerRequiredMixin, LoginRequiredMixin, DetailView):
    model = Result
    template_name = 'pages/test_result.html'

