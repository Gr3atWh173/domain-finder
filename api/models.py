from django.db import models
from django.contrib.postgres import fields
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import AbstractUser


class Domain(models.Model):
    """
    Model class for a domain.

    Attributes:
        name (str): The name of the domain
        tld (str): Thr top-level-domain name
        registered (bool): If the domain is registered or not
    """

    class Meta:
        managed = False

    # https://datatracker.ietf.org/doc/html/rfc1034
    name = models.CharField(max_length=63, validators=[MinLengthValidator(3)])
    tld = models.CharField(max_length=63, validators=[MinLengthValidator(3)])
    registered = models.BooleanField(default=False)


class User(AbstractUser):
    """
    Custom user model.

    Attributes:
        email (str): Email of the user
        history (List[str]): User search historyt
    """

    email = models.EmailField(unique=True, blank=False)
    history = fields.ArrayField(
        base_field=models.CharField(max_length=255), default=list
    )

    REQUIRED_FIELDS = ["email", "history"]
