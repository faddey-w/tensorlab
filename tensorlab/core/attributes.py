from .base import StorageBase

if False:
    import typing


class Attribute:
    """
    Attributes are the main thing by which models and runs can be
    distinguished. Groups define sets of attributes
    for models and runs and they have to provide values for these
    attributes. Then the user's application should use attribute values
    provided by framework to determine how to do everything.

    Subgroups can override attributes defined by parent groups.

    Attribute fields:
        * name: attribute name given by user, unique per group
        * type: defines type of the attribute's values;
                supported types: integer, float, string, enumeration.
                :see tensorlab.core.attributeoptions.AttributeType
        * options: string that defines type-specific options or
                constraints for values.
                Supported options:
                    - integers: "positive", "negative" or empty string
                    - enumerations: semicolon-separated list of choices
                    - floats: no options, should be an empty string
                    - strings: no options, should be an empty string
                :see tensorlab.core.attributeoptions.AttributeType.validate_options
        * default: defines a default value for the options. If attribute has a
                default value, it is not required to provide a value each time.
        * nullable: boolean denoting whether the attribute
                can do not have a value. Ignored if default value is defined.
        * runtime: boolean denoting whether this attribute must be provided
                different for each run, or once at model build time.

    Attribute is denoted as "required" if and only if it
    is not nullable and has no default value.
    """

    def __init__(self, key=None, storage=None, *,
                 name, type, runtime, options='',
                 default=None, nullable=False):
        """
        :type storage: AttributeStorage
        :type name: str
        :type type: tensorlab.core.attributeoptions.AttributeType
        :type runtime: bool
        :type options: str
        :type default: <not specified>
        :type nullable: bool
        """
        self.key = key
        self.storage = storage  # type: AttributeStorage
        self.name = name
        self.runtime = runtime
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
        return 'Attribute(name={!r}, type={}, runtime={}{}{}{})'\
            .format(
                self.name, self.type, self.runtime,
                ', options={!r}'.format(self.options) if self.options else '',
                ', default={!r}'.format(self.default) if self.default is not None else '',
                ', nullable=True' if self.nullable else '',
            )

    def __eq__(self, other):
        if not isinstance(other, Attribute):
            return False
        return self.get_fields() == other.get_fields()

    def get_fields(self):
        return {
            'name': self.name,
            'type': self.type,
            'runtime': self.runtime,
            'options': self.options,
            'default': self.default,
            'nullable': self.nullable,
        }


class AttributeStorage(StorageBase):
    """
    Attribute integrity rules:
        * Any model/run has to define a value for attribute,
          unless the attribute either is nullable or has a default value
        * Each action on the Storage after which the previous rule
          will be violated must be blocked.
            - You cannot define required attribute if you have at least
              one object that will have to define a value for it.
            - You cannot turn nullable attribute into non-nullable one
              if you have at least one object that has not defined
              a value for it.
            - You cannot create an object without providing values for
              all required attributes.
            - You can add required attributes if you don't have any objects
              that have to define values for it.
        * Attributes cannot change their name, type and runtime flag.
        * Attributes of enumeration type cannot remove choices if there is
          at least one value of this choice.
        * When the attribute is deleted, all its values are also dropped.
    """

    def create(self, attribute, group):
        """
        Creates new attribute.
        This operation "defines" attribute on given group.

        This procedure must not violate the integrity rules.
        This operation changes the Python object of Attribute in-place.

        :type attribute: Attribute
        :type group: typing.Optional[tensorboard.core.groups.Group]
        :return: None
        """
        raise NotImplementedError

    def update(self, attribute):
        """
        Updates existing attribute.

        This procedure must not violate the integrity rules.
        This operation changes the Python object of Attribute in-place.

        :type attribute: Attribute
        :return: None
        """
        raise NotImplementedError

    def get_defining_group(self, attribute):
        """
        :returns group that defines given attribute
        :type attribute: Attribute
        :rtype: tensorboard.core.groups.Group
        """
        raise NotImplementedError

    def get_attr_values_for_model(self, model):
        """
        :returns values of all attributes for given model, including defaults
        :type model: tensorboard.core.models.Model
        :rtype: dict
        """
        raise NotImplementedError

    def get_attr_values_for_run(self, run):
        """
        :returns values of all attributes for given run, including defaults
        :type run: tensorboard.core.runs.Run
        :rtype: dict
        """
        raise NotImplementedError

    def list(self, group):
        """
        Lists all attributes that the given group defines.
        :type group: typing.Optional[tensorboard.core.groups.Group]
        :rtype: typing.List[Attribute]
        """
        raise NotImplementedError

    def list_effective(self, group):
        """
        Lists all attributes that are visible on the given group -
        all attributes that models/runs will use.
        :type group: typing.Optional[tensorboard.core.groups.Group]
        :rtype: typing.List[Attribute]
        """
        raise NotImplementedError

    def usage_stats(self, attribute):
        """
        :type attribute: Attribute
        :rtype: typing.Tuple[int]
        :return:
            item #0: number of entities that define value for this attribute
            item #1: number of entities that MAY define a value
        Note that if the attribute is non-nullable, both numbers are the same.
        """
        raise NotImplementedError

    def delete_with_values(self, attribute):
        """
        Deletes the attribute and all values for it.
        :type attribute: Attribute
        :return: None
        """
        raise NotImplementedError
