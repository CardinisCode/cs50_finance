from helpers import lookup, usd, apology
from flask import Flask, render_template, session


def pull_user_transaction_history(session, user_id, historyRepo):
    history = historyRepo.getTransactionHistoryByUserId(user_id)
    if history == None:
        return apology("This user has no history")

    transaction_history = []
    count = 0
    for transaction in history: 
        count += 1
        symbol = history[count - 1]["symbol"]
        price = usd(round(history[count - 1]["stock_price"], 2))
        date = history[count - 1]["date"]
        shares = history[count - 1]["shares"]
        trans_type = history[count - 1]["trans_type"]

        if trans_type == 'Sold':
            shares *= -1

        transaction_history.append({
            "id": count,
            "symbol": symbol, 
            "stock_price": price, 
            "shares": shares,
            "date": date,
            "trans_type": trans_type
        })

    return render_template("history.html", history=transaction_history)
