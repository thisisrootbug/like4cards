# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    like4cards_deviceid = fields.Char("devideId")
    like4cards_email = fields.Char("email")
    like4cards_password = fields.Char("password")
    like4cards_securitycode = fields.Char("securityCode")
    like4cards_phone = fields.Char("phone")
    like4cards_hash_key = fields.Char("hash_key")
    like4cards_secret_key = fields.Char("secret_key")
    like4cards_secret_iv = fields.Char("secret_iv")

    def get_like4cards_creds(self):
        ir_config = self.env['ir.config_parameter'].sudo()
        return {
            "like4cards_deviceid":ir_config.get_param("like4cards_deviceid", self.like4cards_deviceid),
            "like4cards_email":ir_config.get_param("like4cards_email", self.like4cards_email),
            "like4cards_password":ir_config.get_param("like4cards_password", self.like4cards_password),
            "like4cards_securitycode":ir_config.get_param("like4cards_securitycode", self.like4cards_securitycode),
            "like4cards_phone":ir_config.get_param("like4cards_phone", self.like4cards_phone),
            "like4cards_hash_key":ir_config.get_param("like4cards_hash_key", self.like4cards_hash_key),
            "like4cards_secret_key":ir_config.get_param("like4cards_secret_key", self.like4cards_secret_key),
            "like4cards_secret_iv":ir_config.get_param("like4cards_secret_iv", self.like4cards_secret_iv),
        }


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(self.get_like4cards_creds())
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param("like4cards_deviceid", self.like4cards_deviceid)
        ir_config.set_param("like4cards_email", self.like4cards_email)
        ir_config.set_param("like4cards_password", self.like4cards_password)
        ir_config.set_param("like4cards_securitycode", self.like4cards_securitycode)
        ir_config.set_param("like4cards_phone", self.like4cards_phone)
        ir_config.set_param("like4cards_hash_key", self.like4cards_hash_key)
        ir_config.set_param("like4cards_secret_key", self.like4cards_secret_key)
        ir_config.set_param("like4cards_secret_iv", self.like4cards_secret_iv)
        ir_config.set_param("like4cards_secret_key", self.like4cards_secret_key)
        ir_config.set_param("like4cards_secret_iv", self.like4cards_secret_iv)
