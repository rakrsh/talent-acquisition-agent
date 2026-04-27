Usage
=====

CLI Mode
--------

Run the job search agent from the command line:

.. code-block:: bash

   uv run .\src\main.py

Output:

::

   2026-04-25 17:15:12 | INFO | job_agent | Job Agent v1.1.0 starting | Mode: development
   2026-04-25 17:15:12 | INFO | job_agent | Current applications: 0 total | Applied: 0 | Pending: 0
   2026-04-25 17:15:12 | INFO | job_agent | Searching for jobs...
   2026-04-25 17:15:19 | INFO | job_agent | Found 80 jobs
   2026-04-25 17:15:19 | INFO | job_agent | New jobs (not yet applied): 80
   2026-04-25 17:15:19 | INFO | job_agent | Sending notifications...
   2026-04-25 17:15:19 | INFO | job_agent | Job search complete!

HTTP Server Mode
----------------

Run as a REST API server:

.. code-block:: bash

   uv run .\src\server.py

The server will start on ``http://localhost:8080`` by default.

API Endpoints
^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Endpoint
     - Method
     - Description
   * - ``/``
     - GET
     - Health check
   * - ``/health``
     - GET
     - Detailed health status
   * - ``/jobs``
     - GET
     - Search and return jobs
   * - ``/applications``
     - GET
     - List all applications
   * - ``/applications``
     - POST
     - Add new application
   * - ``/applications/{url}/status``
     - GET
     - Get application status
   * - ``/applications/{url}/status``
     - PATCH
     - Update application status

Example API Usage
^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Get jobs
   curl http://localhost:8080/jobs

   # Get applications
   curl http://localhost:8080/applications

   # Add application
   curl -X POST http://localhost:8080/applications \
     -H "Content-Type: application/json" \
     -d '{"title":"Software Engineer","company":"Acme","location":"Remote","url":"https://example.com/job","source":"remote-ok"}'

Scheduled Runs
--------------

To run the job search on a schedule, use cron (Linux/macOS) or Task Scheduler (Windows).

Linux/macOS (cron):

.. code-block:: bash

   # Run daily at 9 AM
   0 9 * * * cd /path/to/talent-acquisition-agent && uv run .\src\main.py

Windows (Task Scheduler):

.. code-block:: batch

   schtasks /create /tn "Job Agent" /tr "uv run .\src\main.py" /sc daily /st 09:00

Application Tracking
--------------------

Applications are stored in ``data/applications.json``:

.. code-block:: json

   [
     {
       "title": "Software Engineer",
       "company": "Acme Corp",
       "location": "Remote",
       "url": "https://example.com/job/123",
       "source": "remote-ok",
       "applied_date": "2026-04-25T10:00:00",
       "status": "applied",
       "notes": ""
     }
   ]

Export to CSV:

.. code-block:: python

   from src.modules.tracker import ApplicationTracker

   tracker = ApplicationTracker()
   csv_path = tracker.export_csv()
   print(f"Exported to: {csv_path}")

Kubernetes Deployment
---------------------

The project supports deployment to Kubernetes via Helm and Kustomize.

**Using Helm:**

.. code-block:: bash

   helm install job-agent ./helm/job-agent --namespace job-agent --create-namespace

**Using Kustomize:**

.. code-block:: bash

   kubectl apply -k k8s/overlays/prod

For more details, see the documentation in the ``k8s/`` directory.
