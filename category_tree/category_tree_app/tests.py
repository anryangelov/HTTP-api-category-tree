from django.test import TestCase, override_settings

from category_tree_app.models import Category


class TestModel(TestCase):

    def setUp(self):
        cat = Category.objects.create(
            image='image_1',
            name='1',
            description='description_1',
        )
        for i in range(2, 101):
            cat = Category.objects.create(
                image=f'image_{i}',
                name=str(i),
                description=f'description_{i}',
                parent_category=cat,
            )
        cat95 = Category.objects.get(name='95')
        Category.objects.create(
            parent_category=cat95,
            name='96B',
            image='image',
            description='96B'
        )

    #@override_settings(DEBUG=True)
    def test_get_parent_list(self):
        parent_list = list(Category.objects.parent_list(category_id=97, depth=-4))
        self.assertEqual(5, len(parent_list))
        self.assertEqual(parent_list[0].name, '93')
        self.assertEqual(parent_list[0].depth, -4)
        self.assertEqual(parent_list[-1].depth, 0)
        self.assertEqual(parent_list[-1].name, '97')

    #@override_settings(DEBUG=True)
    def test_get_child_tree(self):
        child_tree = list(Category.objects.child_tree(category_id=93, depth=4))
        self.assertEqual(5, len(child_tree))
        self.assertEqual(child_tree[0].name, '93')
        self.assertEqual(child_tree[0].depth, 1)
        self.assertEqual(child_tree[-1].depth, 4)
        self.assertEqual(child_tree[-1].name, '96B')
        self.assertEqual(child_tree[-2].depth, 4)
        self.assertEqual(child_tree[-2].name, '96')
