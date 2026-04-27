Configuration
=============

Job Agent uses environment variables for all configuration (12-Factor App Factor III).

Environment Variables
---------------------

Create a ``.env`` file from the example:

.. code-block:: bash

   cp .env.example .env

Application Settings
^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Variable
     - Description
     - Default
   * - ``ENV_MODE``
     - Environment mode
     - ``development``
   * - ``LOG_LEVEL``
     - Logging level
     - ``INFO``
   * - ``HTTP_HOST``
     - HTTP server host
     - ``0.0.0.0``
   * - ``HTTP_PORT``
     - HTTP server port
     - ``8080``

LLM Configuration
^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Variable
     - Description
     - Default
   * - ``OLLAMA_HOST``
     - LLM server URL
     - ``http://localhost:11434``
   * - ``LLM_MODEL``
     - LLM model name
     - ``llama3``

Notification Settings
^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Variable
     - Description
     - Default
   * - ``SENDER_EMAIL``
     - Email sender address
     - (empty)
   * - ``SENDER_PASSWORD``
     - Email app password
     - (empty)
   * - ``RECIPIENT_EMAIL``
     - Email recipient
     - (empty)
   * - ``TWILIO_SID``
     - Twilio account SID
     - (empty)
   * - ``TWILIO_TOKEN``
     - Twilio auth token
     - (empty)
   * - ``TWILIO_PHONE``
     - Twilio phone number
     - (empty)
   * - ``RECIPIENT_PHONE``
     - SMS recipient
     - (empty)

Job Search Settings
^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Variable
     - Description
     - Default
   * - ``REMOTE_OK_ENABLED``
     - Enable Remote OK search
     - ``true``
   * - ``LINKEDIN_ENABLED``
     - Enable LinkedIn search
     - ``false``
   * - ``INDEED_ENABLED``
     - Enable Indeed search
     - ``false``
   * - ``MAX_JOBS_PER_SEARCH``
     - Max jobs to fetch
     - ``20``
   * - ``SEARCH_INTERVAL_HOURS``
     - Search interval
     - ``24``
   * - ``AUTO_APPLY_ENABLED``
     - Enable auto-apply
     - ``false``

Search Criteria
---------------

Edit ``input/search_criteria.json`` to define your job search:

.. code-block:: json

   {
     "search_terms": [
       {
         "role": "python",
         "keywords": ["backend", "api"],
         "locations": ["remote"],
         "job_types": ["full-time"]
       }
     ],
     "excluded_companies": [],
     "experience_level": ["mid", "senior"],
     "date_posted_days": 7
   }

Configuration Fields
^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Field
     - Description
   * - ``role``
     - Search tag (e.g., python, react, javascript)
   * - ``keywords``
     - Additional keywords to filter
   * - ``locations``
     - Job locations (remote, US, UK, etc.)
   * - ``job_types``
     - Job types (full-time, contract, etc.)
