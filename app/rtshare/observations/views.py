from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import UpdateView, ListView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_eventstream import send_event

from .models import Observation, Sample, Configuration


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

    def send_messages(self):
        for telescope in self.object.observation.telescopes.all():
            serializer = ConfigurationSerializer(instance=self.object, context={
                'telescope': telescope,
            })
            send_event(telescope.public_id, 'message', {
                'type': 'update',
                'task': serializer.data,
            })

    def get_success_url(self):
        self.send_messages()
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


