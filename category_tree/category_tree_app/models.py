from django.db import models

from category_tree_app.managers import CategoryManager


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    parent_category = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='uploads/%Y/%m/%d/')
    similarity = models.ManyToManyField('self')

    objects = CategoryManager()

    def __str__(self):
        return f'{self.pk}_{self.name}'