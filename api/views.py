import asyncio
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import DomainSerializer

from . import engine


class RegistrationStatus(APIView):
    """
    Fetch information about the registration status of a domain
    """

    def get(self, request):
        name, tld = engine.split_domain_name(request.GET.get("domain"))
        serializer = DomainSerializer(
            data={
                "name": name,
                "tld": tld,
                "registered": asyncio.run(engine.whois_query(name, tld)),
            },
            many=False,
        )

        if request.user.is_authenticated:
            request.user.history.append(f"{name}.{tld}")
            request.user.save()

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        return Response(serializer.data)


class SimilarDomains(APIView):
    """
    Fetch similar domain names
    """

    def get(self, request):
        name, tld = engine.split_domain_name(request.GET.get("domain"))
        single_serializer = DomainSerializer(
            data={
                "name": name,
                "tld": tld,
                "registered": asyncio.run(engine.whois_query(name, tld)),
            },
            many=False,
        )

        if request.user.is_authenticated:
            request.user.history.append(f"{name}.{tld}")
            request.user.save()

        if not single_serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data=single_serializer.errors
            )

        similar_domains = asyncio.run(engine.similar_domains(name, tld))
        similar_serializer = DomainSerializer(similar_domains, many=True)

        return Response(
            {"domain": single_serializer.data, "similar": similar_serializer.data}
        )
