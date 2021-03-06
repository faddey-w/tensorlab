from ._base import StorageTestCase
from tensorlab.core import attributes
from tensorlab.core.attributeoptions import AttributeType
from tensorlab import exceptions


class AttributesStorageTests(StorageTestCase):
    __abstract_test__ = True

    def test_constructor(self):
        attr = attributes.Attribute(
            storage=self.storage.attributes,
            name='myattr',
            runtime=False,
            type=AttributeType.String
        )
        self.assertIsNone(attr.key)
        self.assertIs(attr.storage, self.storage.attributes)

    def test_creation_for_root_group(self):
        a = self._fixture_attr(None)
        self.assertIsNotNone(a.key)
        self.assertEqual(a.storage, self.storage.attributes)
        self.assertEqual(self.storage.attributes.list(None), [a])

    def test_creation_for_subgroup(self):
        g = self._fixture_group()
        a = self._fixture_attr(g)
        self.assertIsNotNone(a.key)
        self.assertEqual(a.storage, self.storage.attributes)
        self.assertEqual(self.storage.attributes.list(None), [])
        self.assertEqual(self.storage.attributes.list(g), [a])

    def test_dirty_and_synced_fields(self):
        a = self._fixture_attr(None)
        a.runtime = not a.runtime
        a.default = 'something'
        a.name = a.name[::-1]

        self.assertEqual(
            self.storage.attributes.get_dirty(a),
            {'runtime', 'default', 'name'})
        self.assertEqual(
            self.storage.attributes.get_synced(a),
            {'type', 'options', 'nullable'})

        self.storage.attributes.reset(a)
        self.assertEqual(
            self.storage.attributes.get_dirty(a),
            set())
        self.assertEqual(
            self.storage.attributes.get_synced(a),
            {'runtime', 'default', 'name', 'type', 'options', 'nullable'})

    def test_updating(self):
        a = self._fixture_attr(
            None, type=AttributeType.Enum,
            options='qwe;asd;zxc'
        )
        a.nullable = not a.nullable
        a.default = 'qwe'
        self.storage.attributes.update(a)
        self.assertEqual(self.storage.attributes.get_dirty(a), set())

        [a_] = self.storage.attributes.list(None)
        self.assertEqual(a, a_)

    def test_name_type_and_runtime_flag_cannot_be_updated(self):
        a = self._fixture_attr(None)

        a.name = a.name[::-1]
        with self.assertRaises(exceptions.IllegalArgumentError):
            self.storage.attributes.update(a)
        self.storage.attributes.reset(a)

        a.type = AttributeType.Integer
        with self.assertRaises(exceptions.IllegalArgumentError):
            self.storage.attributes.update(a)
        self.storage.attributes.reset(a)

        a.runtime = not a.runtime
        with self.assertRaises(exceptions.IllegalArgumentError):
            self.storage.attributes.update(a)

    def test_enum_choices_cannot_be_updated_if_used(self):
        a = self._fixture_attr(None, name='enumattr', type=AttributeType.Enum,
                               options='wer;sdf;xcv', runtime=False)
        self._fixture_model(None, 'mymodel', {'enumattr': 'sdf'})

        a.options = 'sdf;xcv;tyu'
        self.storage.attributes.update(a)

        a.options = 'sdf'
        self.storage.attributes.update(a)

        a.options = 'qwe;rty;uio'
        with self.assertRaises(exceptions.IllegalArgumentError):
            self.storage.attributes.update(a)

    def test_cannot_override_required_as_nullable(self):
        g = self._fixture_group('grp')
        sg = self._fixture_group('subgrp', g)

        self._fixture_attr(g)
        with self.assertRaises(exceptions.IllegalArgumentError):
            self._fixture_attr(sg, nullable=True)

    def test_get_defining_group(self):
        g = self._fixture_group('grp')
        sg = self._fixture_group('subgrp', g)

        a = self._fixture_attr(sg)
        self.assertEqual(self.storage.attributes.get_defining_group(a), sg)

    def test_list(self):
        g = self._fixture_group('grp')
        sg = self._fixture_group('subgrp', g)
        a1 = self._fixture_attr(None, name='a')
        a2 = self._fixture_attr(g, name='b')
        a3 = self._fixture_attr(sg, name='c')
        a4 = self._fixture_attr(sg, name='d')

        self.assertEqual(set(self.storage.attributes.list(g)), {a3, a4})

    def test_list_effective(self):
        g = self._fixture_group('grp')
        sg = self._fixture_group('subgrp', g)
        a1 = self._fixture_attr(None, name='a')
        a2 = self._fixture_attr(g, name='b')
        a3 = self._fixture_attr(sg, name='c')
        a4 = self._fixture_attr(sg, name='d')

        self.assertEqual(set(self.storage.attributes.list(g)), {a1, a2, a3, a4})

    def test_apply_attribute_to_model(self):
        a = self._fixture_attr(None)

        m = self._fixture_model(None, 'mdl', {a.name: 'somestring'})

        self.assertEqual(self.storage.attributes.get_attr_values_for_model(m),
                         {a.name: 'somestring'})

    def test_apply_runtime_attribute_to_run(self):
        a = self._fixture_attr(None, runtime=True)
        m = self._fixture_model(None, 'mdl', {})
        r = self._fixture_run(m, {a.name: 'somestring'})

        self.assertEqual(self.storage.attributes.get_attr_values_for_run(r),
                         {a.name: 'somestring'})

    def test_cannot_apply_runtime_attribute_to_model(self):
        a = self._fixture_attr(None, runtime=True)

        with self.assertRaises(exceptions.IllegalArgumentError):
            self._fixture_model(None, 'mdl', {a.name: 'somestring'})

    def test_cannot_accept_value_for_non_existing_attribute(self):
        a = self._fixture_attr(None)

        with self.assertRaises(exceptions.IllegalArgumentError):
            self._fixture_model(None, 'mdl', {a.name[::-1]: 'somestring'})

    def test_attribute_is_not_required_if_has_default(self):
        a = self._fixture_attr(None, default='defaultvalue')

        m = self._fixture_model(None, 'mdl', {})

        self.assertEqual(self.storage.attributes.get_attr_values_for_model(m),
                         {a.name: 'defaultvalue'})

    def test_attribute_is_not_required_if_nullable(self):
        a = self._fixture_attr(None, nullable=True)

        m = self._fixture_model(None, 'mdl', {})

        self.assertEqual(self.storage.attributes.get_attr_values_for_model(m),
                         {a.name: None})

    def test_cannot_create_required_attribute_if_have_object(self):
        self._fixture_model(None, 'mdl', {})

        with self.assertRaises(exceptions.InvalidStateError):
            self._fixture_attr(None)

    def test_cannot_make_non_nullable_if_need_to_define_value(self):
        a = self._fixture_attr(None, nullable=True)
        self._fixture_model(None, 'mdl', {})

        a.nullable = False
        with self.assertRaises(exceptions.InvalidStateError):
            self.storage.attributes.update(a)

    def test_cannot_remove_default_if_need_to_define_value(self):
        a = self._fixture_attr(None, default='defaultvalue')
        self._fixture_model(None, 'mdl', {})

        a.default = None
        with self.assertRaises(exceptions.InvalidStateError):
            self.storage.attributes.update(a)

    def test_cannot_create_object_without_value_for_required_attribute(self):
        self._fixture_attr(None)

        with self.assertRaises(exceptions.IllegalArgumentError):
            self._fixture_model(None, 'mdl', {})

    def test_can_create_required_attribute_if_no_objects(self):
        g = self._fixture_group('grp')
        sg = self._fixture_group('subgrp', g)
        self._fixture_model(g, 'mdl', {})

        self._fixture_attr(sg)

    def test_integer_validation(self):
        a = self._fixture_attr(None, type=AttributeType.Integer)

        self._fixture_model(None, 'm1', {a.name: 10})
        self._fixture_model(None, 'm2', {a.name: '-10'})
        with self.assertRaises(exceptions.IllegalArgumentError):
            self._fixture_model(None, 'm3', {a.name: 'foo'})

    def test_positive_integer_validation(self):
        a = self._fixture_attr(None, type=AttributeType.Integer,
                               options='positive')

        self._fixture_model(None, 'm1', {a.name: '10'})
        self._fixture_model(None, 'm2', {a.name: 0})
        with self.assertRaises(exceptions.IllegalArgumentError):
            self._fixture_model(None, 'm3', {a.name: -10})

    def test_negative_integer_validation(self):
        a = self._fixture_attr(None, type=AttributeType.Integer,
                               options='negative')

        self._fixture_model(None, 'm1', {a.name: -10})
        self._fixture_model(None, 'm2', {a.name: 0})
        with self.assertRaises(exceptions.IllegalArgumentError):
            self._fixture_model(None, 'm3', {a.name: 10})

    def test_enum_validation(self):
        a = self._fixture_attr(None, type=AttributeType.Enum,
                               options='ert;dfg;cvb')

        self._fixture_model(None, 'm1', {a.name: 'dfg'})
        self._fixture_model(None, 'm2', {a.name: 'ert'})
        with self.assertRaises(exceptions.IllegalArgumentError):
            self._fixture_model(None, 'm3', {a.name: 'ghj'})

    def test_integer_attribute(self):
        a = self._fixture_attr(None, type=AttributeType.Integer)
        m = self._fixture_model(None, 'm', {a.name: 123})
        self.assertEqual(self.storage.attributes.get_attr_values_for_model(m),
                         {a.name: 123})

    def test_float_attribute(self):
        a = self._fixture_attr(None, type=AttributeType.Float)
        m = self._fixture_model(None, 'm', {a.name: 43.21})
        self.assertEqual(self.storage.attributes.get_attr_values_for_model(m),
                         {a.name: 43.21})

    def test_string_attribute(self):
        a = self._fixture_attr(None, type=AttributeType.String)
        m = self._fixture_model(None, 'm', {a.name: 'data'})
        self.assertEqual(self.storage.attributes.get_attr_values_for_model(m),
                         {a.name: 'data'})

    def test_enum_attribute(self):
        a = self._fixture_attr(None, type=AttributeType.Enum,
                               options='qwe;asd;zxc')
        m = self._fixture_model(None, 'm', {a.name: 'asd'})
        self.assertEqual(self.storage.attributes.get_attr_values_for_model(m),
                         {a.name: 'asd'})

    def test_usage_stats(self):
        a = self._fixture_attr(None, nullable=True)
        g = self._fixture_group('g')
        sg = self._fixture_group('sg', g)
        self.assertEqual(self.storage.attributes.usage_stats(a), (0, 0))

        self._fixture_model(None, 'm1', {a.name: 'a'})
        self.assertEqual(self.storage.attributes.usage_stats(a), (1, 1))

        self._fixture_model(g, 'm2', {a.name: 'a'})
        self.assertEqual(self.storage.attributes.usage_stats(a), (2, 2))

        self._fixture_model(sg, 'm3', {})
        self.assertEqual(self.storage.attributes.usage_stats(a), (2, 3))

        self._fixture_model(sg, 'm4', {a.name: 'a'})
        self.assertEqual(self.storage.attributes.usage_stats(a), (3, 4))

    def test_delete(self):
        a = self._fixture_attr(None, nullable=True)
        g = self._fixture_group('g')
        sg = self._fixture_group('sg', g)

        m1 = self._fixture_model(None, 'm1', {a.name: 'a'})
        m2 = self._fixture_model(g, 'm2', {a.name: 'a'})
        m3 = self._fixture_model(sg, 'm3', {a.name: 'a'})
        m4 = self._fixture_model(sg, 'm4', {a.name: 'a'})

        self.storage.attributes.delete_with_values(a)

        self.assertEqual(self.storage.attributes.get_attr_values_for_model(m1), {})
        self.assertEqual(self.storage.attributes.get_attr_values_for_model(m2), {})
        self.assertEqual(self.storage.attributes.get_attr_values_for_model(m3), {})
        self.assertEqual(self.storage.attributes.get_attr_values_for_model(m4), {})
