"""Custom validators for the models"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from whois import TLD_RE


def domain_name_validator(name):
    """Validates that a domain name consists only of allowed characters"""
    for ch in name:
        if not (ch.isalnum() or ch == "-"):
            raise ValidationError(
                _(
                    "Domain name can only contain alphanumeric characters or '-' (hyphen)"
                ),
                params={"name": name},
            )


def domain_tld_validator(tld):
    """Validates that the TLD is in the list of supported TLDs"""
    if tld not in [tld.replace("_", ".") for tld in TLD_RE]:
        raise ValidationError(_("TLD not supported"), params={"tld": tld})
