import asyncio
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import DomainSerializer

from .models import Domain

from . import engine

User = get_user_model()


class RegistrationStatus(APIView):
    """
    Fetch information about the registration status of a domain
    """

    def get(self, request):
        domain_name = request.GET.get("domain")
        query_res, err = asyncio.run(engine.whois_query(domain_name))
        if err:
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY, data={"message": err}
            )

        name, tld, registered = query_res
        domain = Domain(name=name, tld=tld, registered=registered)
        serializer = DomainSerializer(domain, many=False)

        if request.user.is_authenticated:
            user = User.objects.filter(username=request.user.username).get()
            user.history.append(domain_name)
            user.save()

        return Response(serializer.data)


class SimilarDomains(APIView):
    """
    Fetch similar domain names
    """

    def get(self, request):
        domain_name = request.GET.get("domain")
        query_res, err = asyncio.run(engine.whois_query(domain_name))
        if err:
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY, data={"message": err}
            )

        name, tld, registered = query_res
        domain = Domain(name=name, tld=tld, registered=registered)
        domain_serializer = DomainSerializer(domain, many=False)

        similar = asyncio.run(engine.similar_domains(domain))
        similar_serializer = DomainSerializer(similar, many=True)

        if request.user.is_authenticated:
            user = User.objects.filter(username=request.user.username).get()
            user.history.append(domain_name)
            user.save()

        return Response(
            {"domain": domain_serializer.data, "similar": similar_serializer.data}
        )
