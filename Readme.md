# NYC Taxi Trip Data Analysis

This project presents a comprehensive analysis and database design of the NYC Yellow Taxi trip dataset. It compares relational and document-based models (PostgreSQL & MongoDB), and applies data mining techniques including association rule mining and frequent itemset extraction.

---

## 📦 Dataset Source & Description

- **Source**: NYC Taxi & Limousine Commission (TLC)  
- **Sample Size**: 44M+ trip records (reduced to ~1M for feasibility)  
- **Features**: Pickup/Dropoff times, locations, fare, tip, payment type, passenger count, rate code, vendor ID, etc.

---

## 🧩 Entity-Relationship (ER) Model

The ER model represents the high-level conceptual design of the dataset. It captures the key entities (`Trip`, `Vendor`, `Location`, `Payment`, `RateCode`, and `Time`) and their relationships.

### Highlights:
- `Trip` is the central entity linked to all others via FKs.
- `Time` is modeled as a weak entity for flexible date-time analysis.
- Lookup/reference tables like `Payment`, `Vendor`, `RateCode` promote normalization and consistency.

📌 **ER Diagram:**  
_![ER Diagram](INSERT_PATH_TO_ER_DIAGRAM.png)_

---

## 🧱 Relational Database Schema Design

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

📂 SQL Schema: [`Data_Import/table_creation.sql`](./Data_Import/table_creation.sql)

---

## 🗃️ Data Loading Instructions (SQL)

```bash
# Create tables
psql -U your_user -d your_db -f Data_Import/table_creation.sql

# Load data using COPY or pgAdmin
psql -U your_user -d your_db -f Data_Import/data_load.sql
```

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

📂 MongoDB Script: [`MongoDB/trip_model.json`](./MongoDB/trip_model.json)

---

## 🔍 Query Examples & Performance Tuning

### PostgreSQL:
- Top 5 zones by average fare
- Average trip duration by day of week
- Most common payment types

### MongoDB:
- Aggregations using `$group`, `$project`, `$unwind`
- Geospatial queries on pickup zones

📂 SQL Queries: [`SQL_Queries/analysis_queries.sql`](./SQL_Queries/analysis_queries.sql)

---

## ⚡ Indexing Strategy & Performance Benchmarks

### PostgreSQL:
- Indexes on `PickupLocationID`, `DropoffLocationID`, `PickupDate`, `PaymentID`
- B-Tree and composite indexes improved query times by ~40%

### MongoDB:
- Compound indexes on `pickup.datetime` + `pickup.location.zone`
- Performance monitored via `explain()` and `Atlas profiler`

📂 Benchmark Notebook: [`Benchmarks/index_tuning.ipynb`](./Benchmarks/index_tuning.ipynb)

---

## 🔄 Functional Dependencies & Normalization

- Ensured 3NF/BCNF: e.g.,  
  `Trip → PaymentID`, `PaymentID → PaymentType` ⇒ `Trip → PaymentType`
- Avoided transitive and partial dependencies
- No derived or multivalued attributes in base schema

---

## 🧹 Data Cleaning

- Removed nulls and outliers (`fare_amount <= 0`, unrealistic trip distances)
- Consolidated payment types (`Credit Card`, `CC` → `Credit Card`)
- Added flags like `IsWeekend`, `RushHour` for analysis

📂 Cleaning Script: [`Data_Cleaning/cleaning_script.py`](./Data_Cleaning/cleaning_script.py)

---

## 🛒 Frequent Itemset Mining

Used Apriori to identify co-occurrence patterns between zones and payment types.

- Example: `{Zone=Midtown, Payment=Credit Card} → Frequent set`
- Minimum support threshold: 0.03

📂 Notebook: [`Association_Mining/itemset_analysis.ipynb`](./Association_Mining/itemset_analysis.ipynb)

---

## 🔗 Association Rule Mining

Generated rules such as:

- `If PickupZone=Midtown → likely DropoffZone=Downtown Brooklyn (confidence=0.72)`
- `If PaymentType=Cash → shorter trip distance (confidence=0.61)`

📂 Notebook: [`Association_Mining/rule_mining.ipynb`](./Association_Mining/rule_mining.ipynb)

---

## 🆚 Relational vs Document Database Justification

| Feature              | Relational (PostgreSQL)                     | Document (MongoDB)                        |
|----------------------|---------------------------------------------|-------------------------------------------|
| Normalization        | Fully normalized                           | Embedded & denormalized                  |
| Joins                | Native support with FK                     | Avoided by embedding                     |
| Query Flexibility    | High for complex, multi-table queries      | Great for hierarchical, nested data      |
| Performance          | Better for structured batch analysis       | Better for single document retrieval     |
| Storage              | More efficient due to normalization        | Redundant fields, higher space usage     |
| Use Case Fit         | Ideal for analytical OLAP queries          | Suitable for real-time app backends      |

---

## ▶️ Execution Steps & Folder Structure

```bash
# Clone repo
git clone https://github.com/your-repo/nyc-taxi-analysis.git

# PostgreSQL setup
cd Data_Import
psql -U postgres -d nyc_taxi -f table_creation.sql
psql -U postgres -d nyc_taxi -f data_load.sql

# MongoDB setup
mongoimport --db nyc_taxi --collection trips --file MongoDB/trip_model.json --jsonArray
```

### 📂 Folder Structure
```
├── README.md
├── Data_Import/
│   ├── table_creation.sql
│   └── data_load.sql
├── SQL_Queries/
│   └── analysis_queries.sql
├── MongoDB/
│   └── trip_model.json
├── Benchmarks/
│   └── index_tuning.ipynb
├── Association_Mining/
│   ├── itemset_analysis.ipynb
│   └── rule_mining.ipynb
├── Data_Cleaning/
│   └── cleaning_script.py
├── Diagrams/
│   └── ER_Diagram.png
```

---

## 👨‍💻 Author

Ashwin Kherde  
[LinkedIn](https://www.linkedin.com/in/ashwinkherde) • [GitHub](https://github.com/ashwinkherde)

---