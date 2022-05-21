## Steps to run the assignment solution

### 1. Install docker if not installed

### 2. Run command to start the containers:

```
-- install deps
pip install -r requirements.txt

-- start containers
docker compose up

-- for containerID
docker container ls

-- open container to debug
docker exec -it <containerId> bash

-- manually copy csvs to pg instance
docker cp .\output\assignment_1\ <containerId>:/output/assignment_1/
```

### Notes:

The copy command to import csv s to db may not work on C drive due to user permissions, so I had to copy files to postgres container followed by import script.

## Assignment 3:

I tried to create a stage table (in a raw sql script) to insert only the valid records from the raw table created in the previous scripts.
This would help increase the quality of the data and detect anomalous rows though adding check constraints.

```
CREATE TABLE IF NOT EXISTS public.stage_yellow_taxi_trips
(
id integer NOT NULL DEFAULT nextval('stage_yellow_taxi_trips'::regclass),
vendor_id smallint,
CHECK (vendor_id BETWEEN 1 AND 2),
tpep_pickup timestamp,
tpep_dropoff timestamp,
passenger_count smallint,
CHECK (passenger_count BETWEEN 1 AND 6),
trip_distance double precision,
pu_location_id numeric,
do_location_id numeric,
ratecode_id double precision,
CHECK (ratecode_id BETWEEN 1 AND 6),
store_and_fwd_flag varchar(1) ,
CHECK (store_and_fwd_flag IN ('Y','N')),
payment_type double precision,
fare_amount numeric,
extra numeric,
mta_tax numeric,
improvement_surcharge numeric,
tip_amount numeric,
tolls_amount numeric,
total_amount numeric,
congestion_surcharge numeric,
airport_fee numeric,
CONSTRAINT stage_yellow_taxi_trips_pk PRIMARY KEY (id)
)
;

INSERT INTO public.stage_yellow_taxi_trips
SELECT
id
,vendorid as vendor_id
,cast(tpep_pickup_datetime as timestamp) as tpep_pickup
,cast(tpep_dropoff_datetime as timestamp)as tpep_dropoff
,cast(passenger_count as int) passenger_count
,trip_distance
,pulocationid as pu_location_id
,dolocationid as do_location_id
,ratecodeid as ratecode_id
,store_and_fwd_flag
,payment_type
,fare_amount
,extra
,mta_tax
,improvement_surcharge
,tip_amount
,tolls_amount
,total_amount
,congestion_surcharge
,airport_fee
FROM public.yellow_taxi_trips
WHERE
(ratecodeid > 0 and ratecodeid < 6)
and (passenger_count > 0 and passenger_count < 6)
and (vendorid in (1,2))
;
```

## Assignment 4:

I didn't have the time to generate and architect the tables based on the fact table loaded in the previous scripts due to some configuration issues with docker.

## Assignment 5:

- The docker compose file running the postgres & pgadmin containers could be improved to bundle up python and the load data in batch scripts.
- Credentials for the user accounts should be stored in a more secure location/environment file although docker-compose.yml may be enough.
- Passwords should be harder to brute-force and more secure.
- In order to import the files the user needs to manually run docker cp into the postgres container, this can be automated with docker library command or with a custom build script in docker-compose.yml as mentioned below.
- The files for each day could be converted to a more optimal format (like Apache parquet with spark lib) and imported directly but I couldn't figure it out in the given time.
- Better project structure with pipenv/poetry
- for improving data quality, I would have used data from the stage table and created a partitioned table on the 'tpep_dropoff_datetime' (substring 1-10) column.
