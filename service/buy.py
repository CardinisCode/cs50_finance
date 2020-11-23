
from flask import request, render_template
from helpers import apology, lookup, usd
from datetime import datetime, date


def post_buy(session, userRepo, portfolioRepo, historyRepo):
    symbol = request.form.get("symbol")
    if symbol == '':
        return apology(message="No stock symbol provided!")

    shares = request.form.get("shares")
    if shares == '':
        return apology(message="You have no specified how many shares you'd like to buy.")
    
    elif int(shares) < 1: 
        return apology(message="You cannot purchase less than 1 stock.")

    purchased_shares = int(shares)
    stocks = lookup(symbol)
    if stocks == None:
        return apology(message="Not a valid Stock symbol!")

    price = float(stocks["price"])
    company_name = stocks["name"]
    purchase_value = price * int(purchased_shares)

    # Let's grab the user's balance:
    user_id = session["user_id"]
    user_account = userRepo.getById(user_id)[0]
    balance = float(user_account["cash"])

    final_balance = balance - purchase_value
    if final_balance < 0:
        return apology("You do not have sufficient balance for this transaction.")

    purchase_value = purchase_value * -1

    trans_date = datetime.today()
    str_date = trans_date.strftime('%Y-%m-%d-%X')
    portfolio = portfolioRepo.getByUserIdAndSymbol(user_id, symbol)
    if len(portfolio) == 0:
        account_shares = 0

    else:
        account_shares = portfolio[0]["shares"]

    shares = int(account_shares) + purchased_shares
    trans_type = 'Bought'

    if len(portfolio) > 0:
        portfolioRepo.UpdateSharesbyUserIDAndSymbol(user_id, symbol, shares)
    else:
        portfolioRepo.InsertUserIdAndNameAndSymbolAndShares(user_id, company_name, symbol, shares)
        
    historyRepo.InsertTransactionDetails(user_id, symbol, price, purchase_value, str_date, purchased_shares, trans_type)
    userRepo.updateCashById(user_id, final_balance)

    stock_purchase_info = { 
        "symbol": symbol,
        "name": stocks["name"],
        "shares" : purchased_shares, 
        "price": usd(price), 
        "purchase_value": usd(purchase_value), 
        "id": session["user_id"],
        "user_name": user_account["username"],
        "balance": usd(balance),
        "final": usd(final_balance),
        "date": str_date,
        "trans_type": trans_type
    }

    message = "Bought!"
    return render_template("bought.html", web_data=stock_purchase_info, message=message)

