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
from repo.history import HistoryRepository
from service.registration import post_register
from service.buy import post_buy
from service.sell import post_sale
from service.addcash import post_add_credit
from service.homepage import create_homepage_content
from service.transaction_history import pull_user_transaction_history

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
historyRepo = HistoryRepository(db)

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    return create_homepage_content(session, user_id, portfolioRepo, userRepo)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Display form to user"""
    if request.method == "GET":
        return render_template("buy.html")

    """Buy shares of stock"""
    return post_buy(session, userRepo, portfolioRepo, historyRepo)


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
     
        return render_template("sell.html", stocks_purchased=stocks_purchased)

    # Process POST request
    return post_sale(session, portfolioRepo, userRepo, historyRepo, user_id)
    


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    return pull_user_transaction_history(session, user_id, historyRepo)

    # history = historyRepo.getTransactionHistoryByUserId(user_id)
    # if history == None:
    #     return apology("This user has no history")

    # transaction_history = []
    # count = 0
    # for transaction in history: 
    #     count += 1
    #     symbol = history[count - 1]["symbol"]
    #     price = usd(round(history[count - 1]["stock_price"], 2))
    #     date = history[count - 1]["date"]
    #     shares = history[count - 1]["shares"]
    #     trans_type = history[count - 1]["trans_type"]

    #     if trans_type == 'Sold':
    #         shares *= -1

    #     transaction_history.append({
    #         "id": count,
    #         "symbol": symbol, 
    #         "stock_price": price, 
    #         "shares": shares,
    #         "date": date,
    #         "trans_type": trans_type
    #     })

    # return render_template("history.html", history=transaction_history)


@app.route("/buy_credit", methods=["GET", "POST"])
@login_required
def add_credit():
    """Display form to user"""
    if request.method == "GET":
        return render_template("buy_credit.html")

    # POST
    return post_add_credit(session, userRepo)


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
        

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        """Process a registration"""    
        return post_register(session, userRepo)

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
