from flask import request, render_template
from helpers import apology, lookup, usd

def post_add_credit(session, userRepo):
    credit = request.form.get("credit")
    if not credit: 
        return apology("No cash value provided")

    elif credit[0] == '-' and credit[1].isdigit() == True:
        return apology(message="You cannot purchase less than 1 stock.")

    # Temporary function to validate whether credit is indeed a float:
    dot_count = 0
    int_count = 0
    for i in credit:
        if i == "." and i != credit[0]:
            dot_count += 1
        if ord(i) >= 48 and ord(i) < 58:
            int_count += 1
    
    if (dot_count + int_count) != len(credit):
        return apology(message="Please provide your cash value in numeric form EG 1.00 or 1")
            
    # if credit_float. == False: 
    #     return apology(message="Please provide your cash value in numeric form EG 1.00 or 1")

    credit_float = float(credit)

    if credit_float < 1.0:
        return apology("You must provide a balance above $1.")

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