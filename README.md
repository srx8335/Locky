# Locky

**A web-based key management system integrating RFID technology, real-time communication, and automated notifications.**

Locky is a web application developed with [web2py](https://www.web2py.com/) to streamline the management of shared keys in an industrial environment.

The application centralizes key cabinet management, employee requests, returns, and access permissions, replacing fragmented manual workflows with a structured digital solution.

Originally developed as an internal project at [**CIRES**](https://www.cires.pt), Locky combines traditional web application functionality with physical RFID hardware, real-time updates, and automated notifications to support everyday operations.

## Features

### Key Management

- Create, search, edit, and delete key cabinet records.
- Monitor key availability and active requests.
- Manage individual and bulk key returns.
- View key requests and returns through an integrated calendar.

### Authentication & Access Control

- User authentication and session management through web2py Auth.
- Group-based permissions controlling access to specific key cabinets.
- Administrative privileges for restricted operations.
- Protected application routes requiring authentication.

### RFID Integration

- RFID-assisted identification through application endpoints.
- Integration with Electric Imp-based hardware.
- Communication between physical RFID components and the web application.

### Real-Time Communication & Notifications

- Real-time interface updates through [Pusher](https://pusher.com/).
- Automated operational notifications through [ntfy](https://ntfy.sh/).
- Event-driven updates for key and collaborator interactions.

### Additional Functionality

- Centralized dashboard for key cabinets and requests.
- Feedback collection through an embedded form.
- Administrator-only feedback management.

## Technology Stack

- [Python](https://www.python.org/)
- [web2py](https://www.web2py.com/) 2.27.1
- [SQLite](https://www.sqlite.org/)
- HTML, CSS and JavaScript
- [Bootstrap 4](https://getbootstrap.com/docs/4.6/) and [AdminLTE](https://adminlte.io/)
- [Pusher](https://pusher.com/) for real-time events
- [ntfy](https://ntfy.sh/) for operational notifications
- [Electric Imp](https://www.electricimp.com/) for RFID hardware integration

The application was developed using web2py 2.27.1. Compatibility with other framework versions has not been fully verified.

## Project Structure

```text
Locky/
├── controllers/       Application routes, request handlers and endpoints
├── models/            Database configuration and table definitions
├── views/             HTML templates and application interfaces
├── static/            CSS, JavaScript, images and other assets
├── private/           Local configuration and integration helpers
├── databases/         SQLite database and migration files
└── languages/         Translation files
```

The application follows the Model-View-Controller (MVC) architecture provided by web2py.

## Requirements

- Python 3
- web2py 2.27.1 (tested version)
- Required Python packages, including `requests` and `pusher`
- Pusher credentials for enabled real-time integrations
- An ntfy topic for enabled notification workflows

Certain hardware-dependent features require access to the corresponding RFID infrastructure.

## Running Locally

### 1. Install web2py

Download and install web2py using the [official instructions](https://www.web2py.com/init/default/download).

### 2. Install Locky

Place the project inside the web2py `applications/` directory.

The expected directory structure is:

```text
web2py/
└── applications/
    └── Locky/
```

### 3. Install Dependencies

Install the required Python packages in the environment used by web2py. Run this from the directory containing `requirements.txt`:

```bash
python3 -m pip install -r requirements.txt
```

Additional dependencies may be required depending on the integrations enabled in your deployment.

### 4. Configure the Application

Copy the example configuration file:

```bash
cp private/appconfig.ini.example private/appconfig.ini
```

Edit `private/appconfig.ini` and replace the example values with the appropriate local configuration.

**Important:** Never commit real credentials or sensitive configuration files to version control.

### 5. Start web2py

From the web2py installation directory, execute:

```bash
python3 web2py.py
```

### 6. Access Locky

Open the application in your browser:

```text
http://127.0.0.1:8000/Locky
```

Unauthenticated users are redirected to the login page.

### 7. Administrator Access

Administrative functionality requires membership in the `admin` authentication group.

An authorized account can be assigned to this group through the web2py administration interface or the corresponding authentication tables.

## Configuration

Locky reads its application configuration from:

```text
private/appconfig.ini
```

The configuration file contains database settings and integration-specific values.

Where supported by the application, sensitive configuration values can be supplied through environment variables.

### Integration Environment Variables

| Variable               | Description                  |
| ---------------------- | ---------------------------- |
| `LOCKY_NTFY_TOPIC`     | Notification topic URL       |
| `LOCKY_PUSHER_APP_ID`  | Pusher application ID        |
| `LOCKY_PUSHER_KEY`     | Pusher public key            |
| `LOCKY_PUSHER_SECRET`  | Pusher application secret    |
| `LOCKY_PUSHER_CLUSTER` | Pusher cluster, such as `eu` |
| `LOCKY_TALLY_FORM_URL` | Embedded feedback form URL   |

### Database

By default, Locky uses SQLite:

```text
databases/storage.sqlite
```

The database connection can be configured through the `[db]` section of `private/appconfig.ini`.

Database files containing real application records should not be included in public repositories.

## Access Control

Access to key cabinets is managed through group-based permissions.

The permission mapping is defined in:

```text
private/acessos.py
```

Each collaborator group is associated with the identifiers of the key cabinets it is authorized to request.

This mapping must be updated when cabinet identifiers or organizational access requirements change.

Administrative operations, including record deletion and access to feedback responses, require membership in the `admin` group.

**Current limitation:** Cabinet permissions rely on an application-level mapping of group identifiers to cabinet identifiers rather than a fully configurable permissions interface.

## Main Application Routes

The following routes represent the main application actions, relative to the `/Locky` application path.

| Route                         | Description          |
| ----------------------------- | -------------------- |
| `/default/user/login`         | User authentication  |
| `/default/dashboard_init`     | Main dashboard       |
| `/default/listar_chaveiros`   | Key cabinet listing  |
| `/default/add_chaveiro`       | Create a key cabinet |
| `/default/listar_emprestimos` | Key request listing  |
| `/default/add_emprestimo`     | Create a key request |
| `/default/cal`                | Calendar             |
| `/default/formulario`         | Feedback form        |

Some actions require authentication or specific access permissions.

## RFID & Real-Time Integration

Locky integrates RFID hardware into its key management workflows.

The repository also includes example endpoint requests for [Bruno](https://www.usebruno.com/downloads), allowing developers to simulate selected RFID interactions without the physical IoT hardware. Use the example requests against a local test installation, not a production deployment.

The RFID subsystem communicates with the application through dedicated endpoints, allowing physical identification events to interact with the digital management system.

Real-time communication is handled through Pusher.

### Pusher Events

**Channel:**

```text
chaveiro
```

**Events:**

| Event         | Purpose                                        |
| ------------- | ---------------------------------------------- |
| `chave`       | Key-related identification or updates          |
| `colaborador` | Collaborator-related identification or updates |

These events support communication between the RFID integration and the application interface.

### Notifications

Locky uses ntfy to send operational notifications related to key and request events.

Notifications are delivered to the configured topic and can be consumed by compatible ntfy clients.

Deployments that do not use these integrations should disable the associated workflows or configure them for the intended environment.

## Development & Contributions

I designed and developed Locky during my time at CIRES.

The project originated from an internal operational requirement and evolved into a web-based solution integrating application software with physical identification hardware.

My main contributions included:

- Designing and implementing the application database structure.
- Developing backend logic and application endpoints using Python and web2py.
- Building frontend interfaces using HTML, CSS, JavaScript, and Bootstrap-based layouts.
- Implementing authentication-related workflows and group-based access rules.
- Developing key management, request tracking, and return management functionality.
- Integrating RFID identification with the web application.
- Implementing real-time communication through Pusher.
- Integrating automated notifications through ntfy.
- Testing, troubleshooting, and refining application functionality.

The RFID integration involved adapting and extending existing Electric Imp code to connect the physical hardware with the application.

The project provided practical experience in full-stack development, external service integration, access control, and communication between software and hardware systems.

## Security Considerations

Before deploying the application to a publicly accessible server, the following precautions should be taken:

- Never expose real SMTP, Pusher, or other integration credentials.
- Use HTTPS for all production traffic.
- Configure HTTPS handling appropriately for the hosting environment.
- Review authentication, authorization, and session security.
- Validate permissions on server-side endpoints, including RFID-related actions.
- Restrict access to sensitive application routes.
- Review allowed hosts and deployment-specific settings.
- Replace example credentials and notification topics.
- Protect database files and maintain regular backups.
- Avoid exposing personally identifiable information or internal organizational records.

**Deployment notice:** The publicly available source code should not be assumed to be production-ready without additional security review, configuration, and environment-specific testing.

## Known Limitations

- RFID functionality depends on compatible hardware and its associated integrations.
- Certain workflows require configured external services.
- Access permissions use a manually maintained group-to-cabinet mapping.
- The default SQLite configuration is intended for straightforward deployments and local development.
- Compatibility with different versions of web2py has not been fully verified.
- Hardware-dependent functionality cannot be fully reproduced without the corresponding equipment.

## License & Third-Party Components

Locky incorporates web2py and third-party frontend libraries.

The original web2py welcome application is distributed under the public domain. Third-party CSS, JavaScript, and other bundled assets retain their respective licenses.

Review the applicable licenses before redistributing or modifying third-party components.

Permission to publish project source code does not automatically grant permission to redistribute confidential organizational information, proprietary third-party assets, or restricted credentials.

No separate license for the original Locky application code is declared in this README.

---

*Originally created as an internal software project at CIRES.*
