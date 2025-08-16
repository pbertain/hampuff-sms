from flask import Flask, request, redirect
from lib import hampuff_lib
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

account_sid = 'put_your_account_sid_here'
auth_token = 'put_your_auth_token_here'

sms_reply_hampuff = "Wrong number.  That might be an airport so please text Airpuff at sms://+1-802-247-7833 / [802-AIR-PUFF]"

CONSENT_MESSAGE = "Your SMS request provides consent to send the reply."

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""

    full_body = request.values.get('Body', None)
    body = full_body.strip()
    if ('fuck' in body.lower()):
        sms_resp_body = "Go fuck yourself, too"
    elif ('shit' in body.lower()):
        sms_resp_body = "Go shit your pants"
    elif (len(body.lower()) == 4):
        sms_resp_body = sms_reply_hampuff
    elif ('hampuff' in body.lower()):
        sms_resp_body = hampuff_lib.hampuff_data(body) + f"\n\n{CONSENT_MESSAGE}"
    else:
        sms_resp_body = "Wrong number.  Please waste someone else's time"

    # Start our TwiML response
    resp = MessagingResponse()
    resp.message(sms_resp_body)
    return str(resp)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = '0'
    response.headers["Pragma"] = "no-cache"
    return response


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=15015)
