==============
imio.email.dms
==============

This package ensures the import of incoming emails into DMS.


Features
--------

1. fetch waiting emails from IMAP mailbox
2. parse emails (headers, attachments, ...)
3. generate a PDF email preview
4. send informations to DMS webservice
5. mark emails as imported


Usage
-----

To process emails, you can execute ::

 bin/process_mails config.ini

See `config.ini` file for various parameters.


Errors
------

In case the importation process fails, the corresponding emails are marked as
errors and are not taken into account anymore.
An email notification is sent with the problematic email attached.
To process them again, you can execute ::

 bin/process_mails config.ini --requeue_errors



Requirements
------------

package wkhtmltopdf


Contribute
----------

- Issue Tracker: https://github.com/collective/imio.email.dms/issues
- Source Code: https://github.com/collective/imio.email.dms


License
-------

The project is licensed under the GPLv2.
