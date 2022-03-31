Changelog
=========


0.12 (unreleased)
-----------------

- Used correct recipient for ignored mail
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
