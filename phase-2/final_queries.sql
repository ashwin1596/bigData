--1. This query finds the zone in each borough that earned the highest total TotalAmount on each day of the week.
WITH EarningsPerZone AS (
    SELECT 
        l.borough, 
        l.zone, 
        t.dayofweek, 
        SUM(tr.totalamount) AS totalearnings
    FROM trip tr
    JOIN time t ON tr.id = t.tripid
    JOIN location l ON tr.pickuplocation = l.id
    GROUP BY l.borough, l.zone, t.dayofweek
)

SELECT 
    epz.borough, 
    epz.zone, 
    epz.dayofweek, 
    epz.totalearnings
FROM EarningsPerZone epz
WHERE epz.totalearnings = (
    SELECT MAX(totalearnings)
    FROM EarningsPerZone epz2
    WHERE epz2.dayofweek = epz.dayofweek
    AND epz2.borough = epz.borough
)
ORDER BY epz.dayofweek, epz.totalearnings DESC;

--2. This query calculates the average TripDistance and FareAmount grouped by both PaymentType and Ratecode, providing insights into how distance and fare vary by payment and rate type.
select p.description as paymenttype, r.description as ratecode, avg(tr.tripdistance) as avgtripdistance, avg(tr.fareamount) as avgfareamount
from trip tr
join payment p on tr.paymenttype = p.id
join ratecode r on tr.ratecode = r.id
group by p.description, r.description
order by avgfareamount;

--3. Identify the top 10 most profitable trip routes by total revenue.
select originlocation.zone as originzone,
	destlocation.zone as destzone,
	sum(trip.totalamount) as totalrevenue
from trip
join location as originlocation on trip.pickuplocation = originlocation.id
join location as destlocation on trip.dropofflocation = destlocation.id
group by originzone, destzone
order by totalrevenue desc
limit 10;

--4. Analyze trip volume and revenue trends over time.
select date_trunc('month', time.pickupdate) as monthyear,
	count(*) as tripcount,
	sum(trip.totalamount) as totalrevenue,
	avg(trip.tipamount) as avgtipamount
from trip
join time on time.tripid = trip.id
group by monthyear
order by monthyear;

--5. Analyze the impact of congestion surcharges on trip revenue.
select 
	case when trip.congestionsurcharge > 0 then 'with surcharge' else 'no surcharge' end as surchargestatus,
	count(*) as tripcount,
	sum(trip.totalamount) as totalrevenue,
	avg(trip.totalamount) as avgtriprevenue
from trip
group by surchargestatus
order by tripcount desc;
