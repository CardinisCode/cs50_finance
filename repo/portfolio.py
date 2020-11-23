class PortfolioRepository:
    def __init__(self, db):
        self.db = db
    
    def getByUserIdAndSymbol(self, user_id, symbol):
        return self.db.execute("SELECT user_id, name, symbol, shares FROM portfolio WHERE user_id = :user_id and symbol = :symbol", user_id=user_id, symbol=symbol)

    def getByUserId(self, user_id):
        return self.db.execute("SELECT * FROM portfolio WHERE user_id = :user_id", user_id=user_id)

    def UpdateSharesbyUserIDAndSymbol(self, user_id, symbol, shares):
        self.db.execute("UPDATE portfolio SET shares = :shares WHERE user_id = :user_id AND symbol = :symbol", shares=shares, user_id=user_id, symbol=symbol)

    def DeleteByUserIdAndSymbol(self, user_id, symbol):
        self.db.execute("DELETE FROM portfolio where symbol=:symbol and user_id=:user_id", symbol=symbol, user_id=user_id)

    def InsertUserIdAndNameAndSymbolAndShares(self, user_id, name, symbol, shares):
        self.db.execute("INSERT INTO portfolio (user_id, name, symbol, shares) VALUES (:user_id, :name, :symbol, :shares)", user_id=user_id, name=name, symbol=symbol, shares=shares)