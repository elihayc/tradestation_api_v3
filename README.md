# tradestation api v3 Example
Trade Station API v3 Python Example

# Overview
Using Flask for login to Trade Station with OAuth 2 codeflow, and call to Brokerage API such as Get Account Details / Open Positions / Balances.

# Instructions

For using this example you need to ask for Trade Station Client key and Secret from TradeStation Support team.

once you have it, create a new .env file in the root folder with the same settings as .env_template file has, and update the CLIENT_ID and CLIENT_SECRET.

If you would like also to test automatic login with refresh_token, you can set the REFRESH_TOKEN with a user refresh_token.

# Documentation
Trade Station authentication documentation: https://api.tradestation.com/docs/fundamentals/authentication/auth-overview

Trade Station API Documentation: https://api.tradestation.com/docs/specification
