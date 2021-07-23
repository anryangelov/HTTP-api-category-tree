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


class TestUtils(TestCase):
    island1_similarities = set([
        (1,2),
        (12,1),
        (12,2),
        (2,4),
        (2,1),
        (2,12),
        (1,12),
        (4,2),
    ])
    island2_similarities = set([
        (5,7),
        (5,8),
        (7,5),
        (7,6),
        (8,5),
        (8,6),
        (8,9),
        (6,9),
        (6,8),
        (6,7),
        (9,6),
        (9,8),
        (9,13),
        (13,9),
    ])
    island3_similarities = set([
        (11,3),
        (11,14),
        (3,11),
        (3,10),
        (10,3),
        (10,14),
        (14,11),
        (14,13),
    ])

    def setUp(self):
        self.all_similarities = set()
        self.expected_islands = (
            self.island1_similarities,
            self.island2_similarities,
            self.island3_similarities,
        )
        for similarities in self.expected_islands:
            self.all_similarities.update(similarities)

    def test_get_islands_vetexes(self):
        got_islands = utils.get_islands_vertexes(self.all_similarities)
        #import IPython; IPython.embed()
        for got_island in got_islands:
            self.assertIn(got_island, self.expected_islands)

    def test_get_islands_categories(self):
        islands_categories = utils.get_islands_categories(self.expected_islands)
        self.assertEqual(
            islands_categories,
            [{1, 2, 4, 12}, {5, 6, 7, 8, 9, 13}, {3, 10, 11, 13, 14}]
        )
