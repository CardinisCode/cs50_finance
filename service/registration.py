from flask import request, render_template, redirect, flash
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology


def check_password(password):
    if len(password) < 6: 
        flash('Your password should have at least 6 characters')
        return False

    allowed_characters = ["!", "#", "$", "%", "^", "&", "*", "~"]
    special_char_count = 0
    number_count = 0
    for i in password:
        if i in allowed_characters:
            special_char_count += 1
        
        if i.isdigit():
            number_count += 1

    if special_char_count <= 0:
        flash('You should have at least 1 special character in your password!')
        return False

    if number_count <= 0:
        flash('You should have at least 1 number/digit in your password!')
        return False

    return True


def check_username(username, userRepo):
    valid = False

    # Let's check the username field is not empty
    if not username:
        flash('You must provide a username.')
        return valid

    # To check that username doesn't start with a digit
    firstCharacter = username[0]
    if ord(firstCharacter) >= 48 and ord(firstCharacter) <= 57:
        flash('Invalid Username. Please check the requirements for the username.')
    #     message = "Invalid Username. Please check the requirements for the username."
        return valid

    # To double check that the username actually includes alphabetical characters:
    alpha_count = 0
    number_count = 0
    for i in username:
        # Upper case alphabetical characters
        if ord(i) >= 65 and ord(i) <= 90:
            alpha_count += 1

        # Lower case alphabetical characters
        elif ord(i) >= 97 and ord(i) <= 122:
            alpha_count += 1
        
        # Numbers / Digits
        elif ord(i) >= 48 and ord(i) <= 57:
            number_count += 1

    if alpha_count < 3:
        flash('Invalid Username. Please check the requirements for the username.')
        return valid

    if len(username) < 6: 
        flash('Invalid Username. Please check the requirements for the username.')
        return valid

    if alpha_count == len(username):
        flash('Invalid Username. Please check the requirements for the username.')
        return valid

    if (number_count + alpha_count) != len(username):
        flash('Invalid Username. Please check the requirements for the username.')
        return valid

    # Let's check if the provided username already exist in our database
    user = userRepo.getByUserName(username)
    if user:
        # This means this username already exists
        flash('This username already exists.')
        return valid

    return True

    
def post_register(session, userRepo):
    username = request.form.get("username")
    valid = check_username(username, userRepo)

    if not valid:
        return redirect("/register")

    user = userRepo.getByUserName(username)

    # Grab password from User
    password = request.form.get("password")
    # Let's check that the password field is not empty
    if not password:
        flash("You must provide a password.")
        return redirect("/register")

    #Now let's make sure the password actually meets password requirements
    valid_password = check_password(password)
    if valid_password == False:
        return redirect("/register")

    confirmation = request.form.get("confirmation")
    # Just to make sure the user has not left the confirm password field empty
    if not confirmation:
        flash('You must provide a confirmation password.')
        return redirect("/register")

    # Now to check that if the confirmation password provided matches their provided (above) password
    if confirmation != password:
        flash('Your password and confirmation password do not match.')
        return redirect("/register")

    # We don't want to store the actual password so let's hash the password they provide
    hashed_password = generate_password_hash(password)

    # Now we have the hashed password, let's store the username and password in our database
    session["user_id"] = userRepo.createUser(username, hashed_password)
    flash('Registration Complete!')
    return redirect("/")
