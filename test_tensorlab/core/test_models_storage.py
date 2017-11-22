from test_tensorlab import TestCase
from tensorlab.core import groups, models, runs


class ModelsStorageTests(TestCase):
    """
    :type groups_storage: tensorlab.core.groups.GroupsStorage
    :type models_storage: tensorlab.core.models.ModelsStorage
    :type runs_storage: tensorlab.core.runs.RunsStorage
    """
    __abstract_test__ = True

    groups_storage = None
    models_storage = None
    runs_storage = None

    def test_constructor(self):
        model = models.Model(name='mymodel', storage=self.models_storage)
        self.assertIsNone(model.key)
        self.assertEqual(model.name, 'mymodel')
        self.assertIs(model.storage, self.models_storage)

    def is_data_path_valid(self, data_dir):
        raise NotImplementedError

    def test_create(self):
        g = groups.Group(name='grp')
        self.groups_storage.create(g, None)
        m = models.Model(name='mdl')
        data_path = self.models_storage.create(m, g, {})

        self.assertIsNotNone(m.key)
        self.assertTrue(self.is_data_path_valid(data_path))
        self.assertEqual(self.groups_storage.list_models(None), [])
        self.assertEqual(self.groups_storage.list_models(g), [m])
        self.assertEqual(self.models_storage.list(None), [])
        self.assertEqual(self.models_storage.list(g), [m])

    def test_create_for_root_group(self):
        m = models.Model(name='mdl')
        data_path = self.models_storage.create(m, None, {})

        self.assertIsNotNone(m.key)
        self.assertTrue(self.is_data_path_valid(data_path))
        self.assertEqual(self.groups_storage.list_models(None), [m])
        self.assertEqual(self.models_storage.list(None), [])

    def test_get_by_name(self):
        g = groups.Group(name='grp')
        self.groups_storage.create(g, None)
        m = models.Model(name='somename')
        self.models_storage.create(m, g, {})

        self.assertEqual(self.models_storage.get(g, 'somename'), m)

    def test_renaming(self):
        g = groups.Group(name='grp')
        self.groups_storage.create(g, None)

        original_name = 'original-name'
        new_name = 'new-name'

        m = models.Model(name=original_name)
        self.models_storage.create(m, g, {})
        [loaded_before] = self.models_storage.list(g)

        m.name = new_name
        self.models_storage.rename(m)
        [loaded_after] = self.models_storage.list(None)

        self.assertEqual(loaded_before.name, original_name)
        self.assertEqual(loaded_after.name, new_name)

    def test_get_group(self):
        g = groups.Group(name='grp')
        self.groups_storage.create(g, None)
        m = models.Model(name='somename')
        self.models_storage.create(m, g, {})

        self.assertEqual(self.models_storage.get_group(m), g)

    def test_get_data_dir(self):
        g = groups.Group(name='grp')
        self.groups_storage.create(g, None)
        m = models.Model(name='somename')
        data_path = self.models_storage.create(m, g, {})

        self.assertEqual(self.models_storage.get_data_path(m), data_path)

    def test_list_runs_and_count_runs(self):
        g = groups.Group(name='grp')
        self.groups_storage.create(g, None)
        m = models.Model(name='somename')
        self.models_storage.create(m, g, {})

        r1 = runs.Run(started_at=5, finished_at=10)
        r2 = runs.Run(started_at=1, finished_at=15)
        r3 = runs.Run(started_at=2, finished_at=8)
        self.runs_storage.create(m, r1, {})
        self.runs_storage.create(m, r2, {})
        self.runs_storage.create(m, r3, {})

        # note order: ascending by started_at
        self.assertEqual(self.models_storage.list_runs(m), [r2, r3, r1])
        self.assertEqual(self.models_storage.count_runs(m), 3)

    def test_delete(self):
        g = groups.Group(name='grp')
        self.groups_storage.create(g, None)
        m = models.Model(name='somename')
        self.models_storage.create(m, g, {})

        self.models_storage.delete_with_content(m)

        self.assertEqual(self.models_storage.list(g), [])
