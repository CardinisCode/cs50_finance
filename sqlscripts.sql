CREATE TABLE 'history' (
    'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    'user_id' INTEGER NOT NULL, 
    'symbol' TEXT NOT NULL, 
    'stock_price' FLOAT NOT NULL, 
    'purchase_value' FLOAT NOT NULL, 
    'date' DATETIME NOT NULL 
);

CREATE UNIQUE INDEX 'purchase_id' 
ON "history" ("id");

"INSERT INTO history (user_id, symbol, stock_price, purchase_value)
VALUES (user_id, symbol, price, purchase_value)", 

/* 1, 3, Apple Inc., AAPL, 100 */
/* 2, 2, Apple Inc., AAPL, 2 */

CREATE TABLE 'portfolio' (
    'id' INTEGER PRIMARY KEY AUTOINCREMENT, 
    'user_id' INTEGER NOT NULL, 
    'name' TEXT NOT NULL,
    'symbol' TEXT NOT NULL, 
    'shares' INTEGER NOT NULL
);

CREATE UNIQUE INDEX 'id' 
ON "portfolio" ("id");


SELECT * FROM portfolio INNER JOIN users ON users.id = portfolio.user_id WHERE id = :user_id", user_id=user_id)

DELETE FROM  portfolio  where  id = 1;

INSERT INTO portfolio (user_id, name, symbol, shares) VALUES (4, "Apple, Inc.", "AAPL", 2);

DELETE FROM table_name WHERE condition;

UPDATE users SET cash = :balance WHERE id = :user_id", balance=balance, user_id=user_id)