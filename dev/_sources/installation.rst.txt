Installation
============

Requirements
------------

- Python 3.12+
- uv (package manager)

Clone the Repository
--------------------

.. code-block:: bash

   git clone https://github.com/yourusername/talent-acquisition-agent.git
   cd talent-acquisition-agent

Install Dependencies
--------------------

.. code-block:: bash

   uv sync

This will install all dependencies defined in ``pyproject.toml``:

- ``aiohttp`` - Async HTTP requests
- ``beautifulsoup4`` - HTML parsing
- ``fastapi`` - HTTP API server
- ``pydantic-settings`` - Configuration management
- ``twilio`` - SMS notifications

Verify Installation
-------------------

.. code-block:: bash

   uv run python --version
   uv run .\src\main.py

You should see output like:

::

   2026-04-25 17:15:12 | INFO | job_agent | Job Agent v1.1.0 starting

Windows Installer (.exe)
------------------------

For users on Windows, a standalone installer is provided that registers the
services automatically and provides an uninstaller:

1. Download ``JobAgentInstaller.exe`` from the latest GitHub Release.
2. Double-click the installer and follow the wizard instructions (Administrator
   privileges required).
3. The services (API and Search) will be installed as Windows Services.
4. The Web UI will be accessible at ``http://localhost:8080/ui``.

Uninstallation
~~~~~~~~~~~~~~

To uninstall the application:
1. Go to **Settings > Apps > Installed Apps**.
2. Find **Talent Acquisition Agent** and select **Uninstall**.
3. The uninstaller will stop and remove the Windows services before deleting files.


Development Setup
-----------------

To contribute to this project, please set up the development environment:

1. Install development dependencies:

   .. code-block:: bash

      uv sync

2. Install pre-commit hooks:

   .. code-block:: bash

      uv run pre-commit install

3. Run checks manually:

   .. code-block:: bash

      uv run pre-commit run --all-files

The pre-commit configuration ensures code quality remains intact.
