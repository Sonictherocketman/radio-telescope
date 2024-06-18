import os.path

from django.contrib.auth.models import User
from django.test import TestCase

from observations.models import Configuration, Observation
from .models import Telescope


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


class APITest(TestCase):

    def setUp(self):
        self.telescope = Telescope.objects.create(
            name='Test Scope',
            status=Telescope.Status.ACTIVE,
            state=Telescope.State.OFFLINE,
        )
        self.observation = Observation.objects.create(name='Test Observation #1')
        self.observation.telescopes.add(self.telescope)
        Configuration.objects.create(
            observation=self.observation,
            # Use default values
        )
        self.credentials = {
            'username': 'test-user',
            'password': 'test-password',
        }
        self.user = User.objects.create_user(**self.credentials)

    def test_can_access_tasks(self):
        self.client.login(**self.credentials)
        response = self.client.get(f'/api/telescope/{self.telescope.id}/tasks')
        self.assertEqual(response.status_code, 200)

    def test_can_update_status(self):
        self.client.login(**self.credentials)
        response = self.client.put(
            f'/api/telescope/{self.telescope.id}/health-check',
            data={'state': 'online'},
            content_type='application/json',
        )
        self.assertEqual(response.json()['state'], 'online')

    def test_can_upload_data(self):
        self.client.login(**self.credentials)
        with open(os.path.join(FIXTURES_DIR, 'sample.iqd.gz'), 'rb') as file:
            response = self.client.post(
                f'/api/telescope/{self.telescope.id}/transmit',
                data={'data': file},
            )
        self.assertEqual(response.status_code, 201)
