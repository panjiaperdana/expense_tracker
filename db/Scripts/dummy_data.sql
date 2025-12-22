WITH rnd AS (
  SELECT
    g,
    (floor(random() * 14) + 1)::int AS category_id,
    DATE '2025-01-01' + (RANDOM() * 364)::INT AS transaction_date,
    (RANDOM() * (5000000 - 100000) + 100000)::NUMERIC(15,2) AS amount
  FROM generate_series(1,500) g
)
INSERT INTO transaction_record (
  transaction_date, account_id, category_id, type_id, amount, remark
)
SELECT
  r.transaction_date,
  CASE WHEN r.g % 2 = 0
       THEN (SELECT account_id FROM account WHERE account_name = 'BCA')
       ELSE (SELECT account_id FROM account WHERE account_name = 'BNI')
  END,
  r.category_id,
  CASE 
    WHEN r.category_id IN (1, 2) THEN 1   -- ✅ Salary or Reimburstment → type_id = 1
    ELSE 2                                -- all others → type_id = 2
  END AS type_id,
  r.amount,
  CASE r.category_id
    WHEN 1 THEN 'Monthly salary'
    WHEN 2 THEN 'Reimburstment'        -- updated remark for category_id 2
    WHEN 3 THEN 'Transportation cost'
    WHEN 4 THEN 'Groceries'
    WHEN 5 THEN 'Electric bill'
    WHEN 6 THEN 'Doctor visit'
    WHEN 7 THEN 'Haircut'
    WHEN 8 THEN 'Movie night'
    WHEN 9 THEN 'Savings deposit'
    WHEN 10 THEN 'Stock investment'
    WHEN 11 THEN 'Loan repayment'
    WHEN 12 THEN 'Kids tuition'
    WHEN 13 THEN 'Tax payment'
    ELSE 'Miscellaneous expense'
  END AS remark
FROM rnd r;