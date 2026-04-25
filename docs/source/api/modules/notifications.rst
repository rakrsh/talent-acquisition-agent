Notifications Module
====================

.. automodule:: modules.notifications
   :members:
   :undoc-members:
   :show-inheritance:

NotificationConfig
------------------

.. autoclass:: NotificationConfig
   :members:
   :undoc-members:
   :show-inheritance:

NotificationService
-------------------

.. autoclass:: NotificationService
   :members:
   :undoc-members:
   :show-inheritance:

   .. method:: send_email(subject, body)

      Send email notification.

      :param subject: Email subject
      :type subject: str
      :param body: Email body (HTML)
      :type body: str
      :returns: True if sent successfully
      :rtype: bool

   .. method:: send_sms(message)

      Send SMS notification via Twilio.

      :param message: SMS message
      :type message: str
      :returns: True if sent successfully
      :rtype: bool

   .. method:: notify_new_jobs(jobs)

      Notify about new job listings.

      :param jobs: List of Job objects
      :type jobs: list
      :returns: None
      :rtype: None