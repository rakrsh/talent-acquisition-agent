Introduction
============

Job Agent is an open-source talent acquisition agent that automates your job search workflow.

Overview
--------

Job Agent helps you:

- **Search** multiple job boards (Remote OK, LinkedIn, Indeed)
- **Notify** you via email and SMS when new jobs match your criteria
- **Track** all your applications in a local database
- **Apply** automatically to matching jobs (beta)

Architecture
------------

The application follows the 12-Factor App methodology for cloud-native deployment:

.. mermaid::

   graph LR
       A[main.py] --> B[JobSearcher]
       A[main.py] --> C[NotificationService]
       A[main.py] --> D[ApplicationTracker]
       B --> E[Remote OK API]
       B --> F[LinkedIn API]
       C --> G[SMTP]
       C --> H[Twilio]
       D --> I[(JSON DB)]

Key Concepts
------------

- **Job Searcher**: Fetches jobs from various sources
- **NotificationService**: Sends email/SMS alerts
- **ApplicationTracker**: Records all job applications
- **Settings**: Centralized configuration via environment variables

Use Cases
---------

1. **Passive Job Search**: Run daily to get email notifications of new jobs
2. **Active Application Tracking**: Track all applications in one place
3. **API Service**: Run as a REST API for integration with other tools