from django.db import models
from django.contrib.postgres import fields
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import AbstractUser


class Domain(models.Model):
    class Meta:
        managed = False

    # https://datatracker.ietf.org/doc/html/rfc1034
    name = models.CharField(max_length=63, validators=[MinLengthValidator(3)])
    tld = models.CharField(max_length=63, validators=[MinLengthValidator(3)])
    registered = models.BooleanField(default=False)


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    history = fields.ArrayField(
        base_field=models.CharField(max_length=255), default=list
    )

    REQUIRED_FIELDS = ["email", "first_name", "history"]
