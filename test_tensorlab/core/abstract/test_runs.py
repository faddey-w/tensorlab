from test_tensorlab import TestCase
from tensorlab.core import groups, models, runs
from tensorlab import exceptions


class RunsStorageTests(TestCase):
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
        run = runs.Run(storage=self.runs_storage,
                       started_at=10, finished_at=None)
        self.assertIsNone(run.key)
        self.assertEqual(run.started_at, 10)
        self.assertEqual(run.finished_at, None)
        self.assertIs(run.storage, self.models_storage)

    def is_data_path_valid(self, data_path):
        raise NotImplementedError

    def reset_mocks(self):
        raise NotImplementedError

    def is_run_started(self):
        raise NotImplementedError

    def test_create(self):
        g = groups.Group(name='grp')
        self.groups_storage.create(g, None)
        m = models.Model(name='mdl')
        self.models_storage.create(m, g, {})
        r = runs.Run(started_at=10, finished_at=None)
        data_path = self.runs_storage.create(m, r, {})

        self.assertIsNotNone(r.key)
        self.assertTrue(self.is_data_path_valid(data_path))
        self.assertTrue(self.is_run_started())
        self.assertEqual(self.models_storage.list_runs(m), [r])
        self.assertEqual(self.runs_storage.list(m), [r])

    def test_started_at_is_required(self):
        g = groups.Group(name='grp')
        self.groups_storage.create(g, None)
        m = models.Model(name='mdl')
        self.models_storage.create(m, g, {})
        r = runs.Run(started_at=None, finished_at=None)

        with self.assertRaises(exceptions.IllegalArgumentError):
            self.runs_storage.create(m, r, {})
        self.assertFalse(self.is_run_started())

    def test_get_and_list(self):
        g = groups.Group(name='grp')
        self.groups_storage.create(g, None)
        m = models.Model(name='mdl')
        self.models_storage.create(m, g, {})
        r1 = runs.Run(started_at=30, finished_at=None)
        self.runs_storage.create(m, r1, {})
        r2 = runs.Run(started_at=10, finished_at=None)
        self.runs_storage.create(m, r2, {})
        r3 = runs.Run(started_at=20, finished_at=None)
        self.runs_storage.create(m, r3, {})

        # ordered by started_at
        self.assertEqual(self.runs_storage.get(m, 0), r2)
        self.assertEqual(self.runs_storage.get(m, 1), r3)
        self.assertEqual(self.runs_storage.get(m, 2), r1)
        self.assertEqual(self.runs_storage.get(m, 3), None)
        self.assertEqual(self.runs_storage.list(m), [r2, r3, r1])

    def _fixture_run(self, started_at=None, finished_at=None):
        if not hasattr(self, '_fixture_model'):
            m = models.Model(name='mdl')
            self.models_storage.create(m, None, {})
            self._fixture_model = m
        r = runs.Run(started_at=started_at, finished_at=finished_at)
        data_path = self.runs_storage.create(self._fixture_model, r, {})
        return r, data_path

    def test_set_time(self):
        r, _ = self._fixture_run(started_at=10, finished_at=None)
        self.reset_mocks()

        self.runs_storage.set_time(r, started_at=30, finished_at=40)
        self.assertEqual(self.runs_storage.get(self._fixture_model, 0),
                         runs.Run(started_at=30, finished_at=40))
        self.assertFalse(self.is_run_started())

    def test_cannot_remove_started_time(self):
        r, _ = self._fixture_run(started_at=10, finished_at=None)

        self.runs_storage.set_time(r, started_at=None, finished_at=40)
        self.assertEqual(self.runs_storage.get(self._fixture_model, 0),
                         runs.Run(started_at=10, finished_at=40))

    def test_get_data_path(self):
        r, dp = self._fixture_run(started_at=10, finished_at=None)
        dp2 = self.runs_storage.get_data_path(r)
        self.assertEqual(dp, dp2)

    def test_get_model(self):
        r, _ = self._fixture_run(started_at=30)
        m = self.runs_storage.get_model(r)
        self.assertEqual(m, self._fixture_model)

    def test_group(self):
        r1, _ = self._fixture_run(started_at=30)
        self.reset_mocks()
        self.assertEqual(self.runs_storage.get_group(r1), None)

        g2 = groups.Group(name='grp')
        self.groups_storage.create(g2, None)
        m2 = models.Model(name='mdl')
        self.models_storage.create(m2, g2, {})
        r2 = runs.Run(started_at=30, finished_at=None)
        self.runs_storage.create(m2, r2, {})
        self.assertEqual(self.runs_storage.get_group(r2), g2)

    def test_delete(self):
        r, dp = self._fixture_run(started_at=10, finished_at=None)
        self.runs_storage.delete(r)
        self.assertFalse(self.is_data_path_valid(dp))
        self.assertFalse(self.is_run_started())
