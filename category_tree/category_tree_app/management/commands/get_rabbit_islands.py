from django.core.management.base import BaseCommand, CommandError
from category_tree_app.models import Category
from category_tree_app.utils import get_islands_categories, get_islands_vertexes


class Command(BaseCommand):
    help = 'Get rabbit islands'

    def handle(self, *args, **options):
        result = set(Category.similarities.through.objects.values_list(
            'from_category_id', 'to_category_id'
        ))
        islands_vertexes = get_islands_vertexes(result)  # similarity pair
        islands_category_ids = get_islands_categories(islands_vertexes)

        for island_category_ids in islands_category_ids:
            # better select all at once
            categories = Category.objects.filter(
                pk__in=island_category_ids).values_list('name', flat=True)
            self.stdout.write(self.style.SUCCESS(list(categories)))
