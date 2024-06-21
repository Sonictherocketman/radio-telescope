from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import transaction
from django.views.generic import UpdateView, ListView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django_eventstream import send_event
from rest_framework import generics, serializers

from observations.models import Observation
from observations.serializers import ConfigurationSerializer, SampleSerializer
from .models import Telescope
from .permissions import IsTelescopeUpdatingItself

from . import tasks as _  # noqa


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


# API Views


class TelescopeHealthCheckView(generics.UpdateAPIView):

    class HealthCheckSerializer(serializers.ModelSerializer):
        class Meta:
            model = Telescope
            fields = (
                'state',
            )

        @transaction.atomic
        def update(self, instance, validated_data):
            validated_data['state_updated_at'] = timezone.now()
            return super().update(instance, validated_data)

    queryset = (
        Telescope.objects.filter(status=Telescope.Status.ACTIVE)
        .select_for_update()
    )
    serializer_class = HealthCheckSerializer
    permission_classes = (
        IsTelescopeUpdatingItself,
    )


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
