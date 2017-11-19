from test_tensorlab import TestCase
from tensorlab.core import groups
from tensorlab import exceptions


class GroupStorageTests(TestCase):
    """
    :type groups_storage: tensorlab.core.groups.GroupsStorage
    :type models_storage: tensorlab.core.models.ModelsStorage
    :type instances_storage: tensorlab.core.instances.InstancesStorage
    :type runs_storage: tensorlab.core.runs.RunsStorage
    """
    __abstract_test__ = True

    groups_storage = None
    models_storage = None
    instances_storage = None
    runs_storage = None

    def test_constructor(self):
        group = groups.Group(name='mygroup', storage=self.groups_storage)
        self.assertIsNone(group.key)
        self.assertEqual(group.name, 'mygroup')
        self.assertIs(group.storage, self.groups_storage)
        self.assertEqual(self.groups_storage.list(), [])

    def test_saving_first_time(self):
        g = groups.Group(name='grp', storage=self.groups_storage)
        self.groups_storage.save(g)

        self.assertIsNotNone(g.key)
        self.assertEqual(self.groups_storage.list(), [g])
        self.assertEqual(self.groups_storage.get('grp'), g)

    def test_cannot_save_two_groups_with_same_name(self):
        g = groups.Group(name='mygroup', storage=self.groups_storage)
        self.groups_storage.save(g)

        g2 = groups.Group(name='mygroup', storage=self.groups_storage)
        with self.assertRaises(exceptions.InvalidStateError):
            self.groups_storage.save(g2)

    def test_updating(self):
        original_name = 'original-name'
        new_name = 'new-name'

        g = groups.Group(name=original_name, storage=self.groups_storage)
        self.groups_storage.save(g)
        [loaded_before] = self.groups_storage.list()

        g.name = new_name
        self.groups_storage.save(g)
        [loaded_after] = self.groups_storage.list()

        self.assertEqual(loaded_before.name, original_name)
        self.assertEqual(loaded_after.name, new_name)

    def test_fields_when_dirty(self):
        g = groups.Group(name='mygroup', storage=self.groups_storage)
        self.groups_storage.save(g)
        g.name = 'anothername'

        self.assertEqual(self.groups_storage.get_dirty(g), {'name'})
        self.assertEqual(self.groups_storage.get_synced(g), set())

    def test_fields_when_synced(self):
        g = groups.Group(name='mygroup', storage=self.groups_storage)
        self.groups_storage.save(g)

        self.assertEqual(self.groups_storage.get_dirty(g), set())
        self.assertEqual(self.groups_storage.get_synced(g), {'name'})

    def test_reset_fields(self):
        g = groups.Group(name='mygroup', storage=self.groups_storage)
        self.groups_storage.save(g)
        g.name = 'anothername'

        self.groups_storage.reset(g)

        self.assertEqual(g.name, 'mygroup')

    def test_listing(self):
        g1 = groups.Group(name='group1', storage=self.groups_storage)
        g2 = groups.Group(name='group2', storage=self.groups_storage)
        g3 = groups.Group(name='group3', storage=self.groups_storage)

        self.groups_storage.save(g1)
        self.groups_storage.save(g2)
        self.groups_storage.save(g3)

        loaded = self.groups_storage.list()

        self.assertEqual(loaded, [g1, g2, g3])

    def test_listing_with_filter(self):
        g1 = groups.Group(name='blob', storage=self.groups_storage)
        g2 = groups.Group(name='bob', storage=self.groups_storage)
        g3 = groups.Group(name='bab', storage=self.groups_storage)

        self.groups_storage.save(g1)
        self.groups_storage.save(g2)
        self.groups_storage.save(g3)

        loaded = self.groups_storage.list('b%b')
        self.assertEqual(loaded, [g1, g2, g3])

        loaded = self.groups_storage.list('b?b')
        self.assertEqual(loaded, [g2, g3])

        loaded = self.groups_storage.list('b%ob')
        self.assertEqual(loaded, [g1, g2])

    def test_deletion(self):
        # TODO needed fixture for project and models
        pass

    def test_list_models(self):
        # TODO needed fixture for project and models
        pass

    def test_count_models(self):
        # TODO needed fixture for project and models
        pass

    def test_count_instances(self):
        # TODO needed fixture for project and models
        # TODO needed fixture for instances
        pass

    def test_count_runs(self):
        # TODO needed fixture for project and models
        # TODO needed fixture for instances
        # TODO needed fixture for runs
        pass
