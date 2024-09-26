from suds.client import Client


def send_notification(message, contact_number):
    url = 'https://wiserv.dswd.gov.ph/soap/?wsdl'
    try:
        client = Client(url)
        result = client.service.sendMessage(UserName='crgwiservuser', PassWord='#w153rvcr9!', WSID='0',
                                            MobileNo=contact_number, Message=message)
    except Exception:
        pass


contact_numbers = [{'Vergel Rey': ['09154408923']}, {'Jen-Eric': ['09464131587']}, {'Phillipe Erick': ['09287167193']}]
for contact in contact_numbers:
    for k, vs in contact.items():
        for v in vs:
            send_notification('Good day, {}! The DSWD Caraga WiServ SMS API is still up and alive.'.format(k), v)
