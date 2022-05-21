import pandas as pd
import psycopg2
import os
import tarfile
import docker

current_path = os.path.dirname(os.path.abspath(__file__))

client = docker.from_env()

def convert_parquet_to_csv(input_file_name, output_file_name):
    df = pd.read_parquet(input_file_name)
    df.to_csv(output_file_name, index = False)
    df_sample = df.head(1000)
    df_sample.to_csv('sample.csv', index = False)

def split_csv_by_column(file, output_path, column = 'tpep_dropoff_datetime', column_filter = '2020-01'):
    df = pd.read_csv(file, index_col = 0)

    # get unique column values by splitting each by space and taking first for date
    unique_values = df[column].str.split(' ').str[0].unique()

    for value in unique_values:
        if column_filter in value:
          df_filtered = df[df[column].str.contains(value)]
          df_filtered.to_csv(f'{output_path}\\{value}.csv')

def load_files_to_postgres(path, docker_path, table_name, columns, conn):
    cur = conn.cursor()

    for file in os.listdir(path):

        if file.endswith('.csv'):
            print(f'Loading {file} to postgres')
            cur.execute(f'COPY {table_name} ({columns}) FROM \'{docker_path}/{file}\' DELIMITER \',\' CSV HEADER;')
            conn.commit()

def create_table(name, schema, conn):
    cur = conn.cursor()
    cur.execute(f'CREATE TABLE IF NOT EXISTS {name} ({schema});')
    conn.commit()

if __name__ == '__main__':
    convert_parquet_to_csv('yellow_tripdata_2020-01.parquet', 'yellow_tripdata_2020-01.csv')
    split_csv_by_column('yellow_tripdata_2020-01.csv', 'output/assignment_1')

    # split_csv_by_column('sample.csv', 'output/assignment_1')

    conn = psycopg2.connect(host='localhost', database='assignment_db', user='root', password='assignment')
    schema = 'id serial PRIMARY KEY, VendorID smallint, c datetime, tpep_dropoff_datetime datetime, Passenger_count float, Trip_distance float, PULocationID int, DOLocationID int, RateCodeID float, Store_and_fwd_flag varchar, Payment_type float, Fare_amount numeric, Extra numeric, MTA_tax numeric, Improvement_surcharge numeric, Tip_amount numeric, Tolls_amount numeric, Total_amount numeric, Congestion_Surcharge numeric, Airport_fee numeric'
    create_table('yellow_taxi_trips', schema, conn)

    # get first row as string from csv
    header = pd.read_csv('sample.csv', nrows = 0)
    header = header.columns.to_list()
    header = ','.join(header)

    # this would work only if docker cp is run before due to system permission in C drive
    # load_files_to_postgres('output/assignment_1', '/output/assignment_1', 'YELLOW_TAXI_TRIPS', header, conn)

    print('Done')
    exit(0)
