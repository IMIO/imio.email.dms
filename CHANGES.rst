Changelog
=========


0.28.1 (unreleased)
-------------------

- Replaced `utils.safe_unicode` by `utils.safe_text`.
  [sgeulette]
- imio.email.parser improvements.
  [sgeulette]

0.28.0 (2024-10-07)
-------------------

- Improved failed attempt message.
  [sgeulette]
- Corrected email parsing with empty body (avoiding AttributeError on is_attachment).
  [sgeulette]
- Added test script
  [sgeulette]

0.27 (2024-08-23)
-----------------

- Added `post_with_retries` function, to handle operational errors and timeout from webservice. 5 tries each 30 seconds.
  [sgeulette]
- Added new option `mail_id` to treat only a specific mail id (in any status).
  [sgeulette]
- Improved mark_mail_as_imported
  [sgeulette]
- Upgraded mr.developer and reportlab, Blacked files, Code improvements, Corrected main branch name in gha
  [sgeulette]

0.26 (2023-09-13)
-----------------

- Lowercased email addresses in parser.
  [sgeulette]

0.25 (2023-08-24)
-----------------

- Handled "OSError: broken data stream when reading image file"
  [sgeulette]
- Set lower smtp sent limit
  [sgeulette]

0.24 (2023-05-23)
-----------------

- Corrected unicode error when creating unsupported email.
  [sgeulette]

0.23 (2023-05-23)
-----------------

- Added email subject in unsupported message.
  [sgeulette]
- Added MS Exchange "resent-from" in parser
  [sgeulette]

0.22 (2023-02-03)
-----------------

- Prefixed gotten eml with mailbox login.
  [sgeulette]
- Set a size limit to attach the notified email: so the output email can be sent.
  [sgeulette]
- Handled an exif parsing error
  [sgeulette]
- Renamed filenames in tar when already in
  [sgeulette]

0.21 (2023-01-25)
-----------------

- Changed orientation of image following exif information.
  [sgeulette]
- Added pil test script.
  [sgeulette]

0.20 (2023-01-24)
-----------------

- Kept exif information from original resized image.
  [sgeulette]

0.19 (2022-12-01)
-----------------

- Handled specifically IBM Notes forward (parser modification).
  [sgeulette]

0.18 (2022-11-28)
-----------------

- Handled specifically Apple Mail forward with image in content (parser modification).
  [sgeulette]

0.17 (2022-07-03)
-----------------

- Changed process_mails output to filter easierly.
  [sgeulette]
- Added new option `reset_flags` for `process_mails` to reset all flags of an email id.
  [sgeulette]
- Used default policy in parser
  [sgeulette]
- Output rfc822 payload in parser
  [sgeulette]

0.16 (2022-06-07)
-----------------

- Used now email2pdf2.
  [sgeulette]
- Handled exception when sending notification mail
  [sgeulette]

0.15 (2022-05-12)
-----------------

- Set locale time to avoid UTC time
  [sgeulette]

0.14 (2022-04-29)
-----------------

- Do not mark mail in dev_mode.
  [sgeulette]
- Handled image save when quality parameter is not compliant
  [sgeulette]
- Avoided error with x-forward
  [sgeulette]

0.13 (2022-04-19)
-----------------

- Retried 5 times to upload when webservice has an unknown response
  [sgeulette]
- Handled UnidentifiedImageError when opening image file to resize
  [sgeulette]
- Corrected UnicodeEncodeError when sending notification email
  [sgeulette]

0.12 (2022-03-31)
-----------------

- Used correct recipient for ignored mail
  [sgeulette]
- Used `smtp.send_message` to consider bcc
  [sgeulette]

0.11 (2022-03-14)
-----------------

- Corrected false 'inline' disposition attachments.
  [sgeulette]
- Do not include inline attachments
  [sgeulette]
- Reduced image attachments
  [sgeulette]
- Improved `--list_emails` output.
  [sgeulette]
- Added dev_mode flag
  [sgeulette]

0.10 (2022-02-17)
-----------------

- Removed newline characters from attachment filename in imio.email.parser.
  [sgeulette]

0.9 (2022-02-17)
----------------

- Removed pattern in sent email for ignored error.
  [sgeulette]
- Corrected badly addresses from email.utils.getAddresses (in imio.email.parser)
  [sgeulette]
- Upgraded mail-parser
  [sgeulette]

0.8 (2022-01-24)
----------------

- Ignored 'ignored' flaged mails when getting waiting emails.
  [sgeulette]

0.7 (2022-01-21)
----------------

- Added transferer check following pattern to avoid anyone can push an email in the app.
  [sgeulette]

0.6 (2022-01-13)
----------------

- Corrected bug in email2pdf.
  [sgeulette]

0.5 (2022-01-11)
----------------

- Added --stats option.
  [sgeulette]
- Added timeout in email2pdf to avoid wasting time in external image retriever
  [sgeulette]

0.4 (2021-11-24)
----------------

- Send email notification after clean_mails.
  [sgeulette]
- Corrected error in get_eml option. Added `save_as_eml` function.
  [sgeulette]
- Handled pdf conversion error by sending eml file
  [sgeulette]
- Set unsupported email in french
  [sgeulette]

0.3 (2021-07-23)
----------------

- Avoid exception when decoding in `get_email`
  [sgeulette]
- Added script to clean old processed emails.
  [sgeulette]
- Changed --list_emails parameter in main script
  [sgeulette]

0.2 (2021-05-12)
----------------

- Used https in requests urls if port is 443.
  [sgeulette]

0.1 (2021-05-12)
----------------

- Initial release.
  [laulaz, sgeulette]
