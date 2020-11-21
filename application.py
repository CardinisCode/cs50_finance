import os
import sys

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from datetime import datetime, date

from repo.user import UserRepository
from repo.portfolio import PortfolioRepository

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
userRepo = UserRepository(db)
portfolioRepo = PortfolioRepository(db)

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Let's first grab the current user's personal info from 'users'
    user_id = session["user_id"]
    users_portfolio = db.execute("SELECT user_id, name, symbol, cash, shares FROM portfolio INNER JOIN users ON users.id = portfolio.user_id WHERE user_id = :user_id", user_id=user_id)

    symbol = ""
    balance = 0
    portfolio_info = {}
    purchase_id = 0

    for i in users_portfolio:
        if i["user_id"] == user_id:
            purchase_id += 1
            portfolio_info[purchase_id] = {}
            symbol = i["symbol"]
            balance = round(float(i["cash"]), 2)
            shares = int(i["shares"])
            stock_current_value = int(lookup(symbol)["price"])
            total_value = round(stock_current_value * shares, 2)

            portfolio_info[purchase_id]["balance"] = usd(balance)
            portfolio_info[purchase_id]["symbol"] = symbol
            portfolio_info[purchase_id]["name"] = i["name"]
            portfolio_info[purchase_id]["shares"] = shares
            portfolio_info[purchase_id]["stock_current_value"] = usd(stock_current_value)
            portfolio_info[purchase_id]["total_value"] = usd(total_value)
            portfolio_info[purchase_id]["grand_total"] = usd(balance + total_value)

    return render_template("index.html", portfolio_info=portfolio_info)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Display form to user"""
    if request.method == "GET":
        return render_template("buy.html")

    else:
        """Buy shares of stock"""
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
        user_id = session["user_id"]

        rows = userRepo.getById(user_id)
        balance = float(rows[0]["cash"])

        final_balance = balance - purchase_value

        if final_balance < 0:
            return apology("You do not have sufficient balance for this transaction.")

        purchase_value_str = "- " + str(usd(purchase_value))

        trans_date = date.today()

        portfolio = portfolioRepo.getByUserIdAndSymbol(user_id, symbol)
        if len(portfolio) == 0:
            account_shares = 0

        else:
            account_shares = portfolio[0]["shares"]

        shares = int(account_shares) + purchased_shares

        if len(portfolio) > 0:
            result = db.execute("UPDATE portfolio SET shares = :shares WHERE user_id = :user_id AND symbol = :symbol", shares=shares, user_id=user_id, symbol=symbol);
            # raise ValueError("here", result)
        else:
            db.execute("INSERT INTO portfolio (user_id, name, symbol, shares) VALUES (:user_id, :name, :symbol, :shares)", user_id=user_id, name=company_name, symbol=symbol, shares=shares);
            
        
        db.execute("INSERT INTO history (user_id, symbol, stock_price, purchase_value, date) VALUES (:user_id, :symbol, :price, :purchase_value, :date)", user_id=user_id, symbol=symbol, price=price, purchase_value=purchase_value, date=trans_date);
        userRepo.updateCashById(user_id, final_balance)

        stock_purchase_info = { 
            "symbol": symbol,
            "name": stocks["name"],
            "shares" : purchased_shares, 
            "price": usd(price), 
            "purchase_value": purchase_value_str, 
            "id": session["user_id"],
            "user_name": rows[0]["username"],
            "balance": usd(balance),
            "final": usd(final_balance),
            "date": trans_date
        }

    return render_template("bought.html", web_data=stock_purchase_info)    


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    user_id = session["user_id"]
    if request.method == "GET":
        stocks_owned = portfolioRepo.getByUserId(user_id)

        # Let's make sure the user actually owns any stocks
        if len(stocks_owned) == 0:
            return apology("You do not own stock yet at this point")
    
        # Let's grab every stock symbol in the user's portfolio and save it in a dictionary
        stocks_purchased = {}
        for i in range(len(stocks_owned)):
            stock_item = stocks_owned[i]
            for key, value in stock_item.items():
                if key == "symbol":
                    stocks_purchased[i] = value
            #     
        return render_template("sell.html", stocks_purchased=stocks_purchased)

    # Process POST request
    symbol = request.form.get("symbol")
    shares = request.form.get("shares")
    if not shares:
        return apology("You have no provided any number of shares to sell.")

    shares = int(shares)
    if shares < 1: 
        return apology("You cannot sell less than 1 stock.")

    stocks = lookup(symbol)
    price = float(stocks["price"])
    trans_date = date.today()

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

    if updated_shares == 0:
        db.execute("DELETE FROM portfolio where symbol=:symbol and user_id=:user_id", symbol=symbol, user_id=user_id)
    else:
        result = db.execute("UPDATE portfolio SET shares = :shares WHERE user_id = :user_id AND symbol = :symbol", shares=updated_shares, user_id=user_id, symbol=symbol);




    return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        user = userRepo.getByUserName(request.form.get("username"))

        # Ensure username exists and password is correct
        if user is None or not check_password_hash(user["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "GET":
        return render_template("quote.html")

    else:
        """Process stock quote."""
        symbol = request.form.get("symbol")
        stocks = lookup(symbol)
        if stocks == None:
            return apology("This is not a valid symbol", 403)

        stocks["price"]  = usd(stocks["price"])
        
        return render_template("quoted.html", web_data=stocks)
        




@app.route("/quoted", methods=["GET", "POST"])
@login_required
def display_quote():
    """Get stock quote."""

    return apology("TODO")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        """Process a registration"""    

        username = request.form.get("username")
         # Let's check the username field is not empty
        if not username:
            return apology("You must provide a username.", 403)

        password = request.form.get("password")
        # Let's check that the password field is not empty
        if not password:
            return apology("You must provide a password.", 403)

        confirmation = request.form.get("confirmation")
        # Just to make sure the user has not left the confirm password field empty
        if not confirmation:
            return apology("You must provide a confirmation password.", 403)
        
        # Now to check that if the confirmation password provided matches their provided (above) password
        if confirmation != password:
            return apology("Your password and confirmation password do not match.", 403)

        # Let's check if the provided username already exist in our database
        user = userRepo.getByUserName(username)
        if user:
            # This means this username already exists
            return apology("This username already exists.", 403)

        # We don't want to store the actual password so let's hash the password they provide
        hashed_password = generate_password_hash(password)

        # Now we have the hashed password, let's store the username and password in our database
        session["user_id"] = userRepo.createUser(username, hashed_password)
        return redirect("/")

    # GET
    else:
        return render_template("register.html")






def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
