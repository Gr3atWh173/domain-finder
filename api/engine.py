from urllib.parse import urlparse
import asyncio
import asyncwhois
import requests
from .models import Domain

POPULAR_TLDS = ["com", "org", "net", "dev", "io"]


async def whois_query(domain_name):
    if not domain_name:
        return ([], "Missing required parameter.")

    name, tld = _split_domain_name(domain_name)

    try:
        registered = bool(await asyncwhois.aio_whois_domain(domain_name))
    except asyncwhois.errors.NotFoundError:
        registered = False

    return ([name, tld, registered], "")


async def similar_domains(domain):
    tlds = POPULAR_TLDS

    names = [domain.name] + (_similar_names(domain.name))

    whois_tasks = _create_whois_tasks(names, tlds=tlds)
    results = await asyncio.gather(*whois_tasks, return_exceptions=True)

    results = _exclude_errors(results)
    return _parse_results(results)


def _split_domain_name(domain_name):
    parsed = urlparse(domain_name)
    full_domain = parsed.netloc or parsed.path

    if "." in full_domain:
        return full_domain.split(".", maxsplit=1)

    return (full_domain, "com")


def _parse_results(results):
    parsed = []
    for i, (res, err) in enumerate(results):
        if err:
            continue
        name, tld, registered = res
        if not registered:
            parsed.append(Domain(id=i, name=name, tld=tld, registered=registered))

    return parsed


def _create_whois_tasks(domain_names, tlds):
    tasks = []
    for name in domain_names:
        for tld in tlds:
            task = asyncio.create_task(whois_query(f"{name}.{tld}"))
            tasks.append(task)
    return tasks


def _exclude_errors(results):
    return [p for p in results if isinstance(p, tuple)]


def _similar_names(domain_name):
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
