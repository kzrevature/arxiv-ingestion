import os

from pg8000.native import Connection


# opens a connection to the postgres server
# user is hardcoded to the default 'postgres'
# password and url come from environ
def create_connection(
    port: int = 5432,
    user: str = "postgres",
    password: str | None = None,
    url: str | None = None,
) -> Connection:
    password = password or os.environ["ARXIN_DB_PASS"]
    url = url or os.environ["ARXIN_DB_URL"]
    conn = Connection(user=user, password=password, host=url, port=port)
    return conn
