from .base import StorageBase

if False:
    import typing


class Attribute:
    """
    Attributes are the main thing by which models, instances and runs
    can be distinguished. Group, model or instance defines a set of attributes
    for models, instances and runs and they have to provide values for these
    attributes. Then the user's application should use attribute values
    provided by framework to determine how to do everything.

    Groups can define attributes for models, instances and runs which are
    contained within this group.

    Models can define attributes for instances and runs which are
    contained within this model and have to provide values for attributes
    defined by group which the model belongs to.

    Instances can define attributes for runs which are contained within this
    run and have to provide values for attributes defined by group and model
    which the instance belongs to.

    Runs cannot define attributes and have to provide values for attributes
    define by entities of higher level (group, model and instance).

    Attribute fields:
        * name: attribute name given by user, unique per group
        * def_target: what kind of entity (group, model or instance)
                defines the attribute.
                :see tensorlab.core.attributeoptions.AttributeTarget
        * val_target: what kind of entity (model, instance of run)
                must provide a value for this attribute.
                :see tensorlab.core.attributeoptions.AttributeTarget
        * type: defines type of the attribute's values;
                supported types: integer, float, string, enumeration.
                :see tensorlab.core.attributeoptions.AttributeType
        * options: string that defines type-specific options or
                constraints for values.
                Supported options:
                    - integers: "positive", "negative" of empty string
                    - enumerations: semicolon-separated list of choices
                    - floats: no options, should be an empty string
                    - strings: no options, should be an empty string
                :see tensorlab.core.attributeoptions.AttributeType.validate_options
        * default: defines a default value for the options. If attribute has a
                default value, it is not required to provide a value each time.
        * nullable: boolean denoting whether the attribute
                can to not have a value.

    Attribute is denoted as "required" if and only if it
    is not nullable and has no default value.

    If we say "group attribute for runs", it means that
    def_target is "group" and val_target is "run", and so on.

    If we say "model defines the attribute", it means that
    def_target is "model", and all instances or runs of this model
    have to define a value for this attribute.
    """

    def __init__(self, key=None, storage=None, *,
                 name, def_target, val_target, type, options='',
                 default=None, nullable=False):
        """
        :type storage: AttributeStorage
        :type name: str
        :type def_target: tensorlab.core.attributeoptions.AttributeTarget
        :type val_target: tensorlab.core.attributeoptions.AttributeTarget
        :type type: tensorlab.core.attributeoptions.AttributeType
        :type options: str
        :type default: <not specified>
        :type nullable: bool
        """
        self.key = key
        self.storage = storage  # type: AttributeStorage
        self.name = name
        self.def_target = def_target
        self.val_target = val_target
        self.type = type
        self.options = options
        self.default = default
        self.nullable = nullable

    def derive(self, **changes):
        kwargs = self.get_fields()
        kwargs['storage'] = self.storage
        kwargs.update(changes)
        return Attribute(**kwargs)

    def __repr__(self):
        return 'Attribute(name={!r}, def_target={}, ' \
               'val_target={}, type={}{}{}{})'\
            .format(
                self.name, self.def_target, self.val_target, self.type,
                ', options={!r}'.format(self.options) if self.options else '',
                ', default={!r}'.format
                    (self.default) if self.default is not None else '',
                ', nullable=True' if self.nullable else '',
            )

    def __eq__(self, other):
        if not isinstance(other, Attribute):
            return False
        return self.get_fields() == other.get_fields()

    def get_fields(self):
        return {
            'name': self.name,
            'def_target': self.def_target,
            'val_target': self.val_target,
            'type': self.type,
            'options': self.options,
            'default': self.default,
            'nullable': self.nullable,
        }


class AttributeStorage(StorageBase):
    """
    Attribute integrity rules:
        * Any object has to define a value for any attribute that is targeted
          to it, unless the attribute either is nullable or has a default value
        * Each action on the Storage after which the previous rule is violated
          must be blocked, but the previous actions cannot be cancelled.
            - You cannot define required attribute if you have at least
              one object the has to define a value for it.
            - You cannot turn nullable attribute into non-nullable one
              if you have at least one object that has not defined
              a value for it.
            - You cannot create an object without providing values for
              all required attributes.
            - You can add required attributes if you don't have any objects
              that have to define values for it.
        * Attributes cannot change their type, def_target and val_target.
        * Attributes of enumeration type cannot remove choices if there is
          at least one value of this choice.
        * When the attribute is deleted, all its values are also dropped.
    """

    def save(self, attribute, entity):
        """
        Creates new attribute or updates existing one.
        This operation "defines" attribute on level of the given entity,
        so some nested entities will have to provide values for this attribute.

        This procedure must not violate the integrity rules.
        This operation changes the Python object of Attribute in-place.

        :type attribute: Attribute
        :type entity: typing.Any[Group, Model, Instance]
        :return: None
        """
        method = self._get_method(entity, 'create', run_allowed=False)
        return method(attribute, entity)

    def save_for_group(self, attribute, group):
        """
        Implementation of saving procedure for group attributes.
        See method `create`.
        :type attribute: Attribute
        :type group: Group
        :return: None
        """
        raise NotImplementedError

    def save_for_model(self, attribute, model):
        """
        Implementation of saving procedure for model attributes.
        See method `create`.
        :type attribute: Attribute
        :type model: Model
        :return: None
        """
        raise NotImplementedError

    def save_for_instance(self, attribute, instance):
        """
        Implementation of saving procedure for instance attributes.
        See method `create`.
        :type attribute: Attribute
        :type instance: Instance
        :return: None
        """
        raise NotImplementedError

    def get_defining_entity(self, attribute):
        """
        :returns entity that defines given attribute
        :type attribute: Attribute
        :rtype: typing.Any[Group, Model, Instance]"""
        raise NotImplementedError

    def list(self, entity):
        """
        Lists all attributes that the given entity defines.
        :type entity: typing.Any[Group, Model, Instance]
        :rtype: typing.List[Attribute]
        """
        method = self._get_method(entity, 'list', run_allowed=False)
        return method(entity)

    def list_for_group(self, group):
        """
        Lists all attributes that the given group defines.
        :type group: Group
        :rtype: typing.List[Attribute]
        """
        raise NotImplementedError

    def list_for_model(self, model):
        """
        Lists all attributes that the given model defines.
        :type model: Model
        :rtype: typing.List[Attribute]
        """
        raise NotImplementedError

    def list_for_instance(self, instance):
        """
        Lists all attributes that the given instance defines.
        :type instance: Instance
        :rtype: typing.List[Attribute]
        """
        raise NotImplementedError

    def delete_with_values(self, attribute):
        """
        Deletes the attribute and all values for it.
        :type attribute: Attribute
        :return: None
        """
        raise NotImplementedError

    def _get_method(self, entity, action,
                    group_allowed=True, run_allowed=True):
        from .groups import Group
        from .models import Model
        from .instances import ModelInstance
        from .runs import Run
        if group_allowed and isinstance(entity, Group):
            name = action + '_for_group'
        elif isinstance(entity, Model):
            name = action + '_for_model'
        elif isinstance(entity, ModelInstance):
            name = action + '_for_instance'
        elif run_allowed and isinstance(entity, Run):
            name = action + '_for_run'
        else:
            raise TypeError(entity)
        return getattr(self, name)
