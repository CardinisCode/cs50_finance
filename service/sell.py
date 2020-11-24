from flask import request, render_template
from helpers import apology, lookup, usd
from datetime import datetime, date


def post_sale(session, portfolioRepo, userRepo, historyRepo, user_id):
    symbol = request.form.get("symbol")
    shares = request.form.get("shares")
    if not shares:
        return apology("You have no provided any number of shares to sell.")

    elif shares[0] == '-' and shares[1].isdigit() == True:
        return apology(message="You cannot purchase less than 1 stock.")

    if shares.isdigit() == False: 
        return apology(message="You should provide a QTY of shares in numeric form EG 1")

    shares = int(shares)
    if shares < 1: 
        return apology("You cannot sell less than 1 stock.")

    # Since I've limited the user to select only from the stocks they currently own
    # the user cannot select an invalid symbol
    stocks = lookup(symbol)
    
    price = float(stocks["price"])
    trans_date = datetime.today()
    str_date = trans_date.strftime('%Y-%m-%d-%X')

    rows = userRepo.getById(user_id)
    balance = float(rows[0]["cash"])

    current_share = portfolioRepo.getByUserIdAndSymbol(user_id, symbol)
    stock_details = current_share[0]
    company_name = stock_details["name"]

    if shares > stock_details["shares"]:
        return apology("You're selling more stocks than you own!")

    updated_shares = stock_details["shares"] - shares
    purchase_value = price * shares
    final_balance = balance + purchase_value
    username = userRepo.getById(user_id)

    if updated_shares == 0:
        portfolioRepo.DeleteByUserIdAndSymbol(user_id, symbol)
    else:
        portfolioRepo.UpdateSharesbyUserIDAndSymbol(user_id, symbol, updated_shares)

    trans_type = 'Sold'
    historyRepo.InsertTransactionDetails(user_id, symbol, price, purchase_value, str_date, shares, trans_type)
    userRepo.updateCashById(user_id, final_balance)

    stock_purchase_info = { 
        "symbol": symbol,
        "name": company_name,
        "shares" : shares, 
        "price": usd(price), 
        "purchase_value": usd(round(purchase_value, 2)), 
        "id": user_id,
        "user_name": username,
        "balance": usd(balance),
        "final": usd(final_balance),
        "date": str_date,
    }

    message = "Sold!"
    return render_template("sold.html", web_data=stock_purchase_info, message=message)


