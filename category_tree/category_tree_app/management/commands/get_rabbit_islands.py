from django.core.management.base import BaseCommand, CommandError
from category_tree_app.models import Category
from category_tree_app.utils import get_islands_categories


def get_rabbit_islands():
    similarities = set(Category.similarities.through.objects.values_list(
            'from_category_id', 'to_category_id'
        ))
    islands_category_ids = get_islands_categories(similarities)

    for island_category_ids in islands_category_ids:
        # better select all at once
        categories = Category.objects.filter(
            pk__in=island_category_ids).values_list('name', flat=True)
        yield list(categories)


class Command(BaseCommand):
    help = 'Get rabbit islands'

    def handle(self, *args, **options):
        for categories in get_rabbit_islands():
            self.stdout.write(self.style.SUCCESS(categories))
