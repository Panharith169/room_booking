CREATE DATABASE room_booking;
USE room_booking;mysql -u root -h localhost -P 3307

CREATE TABLE accounts_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(254) NOT NULL UNIQUE,
    student_id VARCHAR(20) NOT NULL UNIQUE,
    phone_number VARCHAR(15) NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    password VARCHAR(128) NOT NULL,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login DATETIME,
    date_joined DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);