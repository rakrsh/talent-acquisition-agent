Tracker Module
==============

.. automodule:: modules.tracker
   :members:
   :undoc-members:
   :show-inheritance:

JobApplication
--------------

.. autoclass:: JobApplication
   :members:
   :undoc-members:
   :show-inheritance:

ApplicationTracker
------------------

.. autoclass:: ApplicationTracker
   :members:
   :undoc-members:
   :show-inheritance:

   .. method:: add_application(job)

      Record a new job application.

      :param job: Job object to record
      :type job: Job
      :returns: True if recorded, False if already exists
      :rtype: bool

   .. method:: get_applications(status=None)

      Get all applications, optionally filtered.

      :param status: Filter by status (applied, pending, rejected, interview)
      :type status: str, optional
      :returns: List of JobApplication objects
      :rtype: list[JobApplication]

   .. method:: update_status(url, status, notes='')

      Update application status.

      :param url: Job URL
      :type url: str
      :param status: New status
      :type status: str
      :param notes: Optional notes
      :type notes: str
      :returns: True if updated, False if not found
      :rtype: bool

   .. method:: get_summary()

      Get application statistics.

      :returns: Dictionary with counts by status
      :rtype: dict

   .. method:: export_csv(output_path=None)

      Export applications to CSV.

      :param output_path: Output file path
      :type output_path: str, optional
      :returns: Path to exported CSV
      :rtype: str