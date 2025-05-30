-- SQL skript pro vytvoření databáze pro Test Management App

CREATE DATABASE IF NOT EXISTS test_management_app;
USE test_management_app;

-- 1. Číselník: statusy testů
CREATE TABLE IF NOT EXISTS test_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- 2. Tabulka: uživatelé
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('tester', 'manager', 'admin') NOT NULL DEFAULT 'tester',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabulka: projekty
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 4. Tabulka: testovací scénáře
CREATE TABLE IF NOT EXISTS test_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    steps TEXT,
    expected_result TEXT,
    status_id INT NOT NULL,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (status_id) REFERENCES test_status(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 5. Tabulka: výsledky testů
CREATE TABLE IF NOT EXISTS test_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    test_case_id INT NOT NULL,
    executed_by INT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result ENUM('pass', 'fail', 'blocked', 'not_run') NOT NULL,
    notes TEXT,
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id),
    FOREIGN KEY (executed_by) REFERENCES users(id)
);

-- Pohled: poslední výsledek testu pro každý scénář
CREATE OR REPLACE VIEW v_last_test_result AS
SELECT tc.id AS test_case_id, tc.title, tr.result, tr.executed_at
FROM test_cases tc
LEFT JOIN test_results tr ON tr.id = (
    SELECT id FROM test_results WHERE test_case_id = tc.id ORDER BY executed_at DESC LIMIT 1
);

-- Funkce: počet testů v projektu
DELIMITER //
CREATE FUNCTION get_test_count_by_project(pid INT) RETURNS INT
    DETERMINISTIC
BEGIN
    DECLARE test_count INT;
    SELECT COUNT(*) INTO test_count FROM test_cases WHERE project_id = pid;
    RETURN test_count;
END //
DELIMITER ;

-- Procedura: přidání nového testovacího scénáře
DELIMITER //
CREATE PROCEDURE add_test_case(
    IN p_project_id INT,
    IN p_title VARCHAR(255),
    IN p_description TEXT,
    IN p_steps TEXT,
    IN p_expected_result TEXT,
    IN p_status_id INT,
    IN p_created_by INT
)
BEGIN
    INSERT INTO test_cases (project_id, title, description, steps, expected_result, status_id, created_by)
    VALUES (p_project_id, p_title, p_description, p_steps, p_expected_result, p_status_id, p_created_by);
END //
DELIMITER ;

-- Trigger: automatické nastavení resultu na "Not Run" při vytvoření nového scénáře v test results
DELIMITER //
CREATE TRIGGER trg_set_default_status BEFORE INSERT ON test_results
FOR EACH ROW
BEGIN
    IF NEW.result_id IS NULL THEN
        SET NEW.result_id = (SELECT id FROM test_status WHERE name = 'Not Run' LIMIT 1);
    END IF;
END //
DELIMITER ;

-- Naplnění číselníku statusů
INSERT IGNORE INTO test_status (id, name) VALUES
    (1, 'Not Run'),
    (2, 'In Progress'),
    (3, 'Blocked'),
    (4, 'Passed'),
    (5, 'Failed');
