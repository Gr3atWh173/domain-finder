from rest_framework import serializers
from .models import Domain


class DomainSerializer(serializers.ModelSerializer):
    """Serializer class for Domain object"""

    class Meta:
        model = Domain
        fields = ["name", "tld", "registered"]
