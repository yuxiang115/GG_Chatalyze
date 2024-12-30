# system library for getting the command line argument
# web library
import http.client


def send(message_list):
    # your webhook URL
    webhookurl = "https://discordapp.com/api/webhooks/1126626700583764039/bMgauGtsszaCd0_mGgMSc_KgZ9MQIiNF1grrliESymBztocLBMOtZsZ_-oZZya6H9Niu"
    results = []
    header = "========================================================= GG_CHATALYZE ============================================================="
    new_message_list = [header] + [message for message in message_list]
    for message in new_message_list:
        # compile the form data (BOUNDARY can be anything)
        formdata = (
            "------:::BOUNDARY:::\r\n"
            "Content-Disposition: form-data; name=\"content\"\r\n\r\n"
            + message
            + "\r\n------:::BOUNDARY:::--"
        ).encode("utf-8")
        # get the connection and make the request
        connection = http.client.HTTPSConnection("discordapp.com")
        connection.request("POST", webhookurl, formdata, {
            'content-type': "multipart/form-data; boundary=----:::BOUNDARY:::",
            'cache-control': "no-cache",
        })

        # get the response
        response = connection.getresponse()
        results.append(response.read().decode("utf-8"))

    # return back to the calling function with the result
    return results



