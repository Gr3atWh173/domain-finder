from urllib.parse import urlparse
import whois


def whois_query(domain_name):
    try:
        name, tld = _whois_helper(domain_name)
        registered = bool(whois.query(f"{name}.{tld}"))

    except AttributeError:
        return ([], "Missing required parameter.")

    except whois.exceptions.FailedParsingWhoisOutput:
        return ([], "Unable to find server for this lookup.")

    except whois.exceptions.UnknownTld:
        return ([], "Unknown TLD")

    except whois.exceptions.WhoisCommandFailed:
        return ([], "Whois lookup failed")

    return ([name, tld, registered], "")


def _whois_helper(domain_name):
    if not domain_name:
        raise AttributeError

    parsed = urlparse(domain_name)

    # the parsed domain name is either in netloc or in path
    full_domain = parsed.netloc or parsed.path

    try:
        name, tld = full_domain.split(".", maxsplit=1)
    except ValueError:
        name = full_domain
        tld = "com"

    return (name, tld)
