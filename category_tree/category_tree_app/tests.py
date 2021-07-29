import io
import os.path
from tempfile import TemporaryDirectory
from unittest import TestCase

from django.urls import reverse
from django.test import TestCase, override_settings
from rest_framework.test import APITestCase
from PIL import Image

from category_tree_app.models import Category
from category_tree_app import utils
from category_tree_app.management.commands.get_rabbit_islands import (
    get_rabbit_islands
)
from category_tree_app.management.commands.get_longest_rabbit_hole import (
    get_longest_rabbit_holes_from_db
)

def add_data(directory):
    cat = Category.objects.create(
        image=os.path.join(directory.name, 'image_1'),
        name='1',
        description='description_1',
    )
    for i in range(2, 101):
        cat = Category.objects.create(
            image=os.path.join(directory.name, f'image_{i}'),
            name=str(i),
            description=f'description_{i}',
            parent_category=cat,
        )
    cat95 = Category.objects.get(name='95')
    Category.objects.create(
        parent_category=cat95,
        name='96B',
        image=os.path.join(directory.name, 'image96B'),
        description='96B'
    )


class TestModel(TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        add_data(self.directory)

    def dearDown(self):
        self.directory.cleanup()

    #@override_settings(DEBUG=True)
    def test_get_parent_list(self):
        parent_list = list(Category.objects.parent_list(category_id=97, depth=-4))
        self.assertEqual(5, len(parent_list))
        self.assertEqual(parent_list[0].name, '93')
        self.assertEqual(parent_list[0].depth, -4)
        self.assertEqual(parent_list[-1].depth, 0)
        self.assertEqual(parent_list[-1].name, '97')

    #@override_settings(DEBUG=True)
    def test_get_child_list(self):
        child_tree = list(Category.objects.child_list(category_id=93, depth=4))
        self.assertEqual(5, len(child_tree))
        self.assertEqual(child_tree[0].name, '93')
        self.assertEqual(child_tree[0].depth, 1)
        self.assertEqual(child_tree[-1].depth, 4)
        self.assertEqual(child_tree[-1].name, '96B')
        self.assertEqual(child_tree[-2].depth, 4)
        self.assertEqual(child_tree[-2].name, '96')


class TestCategoryViewSet(APITestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        add_data(self.directory)

    def dearDown(self):
        self.directory.cleanup()

    def generate_image_file(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_create_category(self):
        Category.objects.all().delete()
        cat = Category.objects.create(name='some name')
        url = reverse('category-list')
        data = {'name': 'foo', 'similarities': [cat.pk]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        new_categories = Category.objects.filter(name='foo')
        self.assertEqual(new_categories.count(), 1)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(list(new_categories[0].similarities.all()), [cat])
        self.assertEqual(list(cat.similarities.all()), [new_categories[0]])

    def test_put_image_for_existing_category(self):
        cat = Category.objects.create(name='bro')
        url = reverse('category-image', kwargs={'pk': cat.pk})
        data = {'image': self.generate_image_file()}
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, 200, response.json())
        cat.refresh_from_db()
        #self.assertEqual(cat.image, response['image'])

    def test_put_invalid_image_for_existing_category(self):
        cat = Category.objects.create(name='bro')
        url = reverse('category-image', kwargs={'pk': cat.pk})
        data = {'image': 'invalid_image'}
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, 400, response.json())

    def test_put_missing_image_field_for_existing_category(self):
        cat = Category.objects.create(name='bro')
        url = reverse('category-image', kwargs={'pk': cat.pk})
        data = {'imaggge': 'invalid_image'}
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, 400, response.json())

    def test_get_parents(self):
        url = reverse('category-parents', kwargs={'pk': '97'})
        respose = self.client.get(url + '?depth=4')
        self.assertEqual(respose.status_code, 200, respose.json())
        self.assertEqual(respose.json()[-1]['category_id'], 97)
        self.assertEqual(respose.json()[0]['category_id'], 93)

    def test_get_children(self):
        url = reverse('category-children', kwargs={'pk': '93'})
        respose = self.client.get(url + '?depth=4')
        self.assertEqual(respose.status_code, 200, respose.json())
        self.assertEqual(respose.json()[-1]['category_id'], 101)
        self.assertEqual(respose.json()[0]['category_id'], 93)


class TestCategorySimilarities(APITestCase):

    graph_1 = {
        'W': ['B', 'D'],
        'B': ['W', 'T', 'D'],
        'D': ['W', 'B'],
        'T': ['B'],
    }

    graph_2 = {
        'C': ['A', 'P', 'K'],
        'K': ['C'],
        'M': ['V'],
        'V': ['P', 'M', 'A'],
        'P': ['V', 'C'],
        'A': ['V', 'C'],
    }

    graph_3 = {
        'J': ['Z'],
        'R': ['G', 'F'],
        'F': ['R', 'I'],
        'G': ['R', 'U'],
        'I': ['F', 'S'],
        'U': ['G',],
        'E': ['S'],
        'S': ['I', 'X', 'E'],
        'X': ['S', 'H', 'Q'],
        'H': ['X'],
        'Q': ['X', 'Z'],
        'Z': ['Q', 'J'],
    }

    def add_island(self, graph):
        Category.objects.bulk_create(
            [
                Category(name=name) for name in graph.keys()
            ]
        )
        name_id_map = {c.name: c.category_id for c in Category.objects.all()}
        for name, similarities in graph.items():
            cat = Category.objects.get(name=name)
            for s in similarities:
                cat.similarities.add(name_id_map[s])

    def test_find_islands_with_one_island(self):
        self.add_island(self.graph_1)
        list_categories = list(get_rabbit_islands())
        self.assertEqual(len(list_categories), 1)
        got_categories = set(list_categories[0])
        expected_categories = set(self.graph_1)
        self.assertEqual(got_categories, expected_categories)

    def test_find_islands_with_tree_island(self):
        for graph in (self.graph_1, self.graph_2, self.graph_3):
            self.add_island(graph)

        got_categories = set([
            tuple(sorted(island)) for island in get_rabbit_islands()
        ])
        self.assertEqual(len(got_categories), 3)

        expected_categories = set([
            tuple(sorted(self.graph_1)),
            tuple(sorted(self.graph_2)),
            tuple(sorted(self.graph_3)),
        ])

        self.assertEqual(got_categories, expected_categories)

    def test_get_longest_rabbit_hole(self):
        for graph in (self.graph_1, self.graph_2, self.graph_3):
            self.add_island(graph)
        got_longest_rabbit_holes = list(get_longest_rabbit_holes_from_db())
        self.assertEqual(len(got_longest_rabbit_holes), 1)
        got = set(got_longest_rabbit_holes[0])
        expected = {'J', 'Z', 'Q', 'X', 'S', 'I', 'F', 'R', 'G', 'U'}
        self.assertEqual(got, expected)
