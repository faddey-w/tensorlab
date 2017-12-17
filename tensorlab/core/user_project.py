

class UserProject:

    def build(self, attributes, model_data, stream):
        """
        :type attributes: typing.Dict[str, Any]
        :type model_data: str
        :type stream: typing.TextIO
        """
        raise NotImplementedError

    def run(self, attributes, model_data, run_data, stream):
        """
        :type attributes: typing.Dict[str, Any]
        :type model_data: str
        :type run_data: str
        :type stream: typing.TextIO
        """
        raise NotImplementedError
