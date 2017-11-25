from test_tensorlab.lib import TestCase
from tensorlab.core import groups, models, runs, attributes, attributeoptions


class StorageTestCase(TestCase):
    """
    :type groups_storage: tensorlab.core.groups.GroupsStorage
    :type models_storage: tensorlab.core.models.ModelsStorage
    :type runs_storage: tensorlab.core.runs.RunsStorage
    :type attributes_storage: tensorlab.core.attributes.AttributeStorage
    """
    __abstract_test__ = True

    groups_storage = None
    models_storage = None
    runs_storage = None
    attributes_storage = None

    def _fixture_attr(self, group, name='myattr', runtime=False,
                      type=attributeoptions.AttributeType.String,
                      options='', default=None, nullable=False):
        attr = attributes.Attribute(
            name=name, runtime=runtime, type=type,
            options=options, default=default, nullable=nullable)
        self.attributes_storage.create(attr, group)
        return attr

    def _fixture_group(self, name='mygroup', parent=None):
        g = groups.Group(name=name)
        self.groups_storage.create(g, parent)
        return g

    def _fixture_model(self, group, name, attr_values):
        m = models.Model(name=name)
        self.models_storage.create(m, group, attr_values)
        return m

    def _fixture_run(self, model, attr_values, started_at=5, finished_at=10):
        r = runs.Run(started_at=started_at, finished_at=finished_at)
        self.runs_storage.create(model, r, attr_values)
        return r
