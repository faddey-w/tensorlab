

class TensorLabStorage:

    @property
    def groups(self):
        """
        :rtype: tensorlab.core.groups.GroupsStorage
        """
        return self._get_impl().groups

    @property
    def models(self):
        """
        :rtype: tensorlab.core.models.ModelsStorage
        """
        return self._get_impl().models

    @property
    def runs(self):
        """
        :rtype: tensorlab.core.runs.RunsStorage
        """
        return self._get_impl().runs

    @property
    def attributes(self):
        """
        :rtype: tensorlab.core.attributes.AttributeStorage
        """
        return self._get_impl().attributes

    def _get_impl(self):
        raise NotImplementedError
