from odoo import api, fields, models, _
import requests
    

class WebsiteLeadAPI(models.Model):
    _inherit = "crm.lead"
    
    def getWebPortalLead(self):
        # url = "http://43.204.150.52/api/resource/Lead Intake?fields=[\"name\",\"name1\",\"email\",\"phone\",\"date\",\"location\",\"service\",\"pincode\"]&filters=[[\"date\",\"=\",\"2023-11-28\"]]"
        # payload = {}
        # headers = {
        #     'Authorization': 'token 891efaeda925d28:8591fcacba3526f',
        #     'Cookie': 'full_name=User; sid=2fe89fc28135ada2529327189924e4ef4f9147f8c83d6e7ce7440a69; system_user=yes; user_id=user%40gmail.com; user_image='
        # }
        # response = requests.request("GET", url, headers=headers, data=payload)
        # print(response.text)
        #
        url = "http://43.204.150.52/api/resource/Lead Intake"
        # url = "http://43.204.150.52/api/resource/Locations"
        # url = "https://catfact.ninja/fact"
        # fields = ["name", "name1", "email", "phone", "date", "location"]
        fields = ["name"]
        headers = {"Authorization": "token 891efaeda925d28:8591fcacba3526f"}
        # filters = [["date", "=", "2023-11-28"]]
        # filters = ["name", "=", "Ernakulam"]

        # params = {"fields": fields, "filters": filters}
        response = requests.get(url, headers=headers)
        # response = requests.get(url, params={"fields": fields, "filters": filters}, headers=headers)
        print(response)

        if response.status_code == 200:
            data = response.json()
            # try:
            #     leadData = self.env['crm.lead'].sudo().create({
            #         'name': "jhgkui",
            #         'description': "kjhgisjodsiuhdo",
            #         'company_id': self.company_id.id,
            #     })
            #     print(leadData)
            # except Exception as e:
            #     # Handle the exception here
            #     print(f"An error occurred: {e}")
            # print(data)
            # for row in data:
            #     name = row[name]

            #     if row:
            #         leadData = self.env['crm.lead'].sudo().create({
            #             'name': row[name],
            #             'description': row
            #         })

        else:
            print(f"Error: {response.status_code}")
            print(response.text)
