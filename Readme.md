# NYC Taxi Trip Data Analysis

## Overview
With the exponential growth in urban transportation data, analyzing and modeling taxi trip records can offer valuable insights for transit planning, policy-making, and operational optimization. This project focuses on a large-scale analysis of the NYC Yellow Taxi Trip dataset, leveraging both relational (PostgreSQL) and document-based (MongoDB) database paradigms. It encompasses end-to-end data handling — from ER modeling, schema normalization, and performance tuning to data mining techniques such as frequent itemset and association rule mining — to uncover actionable trends in trip behavior, payment preferences, and spatial-temporal patterns.

---

## Objective
The primary goal of this project is to design, implement, and compare relational and document-oriented data models for the NYC Taxi dataset in order to:

- Construct normalized schemas and enforce referential integrity for OLAP-style analytical queries.

- Design an efficient document model for flexible, real-time data access.

- Evaluate query performance and indexing strategies across both systems.

- Apply data mining techniques (Apriori, association rule mining) to extract frequent co-occurrence patterns between trip zones, payment types, and time-based factors.

- Derive meaningful insights for urban mobility, such as trip hotspots, fare distribution, and temporal usage trends, while showcasing the trade-offs between different database architectures.

---

## Dataset Source & Description

- **Source**: NYC Taxi & Limousine Commission (TLC)  
- **Sample Size**: 44M+ trip records (reduced to ~1M for feasibility)  
- **Features**: Pickup/Dropoff times, locations, fare, tip, payment type, passenger count, rate code, vendor ID, etc.

---

## Entity-Relationship (ER) Model

The ER model represents the high-level conceptual design of the dataset. It captures the key entities (`Trip`, `Vendor`, `Location`, `Payment`, `RateCode`, and `Time`) and their relationships.

### Highlights:
- `Trip` is the central entity linked to all others via FKs.
- `Time` is modeled as a weak entity for flexible date-time analysis.
- Lookup/reference tables like `Payment`, `Vendor`, `RateCode` promote normalization and consistency.

**ER Diagram:**  
_![ER Diagram](https://github.com/ashwin1596/bigData/blob/main/ER_Diagram.png)_

---

## Relational Database Schema Design

### Key Design Goals:
- **Normalization** up to 3NF or BCNF
- Efficient for OLAP-style queries
- Avoid redundancy and anomalies

### Tables & Attributes:
- `Trip(ID, VendorID, PaymentID, RateCodeID, PickupLocationID, DropoffLocationID, PassengerCount, TripDistance, FareAmount, TipAmount, TotalAmount, ...)`
- `Time(TripID, PickupDate, PickupTime, DropoffDate, DropoffTime, DayOfWeek, IsWeekend)`
- `Location(ID, Borough, Zone)`
- `Vendor(ID, Description)`
- `Payment(ID, Description)`
- `RateCode(ID, Description)`

### Keys & Constraints:
- Surrogate `ID` keys for dimension tables
- Foreign key relationships with `ON DELETE CASCADE`
- Referential integrity enforced for joins and aggregations

**Relational model:**  
_![R Diagram](https://github.com/ashwin1596/bigData/blob/main/Relational_Model.png)_

📂 SQL Schema: [`Phase-1/Data_Import/table_creation.sql`](./Phase-1/Data_Import/table_creation.sql)

---

## Data Loading Instructions (SQL)

1. Store raw CSV files in `Phase-1/Data_Import/raw_data/`
2. Run:  
   ```bash
   python3 DataReader/load_from_kaggle.py

3. Execute SQL:
   ```bash
   psql -f DataReader/table_creation.sql

---

## 📄 Document-Oriented Model (MongoDB)

The document model embeds key information within a `trip` collection, where each document includes vendor, payment, location, and time data.

### Sample Document:
```json
{
  "trip_id": 12345,
  "vendor": "CMT",
  "pickup": {
    "datetime": "2023-02-01T10:30:00",
    "location": {
      "borough": "Manhattan",
      "zone": "Midtown Center"
    }
  },
  "dropoff": {
    "datetime": "2023-02-01T10:50:00",
    "location": {
      "borough": "Brooklyn",
      "zone": "Downtown Brooklyn"
    }
  },
  "fare": 20.5,
  "tip": 4.0,
  "payment_type": "Credit Card"
}
```

📂 MongoDB Script: [`Phase-2/load_to_mongo.py`](./Phase-2/load_to_mongo.py)

---

## Query Examples & Performance Tuning

### PostgreSQL:
- Top 5 zones by average fare
- Average trip duration by day of week
- Most common payment types

### MongoDB:
- Aggregations using `$group`, `$project`, `$unwind`
- Geospatial queries on pickup zones

📂 SQL Queries: [`Phase-2/final_queries.sql`](Phase-2/final_queries.sql)

---

## Indexing Strategy & Performance Benchmarks

### PostgreSQL:
- Indexes on `PickupLocationID`, `DropoffLocationID`, `PickupDate`, `PaymentID`
- B-Tree and composite indexes improved query times by ~40%

### MongoDB:
- Compound indexes on `pickup.datetime` + `pickup.location.zone`
- Performance monitored via `explain()` and `Atlas profiler`

📂 Index creation: [`Phase-2/indexes.sql`](Phase-2/indexes.sql)

---

## Functional Dependencies & Normalization

- Ensured 3NF/BCNF: e.g.,  
  `Trip → PaymentID`, `PaymentID → PaymentType` ⇒ `Trip → PaymentType`
- Avoided transitive and partial dependencies
- No derived or multivalued attributes in base schema

📂 FD Discovery: [`Phase-2/get_functional_dependencies.py`](Phase-2/get_functional_dependencies.py)

---

## Data Cleaning

- Removed nulls and outliers (`fare_amount <= 0`, unrealistic trip distances)
- Consolidated payment types (`Credit Card`, `CC` → `Credit Card`)
- Added flags like `IsWeekend`, `RushHour` for analysis

📂 Cleaning Script: [`Phase-3/clean_data.py`](Phase-3/clean_data.py)

---

## Frequent Itemset Mining

Used Apriori to identify co-occurrence patterns between zones and payment types.

- Example: `{Zone=Midtown, Payment=Credit Card} → Frequent set`
- Minimum support threshold: 0.03

📂 Preprocess: [`Phase-3/preprocess.py`](Phase-3/preprocess.py)
📂 Mining: [`Phase-3/itemset_mining.py`](Phase-3/itemset_mining.py)

📂 Mined Rules: [`Phase-3/[rules_2.txt, rules_3.txt, rules_4.txt]`]

---

## Association Rule Mining

Generated rules such as:

- `If PickupZone=Midtown → likely DropoffZone=Downtown Brooklyn (confidence=0.72)`
- `If PaymentType=Cash → shorter trip distance (confidence=0.61)`

📂 Notebook: [`Phase-3/association_rules.py`](Phase-3/association_rules.py)

---

## Relational vs Document Database Justification

| Feature              | Relational (PostgreSQL)                     | Document (MongoDB)                        |
|----------------------|---------------------------------------------|-------------------------------------------|
| Normalization        | Fully normalized                           | Embedded & denormalized                  |
| Joins                | Native support with FK                     | Avoided by embedding                     |
| Query Flexibility    | High for complex, multi-table queries      | Great for hierarchical, nested data      |
| Performance          | Better for structured batch analysis       | Better for single document retrieval     |
| Storage              | More efficient due to normalization        | Redundant fields, higher space usage     |
| Use Case Fit         | Ideal for analytical OLAP queries          | Suitable for real-time app backends      |

---

## Execution Steps & Folder Structure

### Load data
python3 DataReader/load_from_kaggle.py
psql -f DataReader/table_creation.sql

### Clean data
python3 Phase-3/clean_data.py

### Preprocess for mining
python3 Phase-3/preprocess.py

### Frequent itemsets
python3 Phase-3/itemset_mining.py

### Association rules
python3 Phase-3/association_rules.py

---

### 📂 Folder Structure
```
│   Readme.md
│   ER_Diagram.png
│   Relational_Model.png
│
├───DataReader/
│   ├───load_from_kaggle.py
│   └───table_creation.sql
├───Phase-1/
│   └───Data_Import/
│       ├───load_from_kaggle.py
│       └───table_creation.sql
├───phase-2/
│   ├───get_functional_dependencies.py
│   ├───final_queries.sql
│   └───indexes.sql
└───Phase-3/
    ├───clean_data.py
    ├───preprocess.py
    ├───itemset_mining.py
    └───association_rules.py
```
