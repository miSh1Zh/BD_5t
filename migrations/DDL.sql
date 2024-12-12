CREATE TABLE usr(
    id SERIAL,
    login VARCHAR(255) NOT NULL,
    hash_password VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL DEFAULT 'customer'
);
ALTER TABLE
    usr ADD PRIMARY KEY(id);
ALTER TABLE
    usr ADD CONSTRAINT usr_login_unique UNIQUE(login);
COMMENT ON TABLE usr IS 'Информация о пользователях';
COMMENT ON COLUMN usr.login IS 'Почта, с которой регистрировался пользователь (логин)'; 
COMMENT ON COLUMN usr.hash_password IS 'Хешированный пароль';
COMMENT ON COLUMN usr.role IS 'Роль пользователя';



CREATE TABLE managers(
    id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    paycheck INT NOT NULL
);
ALTER TABLE
    managers ADD PRIMARY KEY(id);
ALTER TABLE
    managers ADD CONSTRAINT manager_id_foreign FOREIGN KEY(id) REFERENCES usr(id);



CREATE TABLE customers(
    id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(255) NOT NULL
);
ALTER TABLE
    customers ADD PRIMARY KEY(id);
ALTER TABLE
    customers ADD CONSTRAINT customer_phone_unique UNIQUE(phone);
ALTER TABLE
    customers ADD CONSTRAINT customer_id_foreign FOREIGN KEY(id) REFERENCES usr(id);



CREATE TABLE restaurants(
    id SERIAL,
    adress VARCHAR(255) NOT NULL,
    open_hour TIME(0) WITHOUT TIME ZONE NOT NULL DEFAULT '10:00',
    close_hour TIME(0) WITHOUT TIME ZONE NOT NULL DEFAULT '22:00',
    phone VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL
);
ALTER TABLE
    restaurants ADD PRIMARY KEY(id);
ALTER TABLE
    restaurants ADD CONSTRAINT restaurant_adress_unique UNIQUE(adress);
ALTER TABLE
    restaurants ADD CONSTRAINT restaurant_phone_unique UNIQUE(phone);
ALTER TABLE
    restaurants ADD CONSTRAINT restaurant_email_unique UNIQUE(email);



CREATE TABLE orders(
    id SERIAL,
    time TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    bill INT NOT NULL,
    approved BOOLEAN DEFAULT false,
    customer_id INT NOT NULL,
    restaurant_id INT NOT NULL
);
ALTER TABLE
    orders ADD PRIMARY KEY(id);
ALTER TABLE
    orders ADD CONSTRAINT order_restaurant_id_foreign FOREIGN KEY(restaurant_id) REFERENCES restaurants(id);
ALTER TABLE
    orders ADD CONSTRAINT order_customer_id_foreign FOREIGN KEY(customer_id) REFERENCES customers(id);




CREATE TABLE dishes(
    id SERIAL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    price INT NOT NULL
);
ALTER TABLE
    dishes ADD PRIMARY KEY(id);
ALTER TABLE
    dishes ADD CONSTRAINT dish_name_unique UNIQUE(name);



CREATE TABLE events(
    id SERIAL,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    start_datetime TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    duration SMALLINT NOT NULL,
    restaurant_id INT NOT NULL
);
ALTER TABLE
    events ADD PRIMARY KEY(id);
ALTER TABLE
    events ADD CONSTRAINT events_restaurant_id_foreign FOREIGN KEY(restaurant_id) REFERENCES restaurants(id);
COMMENT ON TABLE events IS 'Проводимые в сети ресторанов мероприятия';
COMMENT ON COLUMN events.name IS 'Название мероприятия';
COMMENT ON COLUMN events.description IS 'Описание мероприятия';
COMMENT ON COLUMN events.start_datetime IS 'Начало мероприятия';
COMMENT ON COLUMN events.duration IS 'Продолжительность в минутах';



CREATE TABLE managers_restaurants (
    manager_id INT NOT NULL,
    restaurant_id INT NOT NULL
);
ALTER TABLE
    managers_restaurants ADD PRIMARY KEY(manager_id, restaurant_id);
ALTER TABLE
    managers_restaurants ADD CONSTRAINT managers_restaurants_id_foreign FOREIGN KEY(manager_id) REFERENCES managers(id);
ALTER TABLE
    managers_restaurants ADD CONSTRAINT managers_restaurants_restaurant_id_foreign FOREIGN KEY(restaurant_id) REFERENCES restaurants(id);



CREATE TABLE orders_dishes(
    order_id INT NOT NULL,
    dish_id INT NOT NULL,
    positions_in_order SMALLINT NOT NULL DEFAULT 1
);
ALTER TABLE
    orders_dishes ADD PRIMARY KEY(order_id, dish_id);
ALTER TABLE
    orders_dishes ADD CONSTRAINT orders_dishes_order_id_foreign FOREIGN KEY(order_id) REFERENCES orders(id);
ALTER TABLE
    orders_dishes ADD CONSTRAINT orders_dishes_dish_id_foreign FOREIGN KEY(dish_id) REFERENCES dishes(id);



CREATE TABLE dishes_restaurants(
    dish_id INT NOT NULL,
    restaurant_id INT NOT NULL
);
ALTER TABLE
    dishes_restaurants ADD PRIMARY KEY(dish_id, restaurant_id);
ALTER TABLE
    dishes_restaurants ADD CONSTRAINT dishes_restaurants_restaurant_id_foreign FOREIGN KEY(restaurant_id) REFERENCES restaurants(id);
ALTER TABLE
    dishes_restaurants ADD CONSTRAINT dishes_restaurants_dish_id_foreign FOREIGN KEY(dish_id) REFERENCES dishes(id);


-- (?) процедура добавления заказа ->
CREATE OR REPLACE PROCEDURE make_order(
    p_address VARCHAR(255),
    p_bill INT,
    p_customer_id INT,
    p_dish_list JSONB
)
LANGUAGE plpgsql AS $$
DECLARE
    v_restaurant_id INT;
    v_order_id INT;
    v_dish_id INT;
    v_quantity INT;
BEGIN
    SELECT id INTO v_restaurant_id
    FROM restaurants
    WHERE adress = p_address;

    INSERT INTO orders (bill, customer_id, restaurant_id)
    VALUES (p_bill, p_customer_id, v_restaurant_id)
    RETURNING id INTO v_order_id;

    FOR v_dish_id, v_quantity IN
        SELECT (dish ->> 'dish_id')::INT, (dish ->> 'quanity')::INT
        FROM jsonb_array_elements(p_dish_list) AS dish
    LOOP
        INSERT INTO orders_dishes (order_id, dish_id, positions_in_order)
        VALUES (v_order_id, v_dish_id, v_quantity);
    END LOOP;

EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'An error occurred: %', SQLERRM;
END;
$$;


-- To use trigger, we need a purpose -> orders_log
CREATE TABLE orders_log(
    order_id INT NOT NULL,
    create_time TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    approved_time TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL
);
ALTER TABLE
    orders_log ADD PRIMARY KEY(order_id);
ALTER TABLE
    orders_log ADD CONSTRAINT orders_log_order_id_foreign FOREIGN KEY(order_id) REFERENCES orders(id);



CREATE OR REPLACE FUNCTION log_order_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO 
        orders_log (order_id, create_time, approved_time)
    VALUES 
        (
            OLD.id, 
            OLD.time, 
            NOW()
        );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER logging_orders_after_approvement
AFTER UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION log_order_changes();



CREATE VIEW menu_in_restaurants AS 
SELECT 
    adress, 
    category, 
    name, 
    price,
    dish_id
FROM 
    dishes_restaurants dr
    INNER JOIN restaurants r on r.id = dr.restaurant_id
    INNER JOIN dishes d on d.id = dr.dish_id;


CREATE VIEW events_in_restaurants AS 
SELECT 
    adress, 
    name, 
    start_datetime::DATE as date,
    DATE_PART('hour', start_datetime) as start_hour,
    DATE_PART('hour', start_datetime + duration * INTERVAL '1 minute') as end_hour
FROM 
    events e
    INNER JOIN restaurants r on r.id = e.restaurant_id;


CREATE VIEW bills AS 
WITH 
orders_dishes_named AS (
    SELECT order_id, name
    FROM 
        orders_dishes od 
        INNER JOIN dishes d on d.id = od.dish_id 
),
orders_dishes_named_grouped AS (
    SELECT order_id, array_agg(name) AS dish_list
    FROM orders_dishes_named
    GROUP BY order_id
)
SELECT 
    name,
    adress,
    order_id,
    dish_list,
    bill,
    customer_id
FROM 
    orders_dishes_named_grouped od
    INNER JOIN orders o on o.id = od.order_id
    INNER JOIN restaurants r on r.id = o.restaurant_id
    INNER JOIN customers c on c.id = o.customer_id
WHERE approved = true;


CREATE VIEW chain_statistic AS 
SELECT 
    adress, 
    ROUND(AVG(EXTRACT(epoch FROM approved_time - create_time) / 60.0)) AS avg_approve_time, 
    SUM(bill) AS total_month_income
FROM 
    orders_log ol 
    INNER JOIN orders o on o.id = ol.order_id
    INNER JOIN restaurants r on r.id = o.restaurant_id
WHERE DATE_TRUNC('month', create_time::DATE) = DATE_TRUNC('month', current_date)
GROUP BY adress 
ORDER BY avg_approve_time ASC, total_month_income DESC;


CREATE ROLE customer LOGIN;
GRANT SELECT on restaurants to customer;
GRANT SELECT on customers to customer;
GRANT SELECT on menu_in_restaurants to customer;
GRANT SELECT on events_in_restaurants to customer;
GRANT SELECT, INSERT on bills to customer;
GRANT SELECT, INSERT, UPDATE, DELETE on orders to customer;
GRANT SELECT, INSERT, UPDATE, DELETE on orders_dishes to customer;
-- не прокатило
-- GRANT ALL on PROCEDURE make_order to customer; 




CREATE ROLE manager LOGIN;
GRANT SELECT on managers to manager;
GRANT SELECT on customers to manager;
GRANT SELECT, UPDATE on orders to manager;
GRANT INSERT on orders_log to manager;
GRANT SELECT, UPDATE, INSERT, DELETE on events to manager;
GRANT SELECT, UPDATE, INSERT, DELETE on dishes_restaurants to manager;
GRANT SELECT on restaurants to manager;
GRANT SELECT on managers_restaurants to manager;
