from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp, col, window, first
from pyspark.sql.functions import from_json ,get_json_object, to_timestamp, to_timestamp, col, window
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from azure.identity import DefaultAzureCredential
from azure.eventhub import EventHubProducerClient, EventData
from azure.keyvault.secrets import SecretClient
from pyspark.sql import functions as F
import findspark
findspark.init()

def create_spark_session():
    """Create a SparkSession."""
    return SparkSession.builder \
        .appName("AirlineApp") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-azure:3.2.1") \
        .getOrCreate()

def get_input_schema():
    return StructType([
        StructField("Flight_ID", StringType(), True),
        StructField("Air_Name", StringType(), True),
        StructField("City", StringType(), True),
        StructField("Country_code", StringType(), True),
        StructField("date_time", StringType(), True),
        StructField("site_name", StringType(), True),
        StructField("posa_continent", StringType(), True),
        StructField("user_location_country", StringType(), True),
        StructField("user_location_city", StringType(), True),
        StructField("orig_destination_distance", DoubleType(), True),
        StructField("user_id", IntegerType(), True),
        StructField("is_mobile", IntegerType(), True),
        StructField("is_package", StringType(), True),
        StructField("channel", IntegerType(), True),
        StructField("srch_ci", StringType(), True),
        StructField("srch_co", StringType(), True),
        StructField("srch_adults_cnt", IntegerType(), True),
        StructField("srch_children_cnt", IntegerType(), True),
        StructField("srch_rm_cnt", IntegerType(), True),
        StructField("srch_destination_id", IntegerType(), True),
        StructField("srch_destination_type_id", IntegerType(), True),
        StructField("hotel_continent", StringType(), True),
        StructField("hotel_country", StringType(), True),
        StructField("hotel_market", StringType(), True),
        StructField("is_booking", IntegerType(), True),
        StructField("cnt", IntegerType(), True),
        StructField("hotel_cluster", IntegerType(), True),
        StructField("A_ID", IntegerType(), True),
        StructField("Capacity", IntegerType(), True),
        StructField("A_weight", IntegerType(), True),
        StructField("Company", StringType(), True),
        StructField("Route_ID", IntegerType(), True),
        StructField("Take_Off_point", StringType(), True),
        StructField("Destination", StringType(), True),
        StructField("Ps_ID", IntegerType(), True),
        StructField("Ps_Name", StringType(), True),
        StructField("Address", StringType(), True),
        StructField("Age", IntegerType(), True),
        StructField("Sex", StringType(), True),
        StructField("Contacts", StringType(), True),
        StructField("Air_code", IntegerType(), True)
    ])


def main():
    # Initialize a SparkSession and set the necessary configurations
    spark = create_spark_session()

    # Get Azure credentials
    credential = credential = DefaultAzureCredential(authority="https://login.microsoftonline.com/d55e8307-d3b4-4a44-b8b0-83ba7425f6c8")


    # Connecting to the Key Vault
    key_vault_uri = "https://flights-vault.vault.azure.net/"
    secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)


    # Retrieving the storage account access key from Key Vault
    storage_account_access_key = secret_client.get_secret("plane-secret")
    

    # Storage account access key set up
    spark.conf.set(
        "spark.hadoop.fs.azure.account.key.airlineflights.blob.core.windows.net",
        storage_account_access_key.value
    )
    spark.conf.set(
        "spark.hadoop.fs.azure", "org.apache.hadoop.fs.azure.NativeAzureFileSystem"
    )

    # Define the input path
    input_path = "wasbs://data-input@airlineflights.blob.core.windows.net/AirlineData.csv"
    
    

    # Define schema for input data
    input_schema = get_input_schema()

    # Read CSV data from Azure Blob Storage using Structured Streaming    
    df = spark.read.schema(input_schema).csv(input_path)
    
    #df = spark.read.schema('input_schema', inferSchema=True, header=True)
    
    # Handle null values
    default_values = {
    "Flight_ID": "",
    "Air_Name": "",
    "City": "",
    "Country_code": "",
    "date_time": "2000-01-01 00:00:00",
    "site_name": "",
    "posa_continent": "",
    "user_location_country": "",
    "user_location_city": "",
    "orig_destination_distance": 0.0,
    "user_id": "0",
    "is_mobile": "0",
    "is_package": "0",
    "channel": "0",
    "srch_ci": "2000-01-01 00:00:00",
    "srch_co": "2000-01-01 00:00:00",
    "srch_adults_cnt": "0",
    "srch_children_cnt": "0",
    "srch_rm_cnt": "0",
    "srch_destination_id": "0",
    "srch_destination_type_id": "0",
    "hotel_continent": "",
    "hotel_country": "",
    "hotel_market": "",
    "is_booking": "0",
    "cnt": "0",
    "hotel_cluster": "0",
    "A_ID": "0",
    "Capacity": "0",
    "A_weight": "0",
    "Company": "",
    "Route_ID": "",
    "Take_Off_point": "",
    "Destination": "",
    "Ps_ID": "0",
    "Ps_Name": "",
    "Address": "",
    "Age": "0",
    "Sex": "",
    "Contacts": "",
    "Air_code": ""
    }
    df = df.na.fill(default_values)


# Convert the date_time column from string to timestamp
    streaming_df = df.withColumn("date_time", to_timestamp("date_time"))

# Set the event time watermark with a duration of 1 minute
    streaming_df = streaming_df.withWatermark("date_time", "1 minute")

# Set watermark
    watermark = "10 minutes"

# Set the windowDuration
    windowDuration = "5 minutes"

    streaming_df = streaming_df.withWatermark("date_time", watermark) \
        .groupBy(window("date_time", windowDuration), "Flight_ID") \
        .agg(
            first(col("Air_Name")).alias("Air_Name"),
            first(col("City")).alias("City"),
            first(col("Country_code")).alias("Country_code"),
            first(col("date_time")).alias("date_time"),
            first(col("site_name")).alias("site_name"),
            first(col("posa_continent")).alias("posa_continent"),
            first(col("user_location_country")).alias("user_location_country"),
            first(col("user_location_city")).alias("user_location_city"),
            first(col("orig_destination_distance")).alias("orig_destination_distance"),
            first(col("user_id")).alias("user_id"),
            first(col("is_mobile")).alias("is_mobile"),
            first(col("is_package")).alias("is_package"),
            first(col("channel")).alias("channel"),
            first(col("srch_ci")).alias("srch_ci"),
            first(col("srch_co")).alias("srch_co"),
            first(col("srch_adults_cnt")).alias("srch_adults_cnt"),
            first(col("srch_children_cnt")).alias("srch_children_cnt"),
            first(col("srch_rm_cnt")).alias("srch_rm_cnt"),
            first(col("srch_destination_id")).alias("srch_destination_id"),
            first(col("srch_destination_type_id")).alias("srch_destination_type_id"),
            first(col("hotel_continent")).alias("hotel_continent"),
            first(col("hotel_country")).alias("hotel_country"),
            first(col("hotel_market")).alias("hotel_market"),
            first(col("is_booking")).alias("is_booking"),
            first(col("cnt")).alias("cnt"),
            first(col("hotel_cluster")).alias("hotel_cluster"),
            first(col("A_ID")).alias("A_ID"),
            first(col("Capacity")).alias("Capacity"),
            first(col("A_weight")).alias("A_weight"),
            first(col("Company")).alias("Company"),
            first(col("Route_ID")).alias("Route_ID"),
            first(col("Take_Off_point")).alias("Take_Off_point"),
            first(col("Destination")).alias("Destination"),
            first(col("Ps_ID")).alias("Ps_ID"),
            first(col("Ps_Name")).alias("Ps_Name"),
            first(col("Address")).alias("Address"),
            first(col("Age")).alias("Age"),
            first(col("Sex")).alias("Sex"),
            first(col("Contacts")).alias("Contacts"),
            first(col("Air_code")).alias("Air_code")
)

    # Define the output path
    output_path = "wasbs://data-output@airlineflights.blob.core.windows.net/flightdata.csv"

    # Write DataFrame to Delta format
    query= (streaming_df.writeStream.outputMode("append").format("delta").option("checkpointLocation", f"{output_path}/_checkpoints").start(output_path))

    query.awaitTermination()

if __name__ == "__main__":
    main()
