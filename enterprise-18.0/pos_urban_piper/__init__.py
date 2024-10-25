from . import controllers
from . import models

import uuid


def _urban_piper_post_init(env):
    if not env['ir.config_parameter'].sudo().get_param('pos_urban_piper.uuid'):
        env['ir.config_parameter'].sudo().set_param('pos_urban_piper.uuid', str(uuid.uuid4()))
