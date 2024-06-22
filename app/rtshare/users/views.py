from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, UpdateView


User = get_user_model()


class AccountView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):

    template_name = 'account.html'
    context_object_name = 'user'
    permission_required = ('auth.change_user',)
    model = User
    fields = (
        'first_name',
        'last_name',
        'email',
    )

    def get_success_url(self):
        return reverse('user.account', args=(self.object.id,))

    def get_object(self):
        return self.request.user


class UserEventsListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):

    template_name = 'events-list.html'
    model = User
    permission_required = ('auth.view_user',)

    def get_context_data(self):
        telescopes = [
            telescope
            for group in self.request.user.groups.all()
            for telescope in group.telescope_set.all()
        ]
        return {
            **super().get_context_data(),
            'telescopes': telescopes,
            'stream_key': f'U-{self.request.user.id}',
        }
