from django.core.management.base import BaseCommand, CommandError
from category_tree_app.models import Category
from category_tree_app.utils import get_longest_rabbit_holes


def get_longest_rabbit_holes_from_db():
    similarities = set(Category.similarities.through.objects.values_list(
        'from_category_id', 'to_category_id'
    ))
    paths = get_longest_rabbit_holes(similarities)

    for category_ids in paths:
        categories = Category.objects.filter(pk__in=category_ids)
        categories = {c.pk: c.name for c in categories}
        path = [categories[c_id] for c_id in category_ids]
        yield path


class Command(BaseCommand):
    help = 'Get longest rabbit hole'

    def handle(self, *args, **options):
        result = set(Category.similarities.through.objects.values_list(
            'from_category_id', 'to_category_id'
        ))
        paths = get_longest_rabbit_holes(result)

        for category_ids in paths:
            categories = Category.objects.filter(pk__in=category_ids)
            categories = {c.pk: c.name for c in categories}
            path = [categories[c_id] for c_id in category_ids]
            self.stdout.write(self.style.SUCCESS(path))
