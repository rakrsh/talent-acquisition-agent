12-Factor App Compliance
========================

Job Agent follows the `12-Factor <https://12factor.net/>`_ methodology for cloud-native application development.

I. Codebase
-----------

**Principle**: One codebase tracked in revision control, many deployments.

- Single git repository
- All configuration via environment variables
- Same code runs in development and production

.. code-block:: bash

   git clone https://github.com/yourusername/talent-acquisition-agent.git

II. Dependencies
-----------------

**Principle**: Explicitly declare and isolate dependencies.

- All dependencies declared in ``pyproject.toml``
- No implicit reliance on system-wide packages
- Use ``uv sync`` to install

.. code-block:: toml

   [project]
   dependencies = [
       "aiohttp",
       "fastapi",
       "pydantic-settings",
       "twilio",
   ]

III. Config
----------

**Principle**: Store config in the environment.

- All configuration via environment variables
- No hardcoded values in source code
- Template provided in ``.env.example``

.. code-block:: bash

   cp .env.example .env
   # Edit .env with your values

IV. Backing Services
--------------------

**Principle**: Treat backing services as attached resources.

- Remote OK API (job search)
- Twilio (SMS notifications)
- SMTP (email notifications)
- Local JSON file (application storage)

V. Build, Release, Run
---------------------

**Principle**: Strictly separate build and run stages.

- ``uv sync`` - Build/install
- ``uv run`` - Build and run in one step

.. code-block:: bash

   uv run .\src\main.py

VI. Processes
-------------

**Principle**: Execute the app as one or more stateless processes.

- No in-memory state between runs
- Data stored in external service (JSON file)
- Async/await for concurrency

VII. Port Binding
-----------------

**Principle**: Export HTTP as a service by binding to a port.

- FastAPI server binds to configurable port
- Default: ``http://localhost:8080``

.. code-block:: bash

   uv run .\src\server.py

VIII. Concurrency
-----------------

**Principle**: Scale out via the process model.

- Use ``asyncio.gather`` for parallel job searches
- Multiple job sources searched simultaneously

.. code-block:: python

   results = await asyncio.gather(
       self._search_remote_ok(),
       self._search_indeed(),
       return_exceptions=True
   )

IX. Disposability
-----------------

**Principle**: Maximize robustness with fast startup and graceful shutdown.

- Fast startup (< 1 second)
- No complex initialization
- Clean async shutdown

X. Dev/Prod Parity
------------------

**Principle**: Keep development, staging, and production as similar as possible.

- Same Python environment (uv)
- Same dependency resolution
- Same configuration mechanism

XI. Logs
--------

**Principle**: Treat logs as event streams.

- Structured logging via ``config.py``
- JSON format in production
- Human-readable in development

.. code-block:: python

   from config import logger
   logger.info("Job search complete!")

XII. Admin Processes
--------------------

**Principle**: Run admin/management tasks as one-off processes.

- Separate modules for different concerns
- Job search, notifications, tracking as separate components

Summary Table
-------------

.. list-table::
   :header-rows: 1

   * - Factor
     - Implementation
   * - I. Codebase
     - Single git repo
   * - II. Dependencies
     - ``pyproject.toml``
   * - III. Config
     - Environment variables
   * - IV. Backing Services
     - External APIs
   * - V. Build/Release/Run
     - ``uv run``
   * - VI. Processes
     - Stateless async
   * - VII. Port Binding
     - FastAPI server
   * - VIII. Concurrency
     - ``asyncio.gather``
   * - IX. Disposability
     - Fast startup
   * - X. Dev/Prod Parity
     - Same environment
   * - XI. Logs
     - Structured logging
   * - XII. Admin Processes
     - Separate modules