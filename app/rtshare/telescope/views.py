from datetime import datetime, timedelta

from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import UpdateView, ListView
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django_eventstream import send_event
from rest_framework import generics, serializers

from observations.models import Sample, Configuration, Observation
from rtshare.utils import iqd
from .models import Telescope, Token
from .permissions import IsTelescopeUpdatingItself

from . import tasks  # noqa


class TelescopeListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):

    template_name = 'telescope-list.html'
    model = Telescope
    permission_required = ('telescope.view_telescope',)


class TelescopeDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):

    template_name = 'telescope-detail.html'
    model = Telescope
    permission_required = ('telescope.view_telescope', 'telescope.change_telescope')

    fields = (
        'name',
        'status',
        'description',
        'latitude',
        'longitude',
        'elevation',
    )

    def get_success_url(self):
        return reverse('telescope.update', args=(self.object.id,))


class TelescopeSendPingEventView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):

    template_name = 'telescope-detail.html'
    model = Telescope
    context_object_name = 'telescope'
    permission_required = ('telescope.change_telescope',)

    fields = (
        'id',
    )

    def get_success_url(self):
        send_event(self.object.public_id, 'message', {'type': 'ping'})
        return reverse('telescope.update', args=(self.object.id,))


class TelescopeSendReconfigureEventView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):

    template_name = 'telescope-detail.html'
    model = Telescope
    context_object_name = 'telescope'
    permission_required = ('telescope.change_telescope',)

    fields = (
        'id',
    )

    def get_success_url(self):
        send_event(self.object.public_id, 'message', {'type': 'configure'})
        return reverse('telescope.update', args=(self.object.id,))


class TelescopeObservationListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):

    template_name = 'telescope-observation-list.html'
    model = Observation
    context_object_name = 'observations'
    paginate_by = 10
    permission_required = ('telescope.view_observation',)

    def get_queryset(self):
        return self.model.objects.filter(telescopes=self.kwargs['pk'])

    def get_context_data(self):
        return {
            **super().get_context_data(),
            'telescope': get_object_or_404(Telescope, id=self.kwargs['pk']),
        }


class TelescopeRegenerateTokenView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):

    template_name = 'telescope-detail.html'
    model = Telescope
    context_object_name = 'token'
    permission_required = ('telescope.change_token',)

    fields = (
        'id',
    )

    def get_success_url(self):
        self.object.token.key = self.object.token.generate_key()
        self.object.token.save()
        return reverse('telescope.update', args=(self.object.id,))


# API Views


class TelescopeHealthCheckView(generics.UpdateAPIView):

    class HealthCheckSerializer(serializers.ModelSerializer):
        class Meta:
            model = Telescope
            fields = (
                'state',
            )

        def update(self, instance, validated_data):
            validated_data['state_updated_at'] = timezone.now()
            return super().update(instance, validated_data)

    queryset = Telescope.objects.filter(status=Telescope.Status.ACTIVE)
    serializer_class = HealthCheckSerializer
    permission_classes = (
        IsTelescopeUpdatingItself,
    )


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


class TelescopeSerializer(serializers.ModelSerializer):

    tasks = ConfigurationSerializer(many=True)

    class Meta:
        model = Telescope
        fields = (
            'id',
            'name',
            'latitude',
            'longitude',
            'elevation',
            'tasks',
        )


class TelescopeAPIView(generics.RetrieveAPIView):

    serializer_class = TelescopeSerializer
    queryset = Telescope.objects.filter(status=Telescope.Status.ACTIVE)

    def get_serializer_context(self):
        return {
            **super().get_serializer_context(),
            'telescope': get_object_or_404(Telescope, id=self.kwargs['pk']),
        }


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
            'transform': lambda x: datetime.fromisoformat(x),
        },
    }

    def _get_value(self, headers, key, transform):
        try:
            return transform(headers[key])
        except Exception as e:
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


class SampleDataTransmitView(generics.CreateAPIView):

    queryset = Telescope.objects.filter(status=Telescope.Status.ACTIVE)
    serializer_class = SampleSerializer
    permission_classes = (
        IsTelescopeUpdatingItself,
    )

    def perform_create(self, serializer):
        return serializer.save(telescope=self.telescope)

    def create(self, request, pk=None):
        self.telescope = get_object_or_404(Telescope, id=pk)
        return super().create(request, pk=None)
