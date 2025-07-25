from django.db import models
import random
import string
from django.utils import timezone

def generate_invite_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

class UserProfile(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    auth_code = models.CharField(max_length=4, blank=True, null=True)
    auth_code_sent_time = models.DateTimeField(blank=True, null=True)
    invite_code = models.CharField(max_length=6, blank=True, null=True)
    used_invite_code = models.CharField(max_length=6, blank=True, null=True)
    inviter = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='invited_users')

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = generate_invite_code()
        super().save(*args, **kwargs)