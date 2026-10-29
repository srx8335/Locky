"""Create the Pusher client from environment variables or local app config."""

import os

import pusher
from gluon.contrib.appconfig import AppConfig


configuration = AppConfig(reload=True)


def _setting(environment_name, config_name):
    value = os.getenv(environment_name)
    if value:
        return value

    return configuration.get(config_name)


app_id = _setting("LOCKY_PUSHER_APP_ID", "pusher.app_id")
key = _setting("LOCKY_PUSHER_KEY", "pusher.key")
secret = _setting("LOCKY_PUSHER_SECRET", "pusher.secret")
cluster = _setting("LOCKY_PUSHER_CLUSTER", "pusher.cluster") or "eu"

if not app_id or not key or not secret:
    raise RuntimeError(
        "Pusher configuration is incomplete. Set LOCKY_PUSHER_APP_ID, "
        "LOCKY_PUSHER_KEY and LOCKY_PUSHER_SECRET."
    )

pusher_client = pusher.Pusher(
    app_id=str(app_id),
    key=str(key),
    secret=str(secret),
    cluster=str(cluster),
    ssl=True,
)
