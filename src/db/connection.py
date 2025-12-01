import os

from pg8000.native import Connection as Pg8000Connection


class Connection:
    """
    Thin wrapper around pg8000 Connection.

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
        conn = Pg8000Connection(user=user, password=password, host=url, port=port)
        self.pg8000_conn = conn

    def run(self, query_str: str, **kwargs):
        """
        Runs the given query string.
        Keyword arguments can be supplied for parameterized queries.
        """
        return self.pg8000_conn.run(query_str, **kwargs)

    def close(self):
        """Closes the underlying pg8000 connection."""
        self.pg8000_conn.close()
