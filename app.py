import logging
import os
import requests
from dotenv import find_dotenv, load_dotenv

from requests_oauthlib import OAuth2Session
from os import environ as env
from flask import Flask, request, redirect, session, render_template

# uncomment for logging the requests_oauthlib requests
#logging.basicConfig(level=logging.DEBUG)

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

client_id = env.get("CLIENT_ID")
client_secret = env.get("CLIENT_SECRET")
redirect_uri = env.get("REDIRECT_URI")  # TS support 'http://localhost:3000' by default
refresh_token = env.get("REFRESH_TOKEN")


api_base_url = "https://api.tradestation.com/v3" # https://sim-api.tradestation.com/v3 for simulator account
auth_url = "https://signin.tradestation.com/authorize"
token_url = "https://signin.tradestation.com/oauth/token"
scopes = ["ReadAccount", "MarketData"]

if refresh_token is None or refresh_token == "":
    # adding offline_access for getting refresh token in the callback
    scopes.append("offline_access")

app = Flask(__name__)
app.secret_key = os.urandom(50)

ts_session = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)


@app.route("/", methods=["GET"])
def callback():
    code = request.args.get("code")

    if code is not None:
        # grant_type='authorization_code' and redirect_uri added by the OAuth2Session class
        token = ts_session.fetch_token(
            token_url=token_url,
            code=code,
            include_client_id='true',
            client_secret=client_secret,
        )
        print(f"token: {token}")
        session["token"] = token

        if 'refresh_token' in token:
            refresh_token = token['refresh_token']
            print(f"Refresh Token: {refresh_token}")

    return redirect("/index")


@app.route("/login")
def login():
    authorization_url, state = ts_session.authorization_url(
        auth_url,
        audience="https://api.tradestation.com"
    )
    logging.debug(f"authorization_url: {authorization_url}")
    return redirect(authorization_url)


@app.route("/refresh_token", methods=["GET"])
def refresh_token_action():
    new_token = ts_session.refresh_token(
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url,
        refresh_token=refresh_token,
    )
    print(f"new token: {new_token}")
    session["token"] = new_token
    return render_template("index.html", message=new_token, indent=4)


@app.route("/index", methods=["GET"])
def index():
    has_refresh_token = refresh_token is not None and refresh_token != ""
    return render_template("index.html", message=session.get('token'), has_refresh_token=has_refresh_token, indent=4)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/account_details", methods=["GET"])
def account_details():
    account_details_url = f"{api_base_url}/brokerage/accounts"
    access_token = session.get('token')['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}

    response_account_details = requests.request("GET", account_details_url, headers=headers)
    print(response_account_details.text)

    account_details_object = response_account_details.json()
    account_ids = ",".join([str(account["AccountID"]) for account in account_details_object["Accounts"]])

    account_positions_url = f"{api_base_url}/brokerage/accounts/{account_ids}/positions"
    response_positions = requests.request("GET", account_positions_url, headers=headers)
    print(response_positions.text)

    account_balances_url = f"{api_base_url}/brokerage/accounts/{account_ids}/balances"
    response_balances = requests.request("GET", account_balances_url, headers=headers)
    print(response_balances.text)

    message = f"{response_account_details.text}\n{response_positions.text}\n{response_balances.text}"
    return render_template("index.html", message=message, indent=4)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
