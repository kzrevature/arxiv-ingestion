import os
from abc import ABC, abstractmethod

import pg8000.native as pg8000


class Connection(ABC):
    """Abstract base class for database connections."""

    @abstractmethod
    def run(self, query_str: str, **kwargs):
        """
        Runs the given query string.
        Keyword arguments can be supplied for parameterized queries.
        """
        pass

    @abstractmethod
    def close(self):
        """Closes the connection."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Pg8000Connection(Connection):
    """
    Implementation of Connection using pg8000.

    User defaults to 'postgres' and port defaults to 5432.
    Password and URL can be provided, else they will be pulled from the environment.
    """

    def __init__(
        self,
        port: int = 5432,
        user: str = "postgres",
        password: str | None = None,
        url: str | None = None,
    ):
        password = password or os.environ["ARXIN_DB_PASS"]
        url = url or os.environ["ARXIN_DB_URL"]
        conn = pg8000.Connection(user=user, password=password, host=url, port=port)
        self.pg8000_conn = conn

    def run(self, query_str: str, **kwargs):
        return self.pg8000_conn.run(query_str, **kwargs)

    def close(self):
        self.pg8000_conn.close()
