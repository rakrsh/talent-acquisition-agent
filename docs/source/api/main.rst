Main Module
===========

.. automodule:: main
   :members:
   :undoc-members:
   :show-inheritance:

``run_job_search``
------------------

.. async function:: run_job_search()

   Main job search and notification pipeline.

   This function:
   1. Initializes the job searcher, notification service, and application tracker
   2. Searches for jobs across configured sources
   3. Filters out already-applied jobs
   4. Sends notifications for new jobs
   5. Logs the final summary

   :returns: None
   :rtype: None