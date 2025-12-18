-- For Fresh New Data
DROP TABLE IF EXISTS transaction_record, actual_balance, initial_balance, account, category, transaction_type CASCADE;

-- Account Table
CREATE TABLE IF NOT EXISTS account (
	account_id SERIAL PRIMARY KEY,
	account_name VARCHAR(50) UNIQUE NOT NULL
);

-- Insert default accounts
INSERT
	INTO
	account (account_name)
VALUES 
    ('BCA'),
    ('BNI')
ON
CONFLICT DO NOTHING;

-- Initial Balance
CREATE TABLE IF NOT EXISTS initial_balance (
	id SERIAL PRIMARY KEY,
	account_id INT REFERENCES account(account_id),
	balance NUMERIC(15, 2) DEFAULT 0.00
);

-- Insert default values (linking by account_id)
INSERT
	INTO
	initial_balance (
		account_id,
		balance
	)
VALUES 
    (
	(
		SELECT
			account_id
		FROM
			account
		WHERE
			account_name = 'BCA'
	),
	454318.58
),
    (
	(
		SELECT
			account_id
		FROM
			account
		WHERE
			account_name = 'BNI'
	),
	0.00
)
ON
CONFLICT DO NOTHING;


-- Category
CREATE TABLE IF NOT EXISTS category (
	category_id SERIAL PRIMARY KEY,
	category_name VARCHAR(50) UNIQUE NOT NULL
);

-- Insert default categories
INSERT
	INTO
	category (category_name)
VALUES 
    ('Salary'),
    ('Housing'),
    ('Transportation'),
    ('Food'),
    ('Utilities'),
    ('Healthcare'),
    ('Personal Care'),
    ('Entertainment'),
    ('Savings'),
    ('Investments'),
    ('Debt Payments'),
    ('Kids'),
    ('Tax'),
    ('Other')
ON
CONFLICT DO NOTHING;

-- Transaction Type
CREATE TABLE IF NOT EXISTS transaction_type (
	type_id SERIAL PRIMARY KEY,
	type_name VARCHAR(20) UNIQUE NOT NULL
);

-- Insert default types
INSERT
	INTO
	transaction_type (type_name)
VALUES 
    ('Debit'),
    ('Credit')
ON
CONFLICT DO NOTHING;

-- Actual Balance Table
CREATE TABLE IF NOT EXISTS actual_balance (
	id SERIAL PRIMARY KEY,
	account_id INT REFERENCES account(account_id),
	transaction_date DATE NOT NULL,
	amount NUMERIC(15, 2) DEFAULT 0.00
);

-- Insert default value
INSERT
	INTO
	actual_balance (
		account_id,
		transaction_date,
		amount
	)
VALUES (
	(
		SELECT
			account_id
		FROM
			account
		WHERE
			account_name = 'BCA'
	),
	'2025-12-17',
	454318.58
)
ON
CONFLICT DO NOTHING;

-- Transaction Table
CREATE TABLE IF NOT EXISTS transaction_record (
	id SERIAL PRIMARY KEY,
	transaction_date DATE NOT NULL,
	account_id INT REFERENCES account(account_id),
	category_id INT REFERENCES category(category_id),
	type_id INT REFERENCES transaction_type(type_id),
	amount NUMERIC(15, 2) DEFAULT 0.00,
	remark TEXT
);
