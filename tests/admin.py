from django.contrib import admin

from tests.models import Test, Question, Answer, Result, Comment


class QuestionInline(admin.TabularInline):
    model = Question
    min_num = 5
    extra = 0


class AnswerInline(admin.TabularInline):
    model = Answer
    min_num = 4
    max_num = 4
    extra = 0
    can_delete = False


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ['user', 'name', 'description', 'passes_number', 'created_at', 'updated_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ['text', 'created_at', 'updated_at']
    list_filter = ['test']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['letter', 'text', 'is_correct', 'created_at', 'updated_at']
    list_filter = ['question__test', 'question']


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'test', 'score', 'question_count', 'created_at', 'updated_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['test', 'text', 'created_at', 'updated_at']

