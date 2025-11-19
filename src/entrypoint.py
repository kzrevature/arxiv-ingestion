import json
import os
import pg8000.native


def handler(event, context):
    db_user = "postgres"
    db_password = os.environ["ARXIN_DB_PASS"]
    db_url = os.environ["ARXIN_DB_URL"]
    conn = pg8000.native.Connection(
        db_user,
        password=db_password,
        host=db_url,
    )

    conn.close()
    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
