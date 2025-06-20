-- This query calculates the total FareAmount for each day of the week across all trips.
select t.dayofweek, sum(tr.fareamount) as totalfareamount
from trip tr
join time t on tr.id = t.tripid
group by t.dayofweek
order by t.dayofweek;

-- This query finds the average TipAmount for each Borough where passengers were picked up.
select l.borough, avg(tr.tipamount) as avgtipamount
from trip tr
join location l on tr.pickuplocation = l.id
group by l.borough
order by avgtipamount desc;

-- This query shows the count of trips for each PaymentType
select p.description as paymenttype, count(*) as tripcount
from trip tr
join payment p on tr.paymenttype = p.id
group by p.description
order by tripcount desc;

-- This query counts the number of trips taken on weekends versus weekdays.
select 
	case 
		when t.isweekend = 'true' then 'weekend'
		else 'weekday'
	end as daytype,
	count(*) as tripcount
from 
	trip tr
join 
	time t on tr.id = t.tripid
group by daytype
order by daytype;


-- Complex queries

-- This query finds the zone in each borough that earned the highest total TotalAmount on each day of the week. This could help analyze the busiest and most profitable zones on specific days.
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

-- This query calculates the average TripDistance and FareAmount grouped by both PaymentType and Ratecode, providing insights into how distance and fare vary by payment and rate type.
select p.description as paymenttype, r.description as ratecode, avg(tr.tripdistance) as avgtripdistance, avg(tr.fareamount) as avgfareamount
from trip tr
join payment p on tr.paymenttype = p.id
join ratecode r on tr.ratecode = r.id
group by p.description, r.description
order by avgfareamount;

-- This query identifies the peak hours in terms of trip count for each borough, differentiating between weekdays and weekends. It could provide valuable insights into traffic patterns across different boroughs.
SELECT 
    l.borough,
    CASE 
        WHEN t.isweekend = 'true' THEN 'weekend' 
        ELSE 'weekday' 
    END AS daytype,
    EXTRACT(HOUR FROM T.PickUpTime) AS hour,
    COUNT(*) AS tripcount
FROM trip tr
JOIN location l ON tr.pickuplocation = l.id
JOIN time t ON tr.id = t.tripid
GROUP BY l.borough, daytype, EXTRACT(HOUR FROM T.PickUpTime)
HAVING 
    COUNT(*) = (
        SELECT MAX(tripcountperhour)
        FROM (
            SELECT 
                COUNT(*) AS tripcountperhour,
                CASE 
                    WHEN t2.isweekend = 'true' THEN 'weekend'
                    ELSE 'weekday'
                END AS daytype
            FROM trip tr2
            JOIN location l2 ON tr2.pickuplocation = l2.id
            JOIN time t2 ON tr2.id = t2.tripid
            WHERE l2.borough = l.borough
            GROUP BY daytype, EXTRACT(HOUR FROM t2.PickUpTime)
        ) AS hourlycounts
        WHERE hourlycounts.daytype = daytype
    )
ORDER BY l.borough, daytype, hour;

-- Identify the top 10 most profitable trip routes by total revenue. This query joins the trip data with the location data to get the origin and destination zones, groups the results by those zones, calculates the total revenue for each route, and returns the top 10 most profitable routes.
select originlocation.zone as originzone,
	destination.zone as destzone,
	sum(trip.totalamount) as totalrevenue
from trip
join location as originlocation on trip.pickuplocation = originlocation.id
join location as destlocation on trip.dropofflocation = destlocation.id
group by originzone, destzone
order by totalrevenue desc
limit 10;

-- Analyze trip volume and revenue trends over time. This query extracts the year and month from the PickUpDate, groups the data by that time dimension, and calculates the total trip count, revenue, and average tip amount for each month. This can reveal seasonal patterns and trends in the business.
select date_trunc('month', time.pickupdate) as monthyear,
	count(*) as tripcount,
	sum(trip.totalamount) as totalrevenue,
	avg(trip.tipamount) as avgtipamount,
from trip
group by monthyear
order by monthyear;

-- Analyze the impact of congestion surcharges on trip revenue. This query categorizes trips into two groups - those with a congestion surcharge and those without. It then calculates the trip count, total revenue, and average trip revenue for each group. This can show how congestion surcharges impact the overall business metrics.
select 
	case when trip.congestionsurcharge > 0 then 'with surcharge' else 'no surcharge' end as surchargestatus,
	count(*) as tripcount,
	sum(trip.totalamount) as totalrevenue,
	avg(trip.totalrevenue) as avgtriprevenue
from trip
group by surchargestatus
order by tripcount desc;
		