from test_tensorlab.lib import TestCase
from tensorlab.core import groups, models, runs, attributes, attributeoptions


class StorageTestCase(TestCase):
    """
    :type storage: tensorlab.core.facade.TensorLabStorage
    """
    __abstract_test__ = True

    storage = None

    def _fixture_attr(self, group, name='myattr', runtime=False,
                      type=attributeoptions.AttributeType.String,
                      options='', default=None, nullable=False):
        attr = attributes.Attribute(
            name=name, runtime=runtime, type=type,
            options=options, default=default, nullable=nullable)
        self.storage.attributes.create(attr, group)
        return attr

    def _fixture_group(self, name='mygroup', parent=None):
        g = groups.Group(name=name)
        self.storage.groups.create(g, parent)
        return g

    def _fixture_model(self, group, name, attr_values):
        m = models.Model(name=name)
        self.storage.models.create(m, group, attr_values)
        return m

    def _fixture_run(self, model, attr_values, started_at=5, finished_at=10):
        r = runs.Run(started_at=started_at, finished_at=finished_at)
        self.storage.runs.create(model, r, attr_values)
        return r
