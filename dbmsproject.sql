CREATE DATABASE IF NOT EXISTS freelancer_db;
USE freelancer_db;

-- USERS
CREATE TABLE users (
    user_id    INT AUTO_INCREMENT PRIMARY KEY,
    full_name  VARCHAR(100) NOT NULL,
    email      VARCHAR(150) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    role       ENUM('client','freelancer','admin') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- PROJECTS
CREATE TABLE projects (
    project_id  INT AUTO_INCREMENT PRIMARY KEY,
    client_id   INT NOT NULL,
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    budget      DECIMAL(10,2) NOT NULL,
    deadline    DATE,
    status      ENUM('open','in_progress','completed','cancelled') DEFAULT 'open',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES users(user_id)
);

-- BIDS
CREATE TABLE bids (
    bid_id        INT AUTO_INCREMENT PRIMARY KEY,
    project_id    INT NOT NULL,
    freelancer_id INT NOT NULL,
    amount        DECIMAL(10,2) NOT NULL,
    proposal      TEXT,
    status        ENUM('pending','accepted','rejected') DEFAULT 'pending',
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id)    REFERENCES projects(project_id),
    FOREIGN KEY (freelancer_id) REFERENCES users(user_id)
);

-- CONTRACTS
CREATE TABLE contracts (
    contract_id   INT AUTO_INCREMENT PRIMARY KEY,
    project_id    INT NOT NULL UNIQUE,
    freelancer_id INT NOT NULL,
    client_id     INT NOT NULL,
    agreed_amount DECIMAL(10,2) NOT NULL,
    start_date    DATE,
    status        ENUM('active','completed','disputed') DEFAULT 'active',
    FOREIGN KEY (project_id)    REFERENCES projects(project_id),
    FOREIGN KEY (freelancer_id) REFERENCES users(user_id),
    FOREIGN KEY (client_id)     REFERENCES users(user_id)
);

-- PAYMENTS
CREATE TABLE payments (
    payment_id   INT AUTO_INCREMENT PRIMARY KEY,
    contract_id  INT NOT NULL,
    amount       DECIMAL(10,2) NOT NULL,
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    method       ENUM('credit_card','bank_transfer','wallet') DEFAULT 'wallet',
    status       ENUM('pending','completed','failed') DEFAULT 'pending',
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id)
);

-- REVIEWS
CREATE TABLE reviews (
    review_id   INT AUTO_INCREMENT PRIMARY KEY,
    contract_id INT NOT NULL,
    reviewer_id INT NOT NULL,
    reviewee_id INT NOT NULL,
    rating      TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id),
    FOREIGN KEY (reviewer_id) REFERENCES users(user_id),
    FOREIGN KEY (reviewee_id) REFERENCES users(user_id)
);

-- STORED PROCEDURE: place_bid
DELIMITER $$
CREATE PROCEDURE place_bid(IN p_project_id INT, IN p_freelancer_id INT,
                            IN p_amount DECIMAL(10,2), IN p_proposal TEXT)
BEGIN
  INSERT INTO bids (project_id, freelancer_id, amount, proposal)
  VALUES (p_project_id, p_freelancer_id, p_amount, p_proposal);
END$$

-- STORED PROCEDURE: accept_bid
CREATE PROCEDURE accept_bid(IN p_bid_id INT)
BEGIN
  DECLARE v_pid INT; DECLARE v_fid INT;
  DECLARE v_cid INT; DECLARE v_amt DECIMAL(10,2);
  SELECT b.project_id, b.freelancer_id, b.amount, p.client_id
  INTO v_pid, v_fid, v_amt, v_cid
  FROM bids b JOIN projects p ON b.project_id=p.project_id WHERE b.bid_id=p_bid_id;
  UPDATE bids SET status='rejected' WHERE project_id=v_pid;
  UPDATE bids SET status='accepted' WHERE bid_id=p_bid_id;
  UPDATE projects SET status='in_progress' WHERE project_id=v_pid;
  INSERT INTO contracts (project_id,freelancer_id,client_id,agreed_amount,start_date)
  VALUES (v_pid, v_fid, v_cid, v_amt, CURDATE());
END$$

-- STORED PROCEDURE: make_payment
CREATE PROCEDURE make_payment(IN p_contract_id INT,
                               IN p_amount DECIMAL(10,2), IN p_method VARCHAR(20))
BEGIN
  INSERT INTO payments (contract_id, amount, method, status)
  VALUES (p_contract_id, p_amount, p_method, 'completed');
  UPDATE contracts SET status='completed' WHERE contract_id=p_contract_id;
  UPDATE projects p JOIN contracts c ON p.project_id=c.project_id
  SET p.status='completed' WHERE c.contract_id=p_contract_id;
END$$
DELIMITER ;

-- TRIGGER
DELIMITER $$
CREATE TRIGGER before_bid_insert BEFORE INSERT ON bids
FOR EACH ROW
BEGIN
  DECLARE v_status VARCHAR(20);
  SELECT status INTO v_status FROM projects WHERE project_id=NEW.project_id;
  IF v_status != 'open' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Cannot bid on a non-open project.';
  END IF;
END$$
DELIMITER ;

-- VIEWS
CREATE VIEW open_projects_view AS
SELECT p.project_id, p.title, p.budget, p.deadline, u.full_name AS client_name
FROM projects p JOIN users u ON p.client_id=u.user_id WHERE p.status='open';

CREATE VIEW freelancer_ratings_view AS
SELECT u.user_id, u.full_name,
       ROUND(AVG(r.rating),1) AS avg_rating, COUNT(*) AS total_reviews
FROM users u JOIN reviews r ON u.user_id=r.reviewee_id GROUP BY u.user_id;

-- SAMPLE DATA
INSERT INTO users (full_name,email,password,role) VALUES
('Alice Johnson','alice@mail.com','pass123','client'),
('Bob Smith','bob@mail.com','pass123','freelancer'),
('Carol White','carol@mail.com','pass123','freelancer'),
('David Brown','david@mail.com','pass123','client');

INSERT INTO projects (client_id,title,description,budget,deadline) VALUES
(1,'Portfolio Website','Build a personal portfolio',5000,'2025-06-30'),
(1,'Data Dashboard','Pandas + Matplotlib dashboard',8000,'2025-07-15'),
(4,'E-commerce API','Flask REST API with MySQL',12000,'2025-08-01');

INSERT INTO bids (project_id,freelancer_id,amount,proposal) VALUES
(1,3,4500,'I can deliver a stunning portfolio in 2 weeks.'),
(1,2,4800,'Experienced web designer, on-time delivery.'),
(2,2,7500,'Python expert, 3 years data analysis experience.');