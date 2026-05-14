Settings Module
===============

.. automodule:: settings

Settings Class
--------------

.. autodata:: settings
   :annotation: Global settings instance

.. autoclass:: Settings
   :members:
   :undoc-members:
   :show-inheritance:

Configuration Variables
-----------------------

.. envvar:: ENV_MODE

   Environment mode (development, production)

.. envvar:: LOG_LEVEL

   Logging level (DEBUG, INFO, WARNING, ERROR)

.. envvar:: OLLAMA_HOST

   LLM server host URL

.. envvar:: LLM_MODEL

   LLM model name

.. envvar:: DATABASE_URL

   Database connection URL

.. envvar:: SENDER_EMAIL

   Email sender address

.. envvar:: SENDER_PASSWORD

   Email sender password (app password)

.. envvar:: RECIPIENT_EMAIL

   Email recipient address

.. envvar:: TWILIO_SID

   Twilio account SID

.. envvar:: TWILIO_TOKEN

   Twilio auth token

.. envvar:: TWILIO_PHONE

   Twilio phone number

.. envvar:: RECIPIENT_PHONE

   SMS recipient phone number