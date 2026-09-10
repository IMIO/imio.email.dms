# -*- coding: utf-8 -*-
import logging


dev_mode = False

logger = logging.getLogger("imio.email.dms")
logger.setLevel(logging.INFO)
chandler = logging.StreamHandler()
chandler.setLevel(logging.INFO)
chandler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(chandler)
