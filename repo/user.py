class UserRepository():
    def __init__(self, db):
        self.db = db

    def getById(self, user_id):
        return self.db.execute("SELECT * FROM users WHERE id = :user_id", user_id=user_id)

    def getByUserName(self, username):
        user = self.db.execute(
            "SELECT * FROM users WHERE username = :username",
            username=username
        )
        if len(user) == 0:
            return None

        return user[0]

    def updateCashById(self, user_id, balance):
        self.db.execute("UPDATE users SET cash = :balance WHERE id = :user_id", balance=balance, user_id=user_id)

    def createUser(self, username, hashed_password):
        return self.db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=hashed_password)
