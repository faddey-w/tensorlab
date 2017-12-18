from test_tensorlab.core.abstract import (
    test_attributes, test_filtering_by_predicate,
    test_groups_storage, test_models_storage, test_runs
)
from test_tensorlab.lib import TestCase

import os
import io
import shutil
import tempfile
from unittest import mock
from tensorlab.local_storage import LocalStorage


class _LocalStorageSetUp(TestCase):

    def setUp(self):
        self.storage_dir = tempfile.mkdtemp()
        self.user_project = mock.Mock()
        self.logstream = io.StringIO()
        # noinspection PyTypeChecker
        self.storage = LocalStorage(
            self.storage_dir,
            self.user_project,
            self.logstream,
        ).Create()
        super(_LocalStorageSetUp, self).setUp()

    def tearDown(self):
        super(_LocalStorageSetUp, self).tearDown()
        shutil.rmtree(self.storage_dir)


class GroupsLocalStorageTests(
        _LocalStorageSetUp, test_groups_storage.GroupsStorageTests):
    pass


class AttributesLocalStorageTests(_LocalStorageSetUp,
                                  test_attributes.AttributesStorageTests):
    pass


class ModelsLocalStorageTests(
        _LocalStorageSetUp, test_models_storage.ModelsStorageTests):

    def setUp(self):
        super(ModelsLocalStorageTests, self).setUp()
        self.user_project.build.side_effect = self._build_side_effect

    def _build_side_effect(self, attributes, data_path, stream):
        stream.write('some logging')

    def reset_mocks(self):
        self.user_project.reset_mock()

    def is_build_model_called(self, attributes=None):
        yes = (1 == self.user_project.build.call_count)
        if yes and attributes is not None:
            call = self.user_project.build.call_args_list[0]
            yes = (attributes == call[0][0]) \
                  and self.logstream.getvalue() == 'some logging'
        return yes

    def is_data_path_valid(self, data_dir):
        return os.path.isdir(data_dir)


class RunsLocalStorageTests(
        _LocalStorageSetUp, test_runs.RunsStorageTests):

    def setUp(self):
        super(RunsLocalStorageTests, self).setUp()
        self.user_project.run.side_effect = self._run_side_effect

    def _run_side_effect(self, attributes, model_data_dir, tun_data_dir, stream):
        stream.write('some logging')

    def is_run_started(self):
        raise NotImplementedError

    def is_data_path_valid(self, data_dir):
        return os.path.isdir(data_dir)

    def reset_mocks(self):
        self.user_project.reset_mock()


class TestFilteringByPredicateOnModelsLocalStorage(
        test_filtering_by_predicate.ModelFilteringTests, _LocalStorageSetUp):
    pass


class TestFilteringByPredicateOnRunsLocalStorage(
        _LocalStorageSetUp, test_filtering_by_predicate.RunFilteringTests):
    pass
