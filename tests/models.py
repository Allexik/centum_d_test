from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Test(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    passes_number = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


class Answer(models.Model):
    """
    So this model may be removed and changed by the corresponding fields
    in the Question model which would reduce the complexity.
    But for the sake of showing my skills, I will go with it :)
    (and because I'm almost done with stuff for it on the moment of writing this ;) )
    """

    LETTERS = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    letter = models.CharField(max_length=1, choices=LETTERS)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


class UserTest(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.test}'


class Comment(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='comments')
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment_text
