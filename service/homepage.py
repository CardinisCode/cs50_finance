from helpers import lookup, usd
from flask import Flask, render_template, session


def create_homepage_content(session, user_id, portfolioRepo, userRepo):
    user = userRepo.getById(user_id)[0]
    balance = round(float(user["cash"]), 2)
    username = user["username"]

    users_portfolio = portfolioRepo.getByUserId(user_id)

    symbol = ""
    portfolio_info = {}
    purchase_id = 0
    grand_total = balance

    for i in users_portfolio:
        if i["user_id"] == user_id:
            purchase_id += 1
            portfolio_info[purchase_id] = {}

            symbol = i["symbol"]
            shares = int(i["shares"])
            stock_current_value = int(lookup(symbol)["price"])
            total_value = round(stock_current_value * shares, 2)
            grand_total += total_value

            portfolio_info[purchase_id] = {
                "symbol": symbol, 
                "name": i["name"], 
                "shares": shares, 
                "stock_current_value": usd(stock_current_value), 
                "total_value": usd(total_value), 
            }

    user_info = {
        "username": username,
        "balance": usd(balance), 
        "grand_total": usd(round(grand_total, 2))
    }

    return render_template("index.html", portfolio_info=portfolio_info, user_info=user_info)