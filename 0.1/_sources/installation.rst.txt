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
