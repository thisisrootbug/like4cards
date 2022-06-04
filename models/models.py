from odoo import fields, models, api


class Like4CardCategories(models.Model):
    _name = "like4card"
    _description = "like4card model"

    name = fields.Char()

    def categories(self,langId=2, **kw):
        creds = self.env['res.config.settings'].get_values()
        data = {"deviceId": creds["like4cards_deviceid"],
                "email": creds["like4cards_email"],
                "password": creds["like4cards_password"],
                "securityCode": creds["like4cards_securitycode"],
                "langId": langId,
                }
        res = requests.post("https://taxes.like4app.com/online/categories",data=data)
        return res.text


    def products(self,langId=2,categoryId=0,ids=[], **kw):
        creds = self.env['res.config.settings'].get_values()
        data = {"deviceId": creds["like4cards_deviceid"],
                "email": creds["like4cards_email"],
                "password": creds["like4cards_password"],
                "securityCode": creds["like4cards_securitycode"],
                "langId": langId,
                }
        if categoryId != 0:
            data["categoryId"] = categoryId
            res = requests.post("https://taxes.like4app.com/online/products",data=data)
            return res.text
