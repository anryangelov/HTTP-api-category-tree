from django.db import models


class CategoryManager(models.Manager):

    PARENT_LIST_QUERY = '''
        WITH RECURSIVE parents AS (
            SELECT category_tree_app_category.*, 0 AS depth
            FROM category_tree_app_category
            WHERE category_id = %s

            UNION ALL

            SELECT category_tree_app_category.*, parents.depth - 1
            FROM category_tree_app_category, parents
            WHERE category_tree_app_category.category_id = parents.parent_category_id
            LIMIT %s
        )
        SELECT category_id, name, parent_category_id, depth
        FROM parents
        ORDER BY depth
        '''

    CHILD_TREE_QUERY = '''
        WITH RECURSIVE childs AS (
            SELECT category_tree_app_category.*, 1 AS depth
            FROM category_tree_app_category
            WHERE category_id = %s

            UNION ALL

            SELECT category_tree_app_category.*, childs.depth + 1
            FROM category_tree_app_category, childs
            WHERE category_tree_app_category.parent_category_id = childs.category_id
            AND depth <= %s
        )
        SELECT category_id, name, parent_category_id, depth
        FROM childs
        ORDER BY depth, category_id
        '''

    def parent_list(self, category_id, depth=None):
        depth = depth or 2000
        return self.raw(self.PARENT_LIST_QUERY, [category_id, abs(depth) + 1])

    def child_list(self, category_id, depth=None):
        depth = depth or 2000
        return self.raw(self.CHILD_TREE_QUERY, [category_id, depth - 1])
