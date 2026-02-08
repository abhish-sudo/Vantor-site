"""
Account Models
Using Django's built-in User model
Future: Can extend with UserProfile model for additional fields
"""
from django.db import models
from django.contrib.auth.models import User

# Using Django's default User model
# Future extension example:
#
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     phone = models.CharField(max_length=20, blank=True)
#     address = models.TextField(blank=True)
#     date_of_birth = models.DateField(null=True, blank=True)
#     avatar = models.ImageField(upload_to='avatars/', blank=True)
