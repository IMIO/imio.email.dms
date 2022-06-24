# -*- coding: utf-8 -*-
from email._policybase import compat32
from email.policy import default

import logging


dev_mode = False
email_policy = default

logger = logging.getLogger("imio.email.dms")
logger.setLevel(logging.INFO)
chandler = logging.StreamHandler()
chandler.setLevel(logging.INFO)
logger.addHandler(chandler)
