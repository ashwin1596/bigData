-- Location table creation
CREATE TABLE Location (
  ID INT PRIMARY KEY,
  Borough VARCHAR,
  Zone VARCHAR
);

-- RateCode table creation
CREATE TABLE RateCode (
  ID INT PRIMARY KEY,
  Description VARCHAR
);

-- Payment table creation
CREATE TABLE Payment (
  ID INT PRIMARY KEY,
  Description VARCHAR
);

-- Vendor table creation
CREATE TABLE Vendor (
  ID INT PRIMARY KEY,
  Name VARCHAR
);

-- Time table creation
CREATE TABLE Time (
  TripID INT,
  PickUpDate DATE,
  PickUpTime TIME,
  DropOffDate DATE,
  DropOffTime TIME,
  DayOfWeek INT,
  IsWeekend BOOLEAN
);

-- Trip table creation
CREATE TABLE Trip (
  ID INT PRIMARY KEY,
  PassengerCount INT,
  TripDistance NUMERIC,
  StoreAndFwdFlag VARCHAR,
  FareAmount NUMERIC,
  Extra NUMERIC,
  MTATax NUMERIC,
  ImprovementSurcharge INT,
  TipAmount NUMERIC,
  TollsAmount NUMERIC,
  TotalAmount NUMERIC,
  CongestionSurcharge NUMERIC,
  AirportFee NUMERIC,
  Vendor INT,
  PaymentType INT,
  Ratecode INT,
  PickUpLocation INT,
  DropOffLocation INT
);

-- Loading data....

-- Load data into Location table
\copy location FROM C:\Sem4\CSCI620\Project\processed_data\borough_info.csv CSV DELIMITER ',' HEADER;

-- Load data into RateCode table
\copy ratecode FROM C:\Sem4\CSCI620\Project\processed_data\ratecode_info.csv CSV DELIMITER ',' HEADER;

-- Load data into Payment table
\copy payment FROM C:\Sem4\CSCI620\Project\processed_data\payment_info.csv CSV DELIMITER ',' HEADER;

-- Load data into Vendor table
\copy vendor FROM C:\Sem4\CSCI620\Project\processed_data\vendor_info.csv CSV DELIMITER ',' HEADER;

-- Load data into Time table
\copy time FROM C:\Sem4\CSCI620\Project\processed_data\time_info.csv CSV DELIMITER ',' HEADER;

-- Load data into Trip table
\copy trip FROM C:\Sem4\CSCI620\Project\processed_data\trip_info.csv CSV DELIMITER ',' HEADER;

-- Add in foreign keys

-- Add foreign key to Trip table
ALTER TABLE time
ADD CONSTRAINT fk_tripID
FOREIGN KEY (TripID) REFERENCES trip(ID);

-- Add foreign keys to Trip table
ALTER TABLE trip
ADD CONSTRAINT fk_pickup_location
FOREIGN KEY (PickUpLocation) REFERENCES location(ID);

ALTER TABLE trip
ADD CONSTRAINT fk_dropoff_location
FOREIGN KEY (DropOffLocation) REFERENCES location(ID);

-- alter ratecode due to unkown code
INSERT INTO ratecode (id, description) VALUES (99, 'unknown');

ALTER TABLE trip
ADD CONSTRAINT fk_ratecode
FOREIGN KEY (Ratecode) REFERENCES ratecode(ID);

ALTER TABLE trip
ADD CONSTRAINT fk_paymenttype
FOREIGN KEY (PaymentType) REFERENCES payment(id);

ALTER TABLE trip
ADD CONSTRAINT fk_vendor
FOREIGN KEY (Vendor) REFERENCES vendor(id);




