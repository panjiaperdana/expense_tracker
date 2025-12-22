WITH cats AS (
  SELECT array_agg(category_id) AS ids,
         array_agg(category_name) AS names
  FROM category
),
rnd AS (
  SELECT
    g,
    DATE '2025-01-01' + (RANDOM() * 364)::INT AS transaction_date,
    (RANDOM() * (5000000 - 100000) + 100000)::NUMERIC(15,2) AS amount,
    floor(random() * (SELECT count(*) FROM category))::int AS idx
  FROM generate_series(1,500) g
)
INSERT INTO transaction_record (
  transaction_date, account_id, category_id, amount, remark
)
SELECT
  r.transaction_date,
  CASE WHEN r.g % 2 = 0
       THEN (SELECT account_id FROM account WHERE account_name = 'BCA')
       ELSE (SELECT account_id FROM account WHERE account_name = 'BNI')
  END,
  cats.ids[r.idx+1],       -- pick random category_id
  r.amount,
  cats.names[r.idx+1]      -- matching category_name
FROM rnd r, cats;