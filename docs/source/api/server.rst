Server Module
=============

.. automodule:: server
   :members:
   :undoc-members:
   :show-inheritance:

FastAPI Application
-------------------

The server module provides a REST API for the Job Agent.

Endpoints
^^^^^^^^^

.. http:get:: /

   Health check endpoint.

   :returns: Service status
   :rtype: dict

.. http:get:: /health

   Detailed health check.

   :returns: Health status
   :rtype: dict

.. http:get:: /jobs

   Search for jobs.

   :returns: List of jobs
   :rtype: dict

.. http:get:: /applications

   Get or add applications.

   :returns: Application list or status
   :rtype: dict
