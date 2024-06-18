from datetime import datetime

from rest_framework import serializers

from rtshare.utils import iqd
from telescope.models import Telescope
from .models import Configuration, Sample, Observation


class ConfigurationSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()
    start_at = serializers.DateTimeField(source='observation.start_at')
    end_at = serializers.DateTimeField(source='observation.end_at')

    class Meta:
        model = Configuration
        fields = (
            'id',
            'start_at',
            'end_at',
            'frequency',
            'sample_rate',
            'sample_size',
            'ppm',
            'gain',
        )

    def get_id(self, instance):
        return instance.get_identifier(self.context['telescope'])


class SampleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sample
        fields = (
            'data',
        )

    mappings = {
        'frequency': {
            'key': 'frequency',
            'transform': int,
        },
        'sample rate': {
            'key': 'sample_rate',
            'transform': int,
        },
        'n-samples': {
            'key': 'sample_size',
            'transform': int,
        },
        'gain': {
            'key': 'gain',
            'transform': int,
        },
        'ppm': {
            'key': 'ppm',
            'transform': int,
        },
        'capture time': {
            'key': 'captured_at',
            'transform': lambda x: datetime.fromisoformat(
                x,
                tzinfo=datetime.timezone.utc,
            ),
        },
    }

    def _get_value(self, headers, key, transform):
        try:
            return transform(headers[key])
        except Exception:
            return None

    def create(self, validated_data):
        # Using the data file, parse out the header data for the sample and
        # use that to update the record.
        headers = iqd.get_header(validated_data['data'])
        telescope_id, observation_id, configuration_id = [
            int(value)
            for value in headers['identifier'].split('-')
        ]

        if validated_data['telescope'].id != telescope_id:
            raise ValueError('Invalid telescope id for the given endpoint.')

        validated_data['telescope'] = Telescope.objects.get(id=telescope_id)
        validated_data['observation'] = Observation.objects.get(id=observation_id)
        validated_data['configuration'] = Configuration.objects.get(id=configuration_id)

        for source, mapping in self.mappings.items():
            destination, transform = mapping['key'], mapping['transform']
            validated_data[destination] = self._get_value(headers, source, transform)

        return super().create(validated_data)
