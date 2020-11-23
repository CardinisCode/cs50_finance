class HistoryRepository:
    def __init__(self, db):
        self.db = db

    def getTransactionHistoryByUserId(self, user_id):
        return self.db.execute("SELECT * FROM history WHERE user_id = :user_id", user_id=user_id)

    def InsertTransactionDetails(self, user_id, symbol, price, value, date, shares, trans_type):
        self.db.execute("INSERT INTO history (user_id, symbol, stock_price, purchase_value, date, shares, trans_type) VALUES (:user_id, :symbol, :price, :purchase_value, :date, :shares, :trans_type)", user_id=user_id, symbol=symbol, price=price, purchase_value=value, date=date, shares=shares, trans_type=trans_type)

    def updateUserBalanceByUserId(user_id, balance):
        self.db.execute("UPDATE users SET cash = :balance WHERE id = :user_id", balance=balance, user_id=user_id)
