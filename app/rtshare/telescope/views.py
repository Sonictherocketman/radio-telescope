from datetime import timedelta

from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import UpdateView, ListView
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django_eventstream import send_event
from rest_framework import generics, serializers

from .models import Observation, Telescope, Token, Sample, Configuration
from .permissions import IsTelescopeUpdatingItself


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
        send_event(str(self.kwargs['pk']), 'message', {'type': 'ping'})
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
        send_event(str(self.kwargs['pk']), 'message', {'type': 'configure'})
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


class ObservationListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):

    context_object_name = 'observations'
    template_name = 'observation-list.html'
    model = Observation
    permission_required = ('telescope.view_observation',)


class ObservationDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):

    template_name = 'observation-detail.html'
    model = Observation
    permission_required = ('telescope.view_observation', 'telescope.change_observation')

    fields = (
        'name',
        'start_at',
        'end_at',
        'telescopes',
    )

    def get_success_url(self):
        return reverse('observation.update', args=(self.object.id,))


class ObservationConfigurationListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):

    template_name = 'observation-configuration-list.html'
    model = Configuration
    context_object_name = 'configurations'
    paginate_by = 10
    permission_required = ('telescope.view_configuration',)

    def get_queryset(self):
        return self.model.objects.filter(observation=self.kwargs['pk'])

    def get_context_data(self):
        return {
            **super().get_context_data(),
            'observation': get_object_or_404(Observation, id=self.kwargs['pk']),
        }


class ConfigurationDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):

    template_name = 'configuration-detail.html'
    model = Configuration
    permission_required = ('telescope.view_configuration', 'telescope.change_configuration')

    fields = (
        'name',
        'frequency',
        'sample_rate',
        'sample_size',
        'ppm',
        'gain',
    )

    def get_success_url(self):
        return reverse('configuration.update', args=(self.object.id,))


class ObservationSampleListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):

    template_name = 'observation-sample-list.html'
    model = Sample
    context_object_name = 'samples'
    paginate_by = 10
    permission_required = ('telescope.view_sample',)

    def get_queryset(self):
        return self.model.objects.filter(observation=self.kwargs['pk'])

    def get_context_data(self):
        return {
            **super().get_context_data(),
            'observation': get_object_or_404(Observation, id=self.kwargs['pk']),
        }


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


class TelescopeAPIView(generics.RetrieveAPIView):

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


    serializer_class = TelescopeSerializer
    queryset = Telescope.objects.filter(status=Telescope.Status.ACTIVE)

    def get_serializer_context(self):
        return {
            **super().get_serializer_context(),
            'telescope': get_object_or_404(Telescope, id=self.kwargs['pk']),
        }


class SampleDataTransmitView(generics.CreateAPIView):

    class SampleSerializer(serializers.ModelSerializer):
        class Meta:
            model = Sample
            fields = (
                'data',
            )

    queryset = Telescope.objects.filter(status=Telescope.Status.ACTIVE)
    serializer_class = SampleSerializer
    permission_classes = (
        IsTelescopeUpdatingItself,
    )

    def perform_create(self, serializer):
        return serializer.save(observation=self.observation)

    def create(self, request, pk=None):
        self.observation = get_object_or_404(Observation, id=pk)
        return super().create(request, pk=None)
