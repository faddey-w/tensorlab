from tensorlab.core import groups, models
from tensorlab import exceptions
from ._base import StorageTestCase


class GroupsStorageTests(StorageTestCase):
    __abstract_test__ = True

    def test_constructor(self):
        group = groups.Group(name='mygroup', storage=self.storage.groups)
        self.assertIsNone(group.key)
        self.assertEqual(group.name, 'mygroup')
        self.assertIs(group.storage, self.storage.groups)
        self.assertEqual(self.storage.groups.list(None), [])

    def test_create_top_level(self):
        g = groups.Group(name='grp', storage=self.storage.groups)
        self.storage.groups.create(g, None)

        self.assertIsNotNone(g.key)
        self.assertEqual(self.storage.groups.list(None), [g])
        self.assertEqual(self.storage.groups.get('grp'), g)

    def test_create_subgroup(self):
        top = groups.Group(name='top', storage=self.storage.groups)
        self.storage.groups.create(top, None)

        nested1 = groups.Group(name='nested1', storage=self.storage.groups)
        self.storage.groups.create(nested1, top)
        nested2 = groups.Group(name='nested2', storage=self.storage.groups)
        self.storage.groups.create(nested2, top)

        self.assertEqual(self.storage.groups.list(None), [top])
        self.assertEqual(self.storage.groups.list(top), [nested1, nested2])

    def test_cannot_save_two_groups_with_same_name(self):
        g = groups.Group(name='mygroup', storage=self.storage.groups)
        self.storage.groups.create(g, None)

        g2 = groups.Group(name='mygroup', storage=self.storage.groups)
        with self.assertRaises(exceptions.InvalidStateError):
            self.storage.groups.create(g2, None)

    def test_renaming(self):
        original_name = 'original-name'
        new_name = 'new-name'

        g = groups.Group(name=original_name, storage=self.storage.groups)
        self.storage.groups.create(g, None)
        [loaded_before] = self.storage.groups.list(None)

        g.name = new_name
        self.storage.groups.rename(g)
        [loaded_after] = self.storage.groups.list(None)

        self.assertEqual(loaded_before.name, original_name)
        self.assertEqual(loaded_after.name, new_name)

    def test_fields_when_dirty(self):
        g = groups.Group(name='mygroup', storage=self.storage.groups)
        self.storage.groups.create(g, None)
        g.name = 'anothername'

        self.assertEqual(self.storage.groups.get_dirty(g), {'name'})
        self.assertEqual(self.storage.groups.get_synced(g), set())

    def test_fields_when_synced(self):
        g = groups.Group(name='mygroup', storage=self.storage.groups)
        self.storage.groups.create(g, None)

        self.assertEqual(self.storage.groups.get_dirty(g), set())
        self.assertEqual(self.storage.groups.get_synced(g), {'name'})

    def test_reset_fields(self):
        g = groups.Group(name='mygroup', storage=self.storage.groups)
        self.storage.groups.create(g, None)
        g.name = 'anothername'

        self.storage.groups.reset(g)

        self.assertEqual(g.name, 'mygroup')

    def test_listing(self):
        top = groups.Group(name='top', storage=self.storage.groups)
        g1 = groups.Group(name='group1', storage=self.storage.groups)
        g2 = groups.Group(name='group2', storage=self.storage.groups)
        g3 = groups.Group(name='group3', storage=self.storage.groups)

        self.storage.groups.create(top, None)
        self.storage.groups.create(g1, top)
        self.storage.groups.create(g2, top)
        self.storage.groups.create(g3, top)

        loaded = self.storage.groups.list(top)

        self.assertEqual(loaded, [g1, g2, g3])

    def test_listing_with_filter(self):
        g1 = groups.Group(name='blob', storage=self.storage.groups)
        g2 = groups.Group(name='bob', storage=self.storage.groups)
        g3 = groups.Group(name='bab', storage=self.storage.groups)

        self.storage.groups.create(g1, None)
        self.storage.groups.create(g2, None)
        self.storage.groups.create(g3, None)

        loaded = self.storage.groups.list(None, name_pattern='b%b')
        self.assertEqual(loaded, [g1, g2, g3])

        loaded = self.storage.groups.list(None, name_pattern='b?b')
        self.assertEqual(loaded, [g2, g3])

        loaded = self.storage.groups.list(None, name_pattern='b%ob')
        self.assertEqual(loaded, [g1, g2])

    def test_deletion(self):
        g = groups.Group(name='grp', storage=self.storage.groups)
        self.storage.groups.create(g, None)
        m = models.Model(name='mdl', storage=self.storage.models)
        self.storage.models.create(m, g, {})

        self.storage.groups.delete_with_content(g)
        self.assertEqual(self.storage.models.list(g), [])

    def test_list_models(self):
        top = groups.Group(name='top', storage=self.storage.groups)
        self.storage.groups.create(top, None)
        nested = groups.Group(name='nested', storage=self.storage.groups)
        self.storage.groups.create(nested, top)

        m1 = models.Model(name='m1')
        m2 = models.Model(name='m2')
        m3 = models.Model(name='m3')
        self.storage.models.create(m1, top, {})
        self.storage.models.create(m2, top, {})
        self.storage.models.create(m3, nested, {})

        self.assertEqual(self.storage.groups.list_models(top), [m1, m2])
        self.assertEqual(self.storage.groups.list_models(nested), [m3])

    def test_count_models(self):
        top = groups.Group(name='top', storage=self.storage.groups)
        self.storage.groups.create(top, None)
        nested = groups.Group(name='nested', storage=self.storage.groups)
        self.storage.groups.create(nested, top)

        m1 = models.Model(name='m1')
        m2 = models.Model(name='m2')
        m3 = models.Model(name='m3')
        self.storage.models.create(m1, top, {})
        self.storage.models.create(m2, top, {})
        self.storage.models.create(m3, nested, {})

        self.assertEqual(self.storage.groups.count_models(top), 2)
        self.assertEqual(self.storage.groups.count_models(nested), 1)

    def test_count_runs(self):
        # TODO needed fixture for project and models
        # TODO needed fixture for runs
        pass
