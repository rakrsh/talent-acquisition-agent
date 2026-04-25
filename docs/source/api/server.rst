Server Module
=============

.. automodule:: server
   :members:
   :undoc-members:
   :show-inheritance:

FastAPI Application
------------------

The server module provides a REST API for the Job Agent.

Endpoints
^^^^^^^^^

.. http:endpoint:: /

   Health check endpoint.

   :returns: Service status
   :rtype: dict

.. http:endpoint:: /health

   Detailed health check.

   :returns: Health status
   :rtype: dict

.. http:endpoint:: /jobs

   Search for jobs.

   :returns: List of jobs
   :rtype: dict

.. http:endpoint:: /applications

   Get or add applications.

   :returns: Application list or status
   :rtype: dict