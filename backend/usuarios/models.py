from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    role = models.CharField(
        choices=(
            ('admin', 'admin'),
            ('user', 'user'),
        ),
        max_length=200, blank=True, null=True, default='user'
    )

    def __str__(self):
        return self.username
    
class AuthToken(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    token = models.CharField(max_length=200)
    created_at = models.DateTimeField()

    def __str__(self):
        return self.token
    
class Case(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField()
    date_end = models.DateField()

    def __str__(self):
        return self.title
    
class TruthBullet(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content