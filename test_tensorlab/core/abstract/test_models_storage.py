from tensorlab.core import groups, models, runs
from ._base import StorageTestCase


class ModelsStorageTests(StorageTestCase):
    __abstract_test__ = True

    def test_constructor(self):
        model = models.Model(name='mymodel', storage=self.storage.models)
        self.assertIsNone(model.key)
        self.assertEqual(model.name, 'mymodel')
        self.assertIs(model.storage, self.storage.models)

    def is_data_path_valid(self, data_dir):
        raise NotImplementedError

    def reset_mocks(self):
        raise NotImplementedError

    def is_build_model_called(self):
        raise NotImplementedError

    def test_create(self):
        g = groups.Group(name='grp')
        self.storage.groups.create(g, None)
        m = models.Model(name='mdl')
        data_path = self.storage.models.create(m, g, {})

        self.assertIsNotNone(m.key)
        self.assertTrue(self.is_data_path_valid(data_path))
        self.assertTrue(self.is_build_model_called())
        self.assertEqual(self.storage.groups.list_models(None), [])
        self.assertEqual(self.storage.groups.list_models(g), [m])
        self.assertEqual(self.storage.models.list(None), [])
        self.assertEqual(self.storage.models.list(g), [m])

    def test_create_for_root_group(self):
        m = models.Model(name='mdl')
        data_path = self.storage.models.create(m, None, {})

        self.assertIsNotNone(m.key)
        self.assertTrue(self.is_data_path_valid(data_path))
        self.assertTrue(self.is_build_model_called())
        self.assertEqual(self.storage.groups.list_models(None), [m])
        self.assertEqual(self.storage.models.list(None), [])

    def test_get_by_name(self):
        g = groups.Group(name='grp')
        self.storage.groups.create(g, None)
        m = models.Model(name='somename')
        self.storage.models.create(m, g, {})

        self.assertEqual(self.storage.models.get(g, 'somename'), m)

    def test_renaming(self):
        g = groups.Group(name='grp')
        self.storage.groups.create(g, None)

        original_name = 'original-name'
        new_name = 'new-name'

        m = models.Model(name=original_name)
        self.storage.models.create(m, g, {})
        [loaded_before] = self.storage.models.list(g)
        self.reset_mocks()

        m.name = new_name
        self.storage.models.rename(m)
        [loaded_after] = self.storage.models.list(None)

        self.assertEqual(loaded_before.name, original_name)
        self.assertEqual(loaded_after.name, new_name)
        self.assertFalse(self.is_build_model_called())

    def test_get_group(self):
        g = groups.Group(name='grp')
        self.storage.groups.create(g, None)
        m = models.Model(name='somename')
        self.storage.models.create(m, g, {})

        self.assertEqual(self.storage.models.get_group(m), g)

    def test_get_data_dir(self):
        g = groups.Group(name='grp')
        self.storage.groups.create(g, None)
        m = models.Model(name='somename')
        data_path = self.storage.models.create(m, g, {})

        self.assertEqual(self.storage.models.get_data_path(m), data_path)

    def test_list_runs_and_count_runs(self):
        g = groups.Group(name='grp')
        self.storage.groups.create(g, None)
        m = models.Model(name='somename')
        self.storage.models.create(m, g, {})

        r1 = runs.Run(started_at=5, finished_at=10)
        r2 = runs.Run(started_at=1, finished_at=15)
        r3 = runs.Run(started_at=2, finished_at=8)
        self.storage.runs.create(m, r1, {})
        self.storage.runs.create(m, r2, {})
        self.storage.runs.create(m, r3, {})

        # note order: ascending by started_at
        self.assertEqual(self.storage.models.list_runs(m), [r2, r3, r1])
        self.assertEqual(self.storage.models.count_runs(m), 3)

    def test_delete(self):
        g = groups.Group(name='grp')
        self.storage.groups.create(g, None)
        m = models.Model(name='somename')
        data_path = self.storage.models.create(m, g, {})
        self.reset_mocks()

        self.storage.models.delete_with_content(m)

        self.assertEqual(self.storage.models.list(g), [])
        self.assertFalse(self.is_data_path_valid(data_path))
        self.assertFalse(self.is_build_model_called())
