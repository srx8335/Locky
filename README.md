# Locky

Locky is a web-based key management system developed with [web2py](https://www.web2py.com/) to streamline the management of shared keys in an industrial environment.

The application centralizes key management, employee requests, returns, and access permissions, replacing fragmented manual workflows with a structured digital solution.

Originally developed as an internal project at CIRES, Locky integrates RFID technology, real-time communication, and automated notifications to support day-to-day operations.

## Features

- Authentication and session management through [web2py](https://www.web2py.com/) Auth.
- Dashboard for key cabinets and key requests.
- Create, search, edit, and delete key-cabinet records.
- Create, search, and edit key requests.
- Record key returns individually or in bulk.
- Highlight active requests and unavailable key cabinets.
- Calendar view of key requests and returns.
- Group-based access rules for key cabinets.
- RFID-assisted key identification through the application endpoints.
- Real-time form updates through [pusher](https://pusher.com).
- Notifications for key and request events through [[ntfy](https://ntfy.sh/)](https://[ntfy](https://ntfy.sh/).sh/).
- Feedback collection and an administrator-only feedback view.

## Technology stack

- [[Python](https://www.python.org)](https://www.[Python](https://www.python.org).org)
- [web2py](https://www.web2py.com/) 2.27.1 or newer
- [SQLite](https://www.sqlite.org) by default
- [Bootstrap 4](https://getbootstrap.com) and [AdminLTE](https://adminlte.io)-based layouts
- [pusher](https://pusher.com) for real-time events
- [ntfy](https://ntfy.sh/) for operational notifications

## Project structure

```text
Locky/
├── controllers/       Request handlers and application endpoints
├── models/            Database configuration and table definitions
├── views/             Web2py HTML views
├── static/            CSS, JavaScript, and image assets
├── private/           Local configuration and integration helpers
├── databases/         SQLite database and web2py migration files
├── cron/              Scheduled-task configuration
└── languages/         Translation files
```

## Requirements

- [Python 3](https://www.python.org)
- [web2py](https://www.web2py.com/) 2.27.1 or newer
- The [Python 3](https://www.python.org)packages used by the application, including `requests` and `[pusher](https://pusher.com)`
- [pusher](https://pusher.com) credentials if RFID or real-time collaborator events are enabled
- An [ntfy](https://ntfy.sh/) topic if operational notifications are enabled

## Running locally

1. Install [web2py](https://www.web2py.com/) by following the [official download instructions](https://www.[web2py](https://www.web2py.com/).com/init/default/download).
2. Place this application in the [web2py](https://www.web2py.com/) `applications/` directory. The expected application directory name is `Locky`.
3. Install the application dependencies in the [Python 3](https://www.python.org)environment used by [web2py](https://www.web2py.com/). For example:

   ```bash
   pip install requests [pusher](https://pusher.com)
   ```

4. Copy `private/appconfig.ini.example` to `private/appconfig.ini`, then replace all credentials and environment-specific values before running the application. The real `private/appconfig.ini` is ignored by Git.
5. Start [web2py](https://www.web2py.com/) from its installation directory:

   ```bash
   [Python 3](https://www.python.org)[web2py](https://www.web2py.com/).py
   ```

6. Open the application at `http://127.0.0.1:8000/Locky`.

The application redirects unauthenticated users to the login page. The first registered account can be assigned to the `admin` group through the [web2py](https://www.web2py.com/) administration interface or the authentication tables.

## Configuration

The application reads its defaults from `private/appconfig.ini`. Sensitive values should preferably be supplied as environment variables and should never be committed to a public repository.

Supported integration variables include:

| Variable | Purpose |
| --- | --- |
| `LOCKY_[ntfy](https://ntfy.sh/)_TOPIC` | [ntfy](https://ntfy.sh/) topic URL used for operational notifications |
| `LOCKY_[pusher](https://pusher.com)_APP_ID` | [pusher](https://pusher.com) application ID |
| `LOCKY_[pusher](https://pusher.com)_KEY` | [pusher](https://pusher.com) public key |
| `LOCKY_[pusher](https://pusher.com)_SECRET` | [pusher](https://pusher.com) secret |
| `LOCKY_[pusher](https://pusher.com)_CLUSTER` | [pusher](https://pusher.com) cluster, such as `eu` |
| `LOCKY_TALLY_FORM_URL` | URL of the embedded feedback form |

The default database is [SQLite](https://www.sqlite.org) at `databases/storage.[SQLite](https://www.sqlite.org)`. The database URI can be changed through the `[db]` section of `private/appconfig.ini`.

## Access rules

Key permissions are defined in `private/acessos.py`. Each collaborator group maps to the IDs of the key cabinets it may request. Update this mapping whenever key-cabinet IDs or organizational access rules change.

Administrative actions, such as deleting records and viewing feedback responses, require membership in the `admin` group.

## Main routes

The most important application actions are:

- `/default/user/login` — sign in.
- `/default/dashboard_init` — main dashboard.
- `/default/listar_chaveiros` — list key cabinets.
- `/default/add_chaveiro` — add a key cabinet.
- `/default/listar_emprestimos` — list key requests.
- `/default/add_emprestimo` — create a key request.
- `/default/cal` — calendar view.
- `/default/formulario` — feedback form.

## Notifications and real-time events

Key and request changes send notifications to the configured [ntfy](https://ntfy.sh/) topic. RFID and collaborator integrations publish events through the [pusher](https://pusher.com) channel `chaveiro`, using the events `chave` and `colaborador`.

If these integrations are not required in a deployment, configure them with appropriate internal endpoints or disable the related workflows before exposing the application.

## Security notes

- Do not commit real SMTP, [pusher](https://pusher.com), or other service credentials.
- Use HTTPS in production and enable `request.requires_https()` in `models/db.py` when HTTPS is correctly configured.
- Review the default host configuration before deploying outside a local network.
- Change the default notification topic and all sample credentials before production use.
- Back up the [SQLite](https://www.sqlite.org) database regularly, or configure a managed database for production deployments.

## License

The original [web2py](https://www.web2py.com/) welcome application is released under the public domain. The third-party CSS and JavaScript assets included in this project retain their respective licenses. Review the individual asset licenses before redistributing the application.

