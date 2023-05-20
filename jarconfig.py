from pyspark.sql import SparkSession

def create_spark_session():
    spark = (
        SparkSession.builder.appName("RoadWeatherETL")
        .config("spark.jars", "C:\\Terraform\\lib\\azure-security-keyvault-secrets-4.6.1.jar,"
                "C:\\Terraform\\lib\\azure-storage-blob-11.0.1.jar,"
                "C:\\Terraform\\lib\\hadoop-azure-3.3.5.jar,C:\\Terraform\\lib\\jetty-util-12.0.0.beta1.jar,"
                "C:\\Terraform\\lib\\azure-storage-8.6.6.jar, C:\\Terraform\\lib\\jetty-util-ajax-12.0.0.beta1.jar")
        .getOrCreate()
    )
    return spark
