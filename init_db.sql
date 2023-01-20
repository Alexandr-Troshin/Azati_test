create schema orders_db authorization azati_user;

ALTER DATABASE orders_db SET search_path TO orders_db;

CREATE TABLE if not exists orders_db.orders (
"id" serial primary key not null,
"user" integer not null,
-- "user_name" text not null,
"stock" text not null,
"order_type" text not null,
"shares" integer not null,
"price_per_share" real not null,
"order_dttm" timestamp not null);

CREATE TABLE if not exists orders_db.transactions (
"id" serial primary key not null,
"stock" text not null,
"shares" integer not null,
"price_per_share" real not null,
"buyer_name" text not null,
"seller_name" text not null,
"trans_dttm" timestamp not null);


CREATE TABLE if not exists orders_db.trans_last_order (
"id" Integer not null,
"user" integer not null,
-- "user_name" text not null,
"stock" text not null,
"order_type" text not null,
"shares" integer not null,
"price_per_share" real not null,
"sum_shares" integer,
"order_dttm" timestamp not null);

CREATE TABLE if not exists orders_db.orders_log (
"id" Integer not null,
"user" integer not null,
-- "user_name" text not null,"user_name" text not null,
"stock" text not null,
"order_type" text not null,
"shares" integer not null,
"price_per_share" real not null,
"order_dttm" timestamp not null,
"order_action" text not null);

-- функция для триггера

CREATE OR REPLACE FUNCTION orders_db.fn_update_transaction()
  RETURNS trigger AS
$$
BEGIN

    insert into orders_db.orders_log(id, user_name, stock, order_type, shares, price_per_share, order_dttm, order_action)
    VALUES (NEW.id, NEW.user_name, NEW.stock, NEW.order_type, NEW.shares, NEW.price_per_share, NEW.order_dttm, 'put');

	insert into orders_db.trans_last_order
		SELECT id, user_name, stock, order_type, shares, price_per_share, sum_shares, order_dttm
			FROM
				(SELECT 	id, user_name, stock, order_type, shares, price_per_share, order_dttm,
							SUM(shares) OVER (ORDER BY order_sign*price_per_share desc, order_dttm) as sum_shares,
							order_sign
				FROM
					(	SELECT 	id, user_name, stock, order_type, shares, price_per_share, order_dttm,
								CASE 	WHEN order_type = 'SELL' THEN -1
										ELSE 1 END as order_sign
						FROM orders_db.orders
						WHERE 	order_type != NEW.order_type and
								stock = NEW.stock and user_name != new.user_name
					) t1
				) t2
			WHERE 	order_sign*price_per_share >= order_sign*NEW.price_per_share and
					sum_shares <= NEW.shares + shares;



---- 1 block
	Insert into orders_db.transactions(stock, shares, price_per_share, buyer_name, seller_name, trans_dttm)
	SELECT 	stock,
			CASE 	WHEN sum_shares <= NEW.shares THEN shares
					ELSE NEW.shares - sum_shares + shares  END,
			(price_per_share + NEW.price_per_share)/2 as trans_price,
			CASE 	WHEN NEW.order_type = 'SELL' THEN user_name
					ELSE NEW.user_name END,
			CASE 	WHEN NEW.order_type = 'SELL' THEN NEW.user_name
					ELSE user_name END,
			now()
	FROM orders_db.trans_last_order;


---- 2 block


	update orders_db.orders
		set shares = 	CASE 	WHEN (id = (SELECT id FROM orders_db.trans_last_order WHERE sum_shares > new.shares))
									THEN ((SELECT sum_shares FROM orders_db.trans_last_order WHERE sum_shares > new.shares) - new.shares)
								WHEN (id in (SELECT id FROM orders_db.trans_last_order WHERE sum_shares <= new.shares))
									THEN -1
								ELSE shares
						END
		where id in (SELECT id FROM orders_db.trans_last_order);

	update orders_db.orders
		set shares = 	CASE 	WHEN ((SELECT max(sum_shares) FROM orders_db.trans_last_order) < NEW.shares)
									THEN (NEW.shares - (SELECT max(sum_shares) FROM orders_db.trans_last_order))
								WHEN ((SELECT max(sum_shares) FROM orders_db.trans_last_order) is null)
									then shares
								ELSE -1
						END
		where id = (SELECT max(id) FROM orders_db.orders);

	delete from orders_db.trans_last_order;

---- 3 block

	delete from orders_db.orders
		where shares = -1;

	RETURN new;
END;
$$
LANGUAGE 'plpgsql';

-----  конец функции


CREATE trigger  update_transaction
AFTER INSERT ON orders_db.orders
for each row
EXECUTE PROCEDURE orders_db.fn_update_transaction();

--- функция для логгирования удаления ордера

CREATE OR REPLACE FUNCTION orders_db.fn_log_delete_order()
  RETURNS trigger AS
$$
BEGIN
    insert into orders_db.orders_log(id, user_name, stock, order_type, shares, price_per_share, order_dttm, order_action)
    VALUES (OLD.id, OLD.user_name, OLD.stock, OLD.order_type, OLD.shares, OLD.price_per_share, OLD.order_dttm, 'delete');

	RETURN new;
END;
$$
LANGUAGE 'plpgsql';

CREATE trigger  log_delete_order
AFTER DELETE ON orders_db.orders
for each row
WHEN (OLD.shares != -1)
EXECUTE PROCEDURE orders_db.fn_log_delete_order();
