from flask import request
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology


def check_password(password):
    error_message = ""
    if len(password) < 6: 
        error_message = "Your password should have at least 6 characters"
        return (False, error_message)
    
    allowed_characters = ["!", "#", "$", "%", "^", "&", "*", "~"]
    special_char_count = 0
    number_count = 0
    for i in password:
        if i in allowed_characters:
            special_char_count += 1
        
        if i.isdigit():
            number_count += 1
    
    if special_char_count <= 0:
        error_message = "You should have at least 1 special character in your password!"
        return (False, error_message)

    if number_count <= 0:
        error_message = "You should have at least 1 number/digit in your password!"
        return (False, error_message)

    return (True, error_message)


def post_register(session, userRepo):
    username = request.form.get("username")
    # Let's check the username field is not empty
    if not username:
        return apology("You must provide a username.", 403)

    # Let's check if the provided username already exist in our database
    user = userRepo.getByUserName(username)
    if user:
        # This means this username already exists
        return apology("This username already exists.", 403)

    # Grab password from User
    password = request.form.get("password")
    # Let's check that the password field is not empty
    if not password:
        return apology("You must provide a password.", 403)
    
    #Now let's make sure the password actually meets password requirements
    valid_password = check_password(password)[0]
    message = check_password(password)[1]
    if valid_password == False:
        return apology(message, 403)

    confirmation = request.form.get("confirmation")
    # Just to make sure the user has not left the confirm password field empty
    if not confirmation:
        return apology("You must provide a confirmation password.", 403)
    
    # Now to check that if the confirmation password provided matches their provided (above) password
    if confirmation != password:
        return apology("Your password and confirmation password do not match.", 403)



    # We don't want to store the actual password so let's hash the password they provide
    hashed_password = generate_password_hash(password)

    # Now we have the hashed password, let's store the username and password in our database
    session["user_id"] = userRepo.createUser(username, hashed_password)
    return redirect("/")
