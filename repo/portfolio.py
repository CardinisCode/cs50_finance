class PortfolioRepository:
    def __init__(self, db):
        self.db = db
    
    def getByUserIdAndSymbol(self, user_id, symbol):
        return self.db.execute("SELECT user_id, name, symbol, shares FROM portfolio WHERE user_id = :user_id and symbol = :symbol", user_id=user_id, symbol=symbol)

    def getByUserId(self, user_id):
        return self.db.execute("SELECT * FROM portfolio WHERE user_id = :user_id", user_id=user_id)