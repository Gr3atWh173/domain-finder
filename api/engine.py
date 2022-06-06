"""Contains the business logic of the app"""
from typing import List
from urllib.parse import urlparse
import asyncio
import asyncwhois
import requests
from django.core.exceptions import ValidationError

from api.validators import domain_name_validator
from .models import Domain

# POPULAR_TLDS = [tld.replace("_", ".") for tld in whois.TLD_RE]
POPULAR_TLDS = ["com", "org", "net", "dev", "co"]


async def whois_query(name, tld):
    """
    Does a single whois query.

    Args:
        name (str): the domain name to lookup.
        tld (str): the tld of the domain.

    Returns:
        True if the domain is registered, False otherwise.
    """
    try:
        return bool(await asyncwhois.aio_whois_domain(f"{name}.{tld}"))
    except asyncwhois.errors.NotFoundError:
        return False


async def similar_domains(name, tld):
    """
    Finds similar domain names.

    Args:
        domain (Domain): the domain to find similar names to

    Returns:
        A list of similar unregistered domain names.
    """
    tlds = POPULAR_TLDS
    if tld in tlds:
        tlds.remove(tld)

    names = set([name] + _similar_names(name))

    whois_tasks = _create_whois_tasks(names, tlds=tlds)
    results = await asyncio.gather(*whois_tasks, return_exceptions=True)

    results = _exclude_errors(results)
    return _parse_results(results)


async def _structured_whois(name, tld):
    return (name, tld, await whois_query(name, tld))


def split_domain_name(domain_name: str) -> tuple:
    """
    Splits a domain name into name and tld

    Args:
        domain_name (str): the domain name to split

    Returns:
        (name, tld)

    Note:
        If a TLD can't be ascertained, it defaults to 'com'
    """
    parsed = urlparse(domain_name)
    full_domain = parsed.netloc or parsed.path

    if "." in full_domain:
        return full_domain.split(".", maxsplit=1)

    return (full_domain, "com")


def _parse_results(results: list) -> List[Domain]:
    parsed = []
    for name, tld, registered in results:
        parsed.append(Domain(name=name, tld=tld, registered=registered))
    return parsed


def _create_whois_tasks(domain_names: set, tlds: list) -> List:
    tasks = []
    for name in domain_names:
        for tld in tlds:
            task = asyncio.create_task(_structured_whois(name, tld))
            tasks.append(task)
    return tasks


def _exclude_errors(results: list) -> List[tuple]:
    return [p for p in results if isinstance(p, tuple)]


def _similar_names(domain_name: str) -> List[str]:
    similar = []

    api_base = "https://api.datamuse.com"
    endpoints = {"/words?sp=", "/words?sl=", "/words?ml=", "/words?rel_trg=cow"}

    for endpoint in endpoints:
        url = api_base + endpoint + domain_name
        resp = requests.get(url)
        if resp.status_code != 200 or not resp.json():
            continue

        words = resp.json()[0:3]

        for word in words:
            if word["word"] != domain_name:
                domain = "".join(word["word"].split())

                try:
                    domain_name_validator(domain)
                except ValidationError:
                    continue

                similar.append(domain)

    return similar
