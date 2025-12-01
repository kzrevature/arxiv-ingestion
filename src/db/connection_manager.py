from db.connection import Connection


class ConnectionManager:
    """
    Manager class which abstracts connections to a database.

    Currently implemented as a singleton Connection instance.
    """

    _connection = None
    configuration = {}

    @classmethod
    def configure(cls, **kwargs):
        """Configures the connection parameters and resets any existing connection."""
        cls.configuration = kwargs

    @classmethod
    def get_connection(cls):
        """Returns a Connection instance."""
        if cls._connection is None:
            cls._connection = Connection(**cls.configuration)
        return cls._connection
