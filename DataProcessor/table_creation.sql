CREATE DATABASE IF NOT EXISTS product_recs;

USE product_recs;

DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Recommendation;
DROP TABLE IF EXISTS Rating;
DROP TABLE IF EXISTS Product;
DROP TABLE IF EXISTS Receipt;

CREATE TABLE IF NOT EXISTS User (
  id varchar(255),
  firstName varchar(255),
  lastName varchar(255),
  email varchar(255),
  income float,
  PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS Product
(
  id varchar(255),
  title varchar(255),
  category varchar(255),
  /*This is the estimated price and tax*/
  price float,
  tax float,
  /*imageUrl varchar(255),*/
  PRIMARY KEY (ID)
);

CREATE TABLE  IF NOT EXISTS Rating
(
  userId varchar(255),
  productId varchar(255),
  rating int,
  PRIMARY KEY(productId, userId),
  FOREIGN KEY (productId) 
    REFERENCES Product(id),
  FOREIGN KEY (userId)
    REFERENCES User(id)
);

CREATE TABLE  IF NOT EXISTS Recommendation
(
  userId varchar(255),
  productId varchar(255),
  prediction float,
  PRIMARY KEY(userId, productId),
  FOREIGN KEY (productId) 
    REFERENCES Product(id),
  FOREIGN KEY (userId)
    REFERENCES User(id)
);

CREATE TABLE IF NOT EXISTS Receipt
(
  id varchar(255),
  productId varchar(255),
  userId varchar(255),
  title varchar(255),
  category varchar(255),
  location varchar(255),
  price float,
  tax float,
  PRIMARY KEY (id),
  FOREIGN KEY (productId) 
    REFERENCES Product(id),
  FOREIGN KEY (userId)
    REFERENCES User(id)
);
