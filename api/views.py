from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import DomainSerializer

from .models import Domain

from . import utils


class RegistrationStatus(APIView):
    """
    Fetch information about the registration status of a domain
    """

    def get(self, request):
        query_res, err = utils.whois_query(request.GET.get("domain"))
        if err:
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY, data={"message": err}
            )

        name, tld, registered = query_res
        domain = Domain(name=name, tld=tld, registered=registered)
        serializer = DomainSerializer(domain, many=False)

        return Response(serializer.data)
