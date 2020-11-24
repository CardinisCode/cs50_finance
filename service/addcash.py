from flask import request, render_template
from helpers import apology, lookup, usd


def validate_credit_entry(credit):
    valid = False
    message = ""

    if not credit: 
        message = "No Cash value provided!"
        return (valid, message)

    elif credit[0] == '-' and credit[1].isdigit() == True:
        message = "You cannot purchase less than 1 stock."
        return (valid, message)

    # Let's check whether/not credit is indeed a float:
    dot_count = 0
    int_count = 0
    for i in credit:
        if i == "." and i != credit[0]:
            dot_count += 1
        if ord(i) >= 48 and ord(i) < 58:
            int_count += 1
    
    if (dot_count + int_count) != len(credit):
        message = "Please provide your cash value in numeric form EG 1.00 or 1"
        return (valid, message)

    if float(credit) < 1.0:
        message = "You must provide a balance above $1."
        return (valid, message)
    
    return (True, "")


def post_add_credit(session, userRepo):
    credit = request.form.get("credit")
    valid = validate_credit_entry(credit)[0]
    message = validate_credit_entry(credit)[1]
    if not valid:
        return apology(message)

    user_id = session["user_id"]
    user_account = userRepo.getById(user_id)[0]
    balance = float(user_account["cash"])
    updated_balance = round(balance + float(credit), 2)
    userRepo.updateCashById(user_id, updated_balance)
    added_cash = usd(float(credit))

    message = "You have successfully deposited " + added_cash

    balance_display = {
        "prior_balance": usd(balance), 
        "added_cash": added_cash, 
        "updated_cash_balance": usd(updated_balance),
        "message": message
    }

    return render_template("updated_balance.html", balance_display=balance_display)