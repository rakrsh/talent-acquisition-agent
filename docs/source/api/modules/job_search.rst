Job Search Module
=================

.. automodule:: modules.job_search
   :members:
   :undoc-members:
   :show-inheritance:

Job Data Class
--------------

.. autoclass:: Job
   :members:
   :undoc-members:
   :show-inheritance:

JobSearcher Class
-----------------

.. autoclass:: JobSearcher
   :members:
   :undoc-members:
   :show-inheritance:

   .. method:: search_all()

      Search all configured job sources.

      :returns: List of Job objects
      :rtype: list[Job]

   .. method:: _search_remote_ok()

      Search Remote OK job board.

      :returns: List of Job objects from Remote OK
      :rtype: list[Job]