from tensorlab.core import groups, models, runs
from tensorlab import exceptions
from test_tensorlab.lib import TestCase


class RunsStorageTests(TestCase):
    """
    :type storage: tensorlab.core.facade.TensorLabStorage
    """
    __abstract_test__ = True

    storage = None

    def test_constructor(self):
        run = runs.Run(storage=self.storage.runs,
                       started_at=10, finished_at=None)
        self.assertIsNone(run.key)
        self.assertEqual(run.started_at, 10)
        self.assertEqual(run.finished_at, None)
        self.assertIs(run.storage, self.storage.runs)

    def is_data_path_valid(self, data_path):
        raise NotImplementedError

    def reset_mocks(self):
        raise NotImplementedError

    def is_run_started(self):
        raise NotImplementedError

    def test_create(self):
        g = groups.Group(name='grp')
        self.storage.groups.create(g, None)
        m = models.Model(name='mdl')
        self.storage.models.create(m, g, {})
        r = runs.Run(started_at=10, finished_at=None)
        data_path = self.storage.runs.create(m, r, {})

        self.assertIsNotNone(r.key)
        self.assertTrue(self.is_data_path_valid(data_path))
        self.assertTrue(self.is_run_started())
        self.assertEqual(self.storage.models.list_runs(m), [r])
        self.assertEqual(self.storage.runs.list(m), [r])

    def test_started_at_is_required(self):
        g = groups.Group(name='grp')
        self.storage.groups.create(g, None)
        m = models.Model(name='mdl')
        self.storage.models.create(m, g, {})
        r = runs.Run(started_at=None, finished_at=None)

        with self.assertRaises(exceptions.IllegalArgumentError):
            self.storage.runs.create(m, r, {})
        self.assertFalse(self.is_run_started())

    def test_get_and_list(self):
        g = groups.Group(name='grp')
        self.storage.groups.create(g, None)
        m = models.Model(name='mdl')
        self.storage.models.create(m, g, {})
        r1 = runs.Run(started_at=30, finished_at=None)
        self.storage.runs.create(m, r1, {})
        r2 = runs.Run(started_at=10, finished_at=None)
        self.storage.runs.create(m, r2, {})
        r3 = runs.Run(started_at=20, finished_at=None)
        self.storage.runs.create(m, r3, {})

        # ordered by started_at
        self.assertEqual(self.storage.runs.get(m, 0), r2)
        self.assertEqual(self.storage.runs.get(m, 1), r3)
        self.assertEqual(self.storage.runs.get(m, 2), r1)
        self.assertEqual(self.storage.runs.get(m, 3), None)
        self.assertEqual(self.storage.runs.list(m), [r2, r3, r1])

    def _fixture_run(self, started_at=None, finished_at=None):
        if not hasattr(self, '_fixture_model'):
            m = models.Model(name='mdl')
            self.storage.models.create(m, None, {})
            self._fixture_model = m
        r = runs.Run(started_at=started_at, finished_at=finished_at)
        data_path = self.storage.runs.create(self._fixture_model, r, {})
        return r, data_path

    def test_set_time(self):
        r, _ = self._fixture_run(started_at=10, finished_at=None)
        self.reset_mocks()

        self.storage.runs.set_time(r, started_at=30, finished_at=40)
        self.assertEqual(self.storage.runs.get(self._fixture_model, 0),
                         runs.Run(started_at=30, finished_at=40))
        self.assertFalse(self.is_run_started())

    def test_cannot_remove_started_time(self):
        r, _ = self._fixture_run(started_at=10, finished_at=None)

        self.storage.runs.set_time(r, started_at=None, finished_at=40)
        self.assertEqual(self.storage.runs.get(self._fixture_model, 0),
                         runs.Run(started_at=10, finished_at=40))

    def test_get_data_path(self):
        r, dp = self._fixture_run(started_at=10, finished_at=None)
        dp2 = self.storage.runs.get_data_path(r)
        self.assertEqual(dp, dp2)

    def test_get_model(self):
        r, _ = self._fixture_run(started_at=30)
        m = self.storage.runs.get_model(r)
        self.assertEqual(m, self._fixture_model)

    def test_group(self):
        r1, _ = self._fixture_run(started_at=30)
        self.reset_mocks()
        self.assertEqual(self.storage.runs.get_group(r1), None)

        g2 = groups.Group(name='grp')
        self.storage.groups.create(g2, None)
        m2 = models.Model(name='mdl')
        self.storage.models.create(m2, g2, {})
        r2 = runs.Run(started_at=30, finished_at=None)
        self.storage.runs.create(m2, r2, {})
        self.assertEqual(self.storage.runs.get_group(r2), g2)

    def test_delete(self):
        r, dp = self._fixture_run(started_at=10, finished_at=None)
        self.storage.runs.delete(r)
        self.assertFalse(self.is_data_path_valid(dp))
        self.assertFalse(self.is_run_started())
