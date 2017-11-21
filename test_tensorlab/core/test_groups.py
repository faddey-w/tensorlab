from test_tensorlab import TestCase
from tensorlab.core import groups, models
from tensorlab import exceptions


class GroupStorageTests(TestCase):
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
        group = groups.Group(name='mygroup', storage=self.groups_storage)
        self.assertIsNone(group.key)
        self.assertEqual(group.name, 'mygroup')
        self.assertIs(group.storage, self.groups_storage)
        self.assertEqual(self.groups_storage.list(None), [])

    def test_create_top_level(self):
        g = groups.Group(name='grp', storage=self.groups_storage)
        self.groups_storage.create(g, None)

        self.assertIsNotNone(g.key)
        self.assertEqual(self.groups_storage.list(None), [g])
        self.assertEqual(self.groups_storage.get('grp'), g)

    def test_create_subgroup(self):
        top = groups.Group(name='top', storage=self.groups_storage)
        self.groups_storage.create(top, None)

        nested1 = groups.Group(name='nested1', storage=self.groups_storage)
        self.groups_storage.create(nested1, top)
        nested2 = groups.Group(name='nested2', storage=self.groups_storage)
        self.groups_storage.create(nested2, top)

        self.assertEqual(self.groups_storage.list(None), [top])
        self.assertEqual(self.groups_storage.list(top), [nested1, nested2])

    def test_cannot_save_two_groups_with_same_name(self):
        g = groups.Group(name='mygroup', storage=self.groups_storage)
        self.groups_storage.create(g, None)

        g2 = groups.Group(name='mygroup', storage=self.groups_storage)
        with self.assertRaises(exceptions.InvalidStateError):
            self.groups_storage.create(g2, None)

    def test_renaming(self):
        original_name = 'original-name'
        new_name = 'new-name'

        g = groups.Group(name=original_name, storage=self.groups_storage)
        self.groups_storage.create(g, None)
        [loaded_before] = self.groups_storage.list(None)

        g.name = new_name
        self.groups_storage.rename(g)
        [loaded_after] = self.groups_storage.list(None)

        self.assertEqual(loaded_before.name, original_name)
        self.assertEqual(loaded_after.name, new_name)

    def test_fields_when_dirty(self):
        g = groups.Group(name='mygroup', storage=self.groups_storage)
        self.groups_storage.create(g, None)
        g.name = 'anothername'

        self.assertEqual(self.groups_storage.get_dirty(g), {'name'})
        self.assertEqual(self.groups_storage.get_synced(g), set())

    def test_fields_when_synced(self):
        g = groups.Group(name='mygroup', storage=self.groups_storage)
        self.groups_storage.create(g, None)

        self.assertEqual(self.groups_storage.get_dirty(g), set())
        self.assertEqual(self.groups_storage.get_synced(g), {'name'})

    def test_reset_fields(self):
        g = groups.Group(name='mygroup', storage=self.groups_storage)
        self.groups_storage.create(g, None)
        g.name = 'anothername'

        self.groups_storage.reset(g)

        self.assertEqual(g.name, 'mygroup')

    def test_listing(self):
        top = groups.Group(name='top', storage=self.groups_storage)
        g1 = groups.Group(name='group1', storage=self.groups_storage)
        g2 = groups.Group(name='group2', storage=self.groups_storage)
        g3 = groups.Group(name='group3', storage=self.groups_storage)

        self.groups_storage.create(top, None)
        self.groups_storage.create(g1, top)
        self.groups_storage.create(g2, top)
        self.groups_storage.create(g3, top)

        loaded = self.groups_storage.list(top)

        self.assertEqual(loaded, [g1, g2, g3])

    def test_listing_with_filter(self):
        g1 = groups.Group(name='blob', storage=self.groups_storage)
        g2 = groups.Group(name='bob', storage=self.groups_storage)
        g3 = groups.Group(name='bab', storage=self.groups_storage)

        self.groups_storage.create(g1, None)
        self.groups_storage.create(g2, None)
        self.groups_storage.create(g3, None)

        loaded = self.groups_storage.list(None, name_pattern='b%b')
        self.assertEqual(loaded, [g1, g2, g3])

        loaded = self.groups_storage.list(None, name_pattern='b?b')
        self.assertEqual(loaded, [g2, g3])

        loaded = self.groups_storage.list(None, name_pattern='b%ob')
        self.assertEqual(loaded, [g1, g2])

    def test_deletion(self):
        g = groups.Group(name='grp', storage=self.groups_storage)
        self.groups_storage.create(g, None)
        m = models.Model(name='mdl', storage=self.models_storage)
        self.models_storage.create(m, g, {})

        self.groups_storage.delete_with_content(g)
        self.assertEqual(self.models_storage.list(g), [])

    def test_list_models(self):
        top = groups.Group(name='top', storage=self.groups_storage)
        self.groups_storage.create(top, None)
        nested = groups.Group(name='nested', storage=self.groups_storage)
        self.groups_storage.create(nested, top)

        m1 = models.Model(name='m1')
        m2 = models.Model(name='m2')
        m3 = models.Model(name='m3')
        self.models_storage.create(m1, top, {})
        self.models_storage.create(m2, top, {})
        self.models_storage.create(m3, nested, {})

        self.assertEqual(self.groups_storage.list_models(top), [m1, m2])
        self.assertEqual(self.groups_storage.list_models(nested), [m3])

    def test_count_models(self):
        top = groups.Group(name='top', storage=self.groups_storage)
        self.groups_storage.create(top, None)
        nested = groups.Group(name='nested', storage=self.groups_storage)
        self.groups_storage.create(nested, top)

        m1 = models.Model(name='m1')
        m2 = models.Model(name='m2')
        m3 = models.Model(name='m3')
        self.models_storage.create(m1, top, {})
        self.models_storage.create(m2, top, {})
        self.models_storage.create(m3, nested, {})

        self.assertEqual(self.groups_storage.count_models(top), 2)
        self.assertEqual(self.groups_storage.count_models(nested), 1)

    def test_count_runs(self):
        # TODO needed fixture for project and models
        # TODO needed fixture for runs
        pass
