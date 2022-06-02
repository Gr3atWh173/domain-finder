import asyncio
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import DomainSerializer

from .models import Domain

from . import engine


class RegistrationStatus(APIView):
    """
    Fetch information about the registration status of a domain
    """

    def get(self, request):
        domain = request.GET.get("domain")
        query_res, err = asyncio.run(engine.whois_query(domain))
        if err:
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY, data={"message": err}
            )

        name, tld, registered = query_res
        domain = Domain(name=name, tld=tld, registered=registered)
        serializer = DomainSerializer(domain, many=False)

        return Response(serializer.data)


class SimilarDomains(APIView):
    """
    Fetch similar domain names
    """

    def get(self, request):
        domain = request.GET.get("domain")
        query_res, err = asyncio.run(engine.whois_query(domain))
        if err:
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY, data={"message": err}
            )

        name, tld, registered = query_res
        domain = Domain(name=name, tld=tld, registered=registered)

        similar = asyncio.run(engine.similar_domains(domain))
        serializer = DomainSerializer(similar, many=True)

        return Response(serializer.data)
