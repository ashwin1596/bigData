import pandas as pd

pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None 

borough_info = "raw_data\\taxi_zone_lookup.csv"
data_2024_01 = "raw_data\\yellow_tripdata_2024-01.parquet"
data_2024_02 = "raw_data\\yellow_tripdata_2024-02.parquet"
data_2024_03 = "raw_data\\yellow_tripdata_2024-03.parquet"
data_2024_04 = "raw_data\\yellow_tripdata_2024-04.parquet"
data_2024_05 = "raw_data\\yellow_tripdata_2024-05.parquet"
data_2024_06 = "raw_data\\yellow_tripdata_2024-06.parquet"
data_2024_07 = "raw_data\\yellow_tripdata_2024-07.parquet"

data_2023_01 = "raw_data\\yellow_tripdata_2023-01.parquet"
data_2023_02 = "raw_data\\yellow_tripdata_2023-02.parquet"
data_2023_03 = "raw_data\\yellow_tripdata_2023-03.parquet"
data_2023_04 = "raw_data\\yellow_tripdata_2023-04.parquet"
data_2023_05 = "raw_data\\yellow_tripdata_2023-05.parquet"
data_2023_06 = "raw_data\\yellow_tripdata_2023-06.parquet"
data_2023_07 = "raw_data\\yellow_tripdata_2023-07.parquet"
data_2023_08 = "raw_data\\yellow_tripdata_2023-08.parquet"
data_2023_09 = "raw_data\\yellow_tripdata_2023-09.parquet"
data_2023_10 = "raw_data\\yellow_tripdata_2023-10.parquet"
data_2023_11 = "raw_data\\yellow_tripdata_2023-11.parquet"
data_2023_12 = "raw_data\\yellow_tripdata_2023-12.parquet"

trips_data = [
    # data_2024_01, data_2024_02, data_2024_03, data_2024_04, data_2024_05, data_2024_06, data_2024_07,
              data_2023_01, data_2023_02, data_2023_03, data_2023_04, data_2023_05, data_2023_06, data_2023_07,
              data_2023_08, data_2023_09, data_2023_10, data_2023_11, data_2023_12]

# boroguh
borough_df = pd.read_csv(borough_info)

# Location table requires ID, Borough, Zone, save new csv
borough_df.rename(columns={'LocationID': 'ID'}, inplace=True)
borough_df[['ID', 'Borough', 'Zone']].to_csv('C:\\Sem4\\CSCI620\\Project\\processed_data\\borough_info.csv', index=False)

# RateCode table requires columns: ID and description
ratecode_df = pd.DataFrame({
    'ID': [1, 2, 3, 4, 5, 6],
    'description': ['Standard rate', 'JFK', 'Newark', 'Nassau or Westchester', 'Negotiated fare', 'Group ride']
})
ratecode_df.to_csv('C:\\Sem4\\CSCI620\\Project\\processed_data\\ratecode_info.csv', index=False)

# Payment table requires columns: ID and description
payment_df = pd.DataFrame({
    'ID': [1, 2, 3, 4, 5, 6],
    'description': ['Credit card', 'Cash', 'No charge', 'Dispute', 'Unknown', 'Voided trip']
})
payment_df.to_csv('C:\\Sem4\\CSCI620\\Project\\processed_data\\payment_info.csv', index=False)

# Vendor table requires columns: ID and description
vendor_df = pd.DataFrame({
    'ID': [1, 2],
    'description': ['Creative Mobile Technologies, LLC', 'VeriFone Inc.']
})
vendor_df.to_csv('C:\\Sem4\\CSCI620\\Project\\processed_data\\vendor_info.csv', index=False)


# clear the time_info.csv and trip_info.csv
open('C:\\Sem4\\CSCI620\\Project\\processed_data\\time_info.csv', 'w').close()
open('C:\\Sem4\\CSCI620\\Project\\processed_data\\trip_info.csv', 'w').close()

count = 0
next_id_start = 0
for trip in trips_data:
    if count == 0:
        header_bool = True
        first = False
        count = 1
    else:
        header_bool = False
        count += 1

    print("Loading file ", count, " of ", len(trips_data))
        

    # Load the Parquet file
    data_df = pd.read_parquet(trip)
    data_df['TripID'] = data_df.index
    data_df.dropna(inplace=True)

    # Time table requires TripID, PickUpDate, PickUpTime, DropOffDate, DropOffTime, DayOfWeek, IsWeekend
    # Create a new DataFrame with the desired columns
    time_df = data_df[['TripID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']]

    # Convert datetime to appropriate formats
    time_df['PickUpDate'] = time_df['tpep_pickup_datetime'].dt.date
    time_df['PickUpTime'] = time_df['tpep_pickup_datetime'].dt.time
    time_df['DropOffDate'] = time_df['tpep_dropoff_datetime'].dt.date
    time_df['DropOffTime'] = time_df['tpep_dropoff_datetime'].dt.time

    # Calculate DayOfWeek and IsWeekend
    time_df['DayOfWeek'] = time_df['tpep_pickup_datetime'].dt.dayofweek
    time_df['IsWeekend'] = time_df['DayOfWeek'].isin([5, 6])

    # Drop unnecessary columns
    time_df.drop(columns=['tpep_pickup_datetime', 'tpep_dropoff_datetime'], inplace=True)

    # Save the time DataFrame to a CSV file
    time_df.to_csv('C:\\Sem4\\CSCI620\\Project\\processed_data\\time_info.csv', mode='a', header=header_bool, index=False)

    # Trip table requires columns: TripID, PassengerCount, TripDistance, StoreAndFwdFlag, FareAmount, Extra, MTATax, 
    # ImprovementSurcharge, TipAmount, TollsAmount, TOtalAmount, CongestionSurcharge, AirportFee, Vendor, PaymentType, 
    # Ratecode, PickUpLocation, DropOffLocation

    desired_columns = ['TripID', 'passenger_count', 'trip_distance', 'store_and_fwd_flag', 'fare_amount', 'extra', 'mta_tax', 'improvement_surcharge',
                    'tip_amount', 'tolls_amount', 'total_amount', 'congestion_surcharge', 'Airport_fee', 'VendorID', 'payment_type', 'RatecodeID',
                    'PULocationID', 'DOLocationID']

    existing_columns = [col for col in desired_columns if col in data_df.columns]
    # existing_columns = [col if col in data_df.columns else None for col in desired_columns]

    trip_df = data_df[existing_columns].rename(columns={
                                                            'TripID': 'ID',
                                                            'passenger_count': 'PassengerCount',
                                                            'trip_distance': 'TripDistance',
                                                            'store_and_fwd_flag': 'StoreAndFwdFlag',
                                                            'fare_amount': 'FareAmount',
                                                            'mta_tax': 'MTATax',
                                                            'improvement_surcharge': 'ImprovementSurcharge',
                                                            'tip_amount': 'TipAmount',
                                                            'tolls_amount': 'TollsAmount',
                                                            'total_amount': 'TotalAmount',
                                                            'congestion_surcharge': 'CongestionSurcharge',
                                                            'Airport_fee': 'AirportFee',
                                                            'VendorID': 'Vendor',
                                                            'payment_type': 'PaymentType',
                                                            'RatecodeID': 'Ratecode',
                                                            'PULocationID': 'PickUpLocation',
                                                            'DOLocationID': 'DropOffLocation'
                                                        }, errors= 'ignore')
    trip_df['ID'] = trip_df['ID'] + next_id_start
    next_id_start = trip_df['ID'].max() + 1
    trip_df['PassengerCount'] = trip_df['PassengerCount'].astype(int)
    trip_df['ImprovementSurcharge'] = trip_df['ImprovementSurcharge'].astype(int)
    trip_df['Vendor'] = trip_df['Vendor'].astype(int)
    trip_df['PaymentType'] = trip_df['PaymentType'].astype(int)
    trip_df['Ratecode'] = trip_df['Ratecode'].astype(int)
    trip_df['PickUpLocation'] = trip_df['PickUpLocation'].astype(int)
    trip_df['DropOffLocation'] = trip_df['DropOffLocation'].astype(int)
    trip_df.to_csv('C:\\Sem4\\CSCI620\\Project\\processed_data\\trip_info.csv', float_format='%.0f', mode='a', header=header_bool, index=False)



