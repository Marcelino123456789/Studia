-- Studia database schema (MySQL)
-- Converted from the original SQLite schema. Table names, columns, and
-- relationships are unchanged; only the types/syntax are MySQL-compatible.
-- `sqlite_sequence` is SQLite-internal and has no MySQL equivalent, so it
-- is intentionally omitted (AUTO_INCREMENT handles it natively).

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    hash VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    `date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    due_date TEXT
) ENGINE=InnoDB;

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    content TEXT NOT NULL,
    `time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read INT DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE friends (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    friends_name VARCHAR(80) NOT NULL,
    UNIQUE(user_id, friends_name)
) ENGINE=InnoDB;

CREATE TABLE timers (
    user_id INT PRIMARY KEY,
    status TEXT NOT NULL,
    end_time DOUBLE,
    remaining INT
) ENGINE=InnoDB;
