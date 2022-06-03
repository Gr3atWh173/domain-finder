"""Contains the business logic of the app"""
from typing import List
from urllib.parse import urlparse
import asyncio
import asyncwhois

# import whois
import requests
from .models import Domain

# POPULAR_TLDS = [tld.replace("_", ".") for tld in whois.TLD_RE]
POPULAR_TLDS = ["com", "org", "net", "dev", "co.in"]


async def whois_query(domain_name: str):
    """
    Does a single whois query.

    Args:
        domain_name (str): the domain name to lookup.

    Returns:
        A tuple with the structure: ([name, tld, registered], error_msg)
    """
    if not domain_name:
        return ([], "Missing required parameter.")

    name, tld = _split_domain_name(domain_name)
    if not _valid_domain_name(name):
        return ([], "Invalid domain name")

    try:
        registered = bool(await asyncwhois.aio_whois_domain(f"{name}.{tld}"))
    except asyncwhois.errors.NotFoundError:
        registered = False

    return ([name, tld, registered], "")


async def similar_domains(domain: Domain):
    """
    Finds similar domain names.

    Args:
        domain (Domain): the domain to find similar names to

    Returns:
        A list of similar unregistered domain names.
    """
    tlds = POPULAR_TLDS

    names = [domain.name] + (_similar_names(domain.name))

    whois_tasks = _create_whois_tasks(names, tlds=tlds)
    results = await asyncio.gather(*whois_tasks, return_exceptions=True)

    results = _exclude_errors(results)
    return _parse_results(results)


def _split_domain_name(domain_name: str) -> tuple:
    parsed = urlparse(domain_name)
    full_domain = parsed.netloc or parsed.path

    if "." in full_domain:
        return full_domain.split(".", maxsplit=1)

    return (full_domain, "com")


def _parse_results(results: list) -> List[Domain]:
    parsed = []
    for i, (res, err) in enumerate(results):
        if err:
            continue
        name, tld, registered = res
        parsed.append(Domain(id=i, name=name, tld=tld, registered=registered))

    return parsed


def _create_whois_tasks(domain_names: list, tlds: list) -> List:
    tasks = []
    for name in domain_names:
        for tld in tlds:
            task = asyncio.create_task(whois_query(f"{name}.{tld}"))
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
            if word == domain_name:
                continue
            similar.append(word["word"])

    return similar


def _valid_domain_name(name: str) -> bool:
    for c in name:
        if c.isalnum() or c == "-":
            continue
        return False
    return True
