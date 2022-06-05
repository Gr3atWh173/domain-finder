from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.postgres import fields
from django.contrib.auth.models import AbstractUser
from .validators import domain_name_validator, domain_tld_validator


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
    name = models.CharField(
        max_length=63, validators=[MinLengthValidator(2), domain_name_validator]
    )
    tld = models.CharField(
        max_length=63, validators=[MinLengthValidator(2), domain_tld_validator]
    )
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
