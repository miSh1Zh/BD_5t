INSERT INTO 
    usr (login, hash_password, role)
VALUES
    (
        'mito',
        '$2b$12$wxdfFhcGccaIeY//zm5vweTpFQ/OxRdw.M6vfkIX.AGzRjl99M5Vi',
        'admin'
    ),
    (
        'supman',
        '$2b$12$p.BJ6Yto2mF.jjxhGGpUwe4dtBdwnaWG087oPzAhi4jjv5lU5dd5y',
        'manager'
    ),
    (
        'ultman',
        '$2b$12$sDaqfvlDBMIvgoWq/bczruX7h/zaAXDRxktBKHOGGu4H8QTofDram',
        'manager'
    ),
    (
        'customan',
        '$2b$12$aqZZEKkJHXWMeo3iv23Zg./eZN8UO0VUOZKMRm0PMKnD5xPnFjlLe',
        'customer'
    );


INSERT INTO 
    managers (id, name, paycheck)
VALUES
    (
        2,
        'Besnov Dmitry Valerevich',
        100000
    ),
    (
        3,
        'Filinova Anastasia Stepanovna',
        70000
    );


INSERT INTO 
    customers (id, name, phone)
VALUES
    (
        4,
        'Zhadnov Mikhail Denisovich',
        '+7 967 258-75-39'
    );


INSERT INTO
    restaurants (adress, phone, email)
VALUES 
    (
        'Tverskaya Street 45, Moscow',
        '+7 495 123-45-67',
        'shoko1@mail.ru'
    ),
    (
        'Lenin Street 10, Moscow',
        '+7 495 678-90-12',
        'shoko2@mail.ru'
    );


INSERT INTO
    managers_restaurants (manager_id, restaurant_id)
VALUES
    (
        2,
        1
    ),
    (
        3,
        1
    ),
    (
        2,
        2
    );


INSERT INTO 
    events (name, description, start_datetime, duration, restaurant_id)
VALUES
    (
        'New 2025 Year',
        'Merry Cristmas, dear viewers of this message! It is an invitation to the event in Tverskaya Street 45, Moscow restaurant',
        '2024-12-31 20:00:00',
        180,
        1
    ),
    (
        'New 2025 Year',
        'Merry Cristmas, dear viewers of this message! It is an invitation to the event in Lenin Street 10, Moscow restaurant',
        '2024-12-31 20:00:00',
        180,
        2
    ),
    (
        'День Рождения директора',
        'Директор нашей сети приглашает Вас на свой День Рождения',
        '2024-12-07 15:00:00',
        240,
        1
    );


INSERT INTO
    dishes (name, category, price)
VALUES
    (
        'Omelet with vegetables',
        'Breakfasts',
        370
    ),
    (
        'Pancakes with salmon',
        'Breakfasts',
        450
    ),
    (
        'Brioche with salmon',
        'Breakfasts',
        590
    ),
    (
        'Oat porridge with bacon and egg',
        'Breakfasts',
        390
    ),
    (
        'Rice porridge',
        'Breakfasts',
        190
    ),
    (
        'Carbonara',
        'Main dishes',
        550
    ),
    (
        'Lasagna',
        'Main dishes',
        590
    ),
    (
        'Ratatouille',
        'Main dishes',
        290
    ),
    (
        'Beef Stroganoff with mashed potatoes',
        'Main dishes',
        490
    ),
    (
        'Seafood in cream sauce',
        'Main dishes',
        570
    ),
    (
        'Chicken soup with egg',
        'Soups',
        290
    ),
    (
        'Borscht with beef',
        'Soups',
        350
    ),
    (
        'Pumpkin cream soup',
        'Soups',
        370
    ),
    (
        'Cream soup with champignons',
        'Soups',
        350
    ),
    (
        'Cheese cream soup',
        'Soups',
        320
    ),
    (
        'Caesar salad with chicken',
        'Salads',
        490
    ),
    (
        'Seafood salad',
        'Salads',
        590
    ),
    (
        'Salad with hummus and artichokes',
        'Salads',
        490
    ),
    (
        'Greek salad',
        'Salads',
        390
    ),
    (
        'Tea with honey and cinnamon',
        'Hot drinks',
        250
    ),
    (
        'Cappuccino',
        'Hot drinks',
        350
    ),
    (
        'Flat-white',
        'Hot drinks',
        370
    ),
    (
        'Filter coffee',
        'Hot drinks',
        295
    );


INSERT INTO
    dishes_restaurants (dish_id, restaurant_id)
VALUES
    (
        3,
        1
    ),
    (
        2,
        2
    ),
    (
        1,
        1
    ),
    (
        1,
        2
    ),
    (
        4,
        1
    ),
    (
        4,
        2
    ),
    (
        5,
        1
    ),
    (
        5,
        2
    ),
    (
        6,
        2
    ),
    (
        7,
        2
    ),
    (
        8,
        1
    ),
    (
        9,
        1
    ),
    (
        9,
        2
    ),
    (
        10,
        1
    ),
    (
        11,
        1
    ),
    (
        11,
        2
    ),
    (
        12,
        1
    ),
    (
        12,
        2
    ),
    (
        13,
        1
    ),
    (
        14,
        2
    ),
    (
        15,
        1
    ),
    (
        16,
        1
    ),
    (
        16,
        2
    ),
    (
        17,
        1
    ),
    (
        18,
        1
    ),
    (
        19,
        2
    ),
    (
        20,
        1
    ),
    (
        20,
        2
    ),
    (
        21,
        1
    ),
    (
        21,
        2
    ),
    (
        22,
        1
    ),
    (
        22,
        2
    ),
    (
        23,
        1
    ),
    (
        23,
        2
    );


SELECT name, paycheck, ARRAY_AGG(adress) AS adresses
            FROM 
                managers m
                INNER JOIN managers_restaurants mr on mr.manager_id = m.id
                INNER JOIN restaurants r on r.id = mr.restaurant_id
            GROUP BY name, paycheck;