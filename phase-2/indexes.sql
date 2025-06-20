-- 1.
-- Tried
create index time_dayofweek_idx on time (dayofweek);
create index location_borough_zone_idx on location (borough, zone);
create index trip_pul_idx on trip (pickuplocation);
create index time_tripid_dayofweek_idx on time (tripid, dayofweek);

-- Worked
create index time_tripid_dayofweek_idx on time (tripid, dayofweek);

-- 2.
-- Tried
create index trip_ratecode_idx on trip (ratecode);
create index trip_paymenttype_idx on trip (paymenttype);
create index ratecode_id_desc_idx on ratecode (id, description);
create index payment_id_desc_idx on payment (id, description);
create index trip_pttype_rtcode_fare_dist_idx on trip (paymenttype, ratecode, tripdistance, fareamount);
-- None worked

--3.
-- Tried
create index trip_puloc_idx on trip (pickuplocation);
create index trip_dloc_idx on trip (dropofflocation);
create index trip_puloc_dloc_idx on trip (pickuplocation, dropofflocation);
create index location_zone_idx on location (zone);
create index location_id_zone_idx on location (id, zone);
create index trip_totalamount_idx on trip (totalamount);
-- None worked

--4.
-- tried
create index time_tripid_idx on time (tripid);
create index time_tripid_pickupdate_idx on time (tripid, pickupdate);
--worked
create index time_tripid_pickupdate_idx on time (tripid, pickupdate);

--5.
-- tried
create index trip_totalamount_idx on trip (totalamount);
create index trip_congestionsurcharge_idx on trip (congestionsurcharge);
-- None worked

