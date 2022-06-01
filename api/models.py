from django.db import models
from django.core.validators import MinLengthValidator


class Domain(models.Model):
    class Meta:
        managed = False

    # https://datatracker.ietf.org/doc/html/rfc1034
    name = models.CharField(max_length=63, validators=[MinLengthValidator(3)])
    tld = models.CharField(max_length=63, validators=[MinLengthValidator(3)])
    registered = models.BooleanField(default=False)
