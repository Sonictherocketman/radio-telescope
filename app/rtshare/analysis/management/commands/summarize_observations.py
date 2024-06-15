from django.core.management.base import BaseCommand

from analysis.tasks import summarize_completed_observations_if_needed


class Command(BaseCommand):
    help = (
        'Summarize all completed observations.'
    )

    def handle(self, **options):
        summarize_completed_observations_if_needed.delay()

        self.stdout.write(self.style.SUCCESS(
            'Dispatched tasks'
        ))
