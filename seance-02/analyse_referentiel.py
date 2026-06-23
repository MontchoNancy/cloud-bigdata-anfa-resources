from pyspark.sql import SparkSession
from pyspark.sql.functions import sum as spark_sum, count, avg, desc

DATA_DIR = "/data/referentiel"  # chemin DANS le conteneur (bind mount)


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("Anfa - Analyse du référentiel")
        .master("local[*]")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    lignes = spark.read.csv(f"{DATA_DIR}/lignes.csv", header=True, inferSchema=True)
    arrets = spark.read.csv(f"{DATA_DIR}/arrets.csv", header=True, inferSchema=True)
    bus    = spark.read.csv(f"{DATA_DIR}/bus.csv",    header=True, inferSchema=True)
    tarifs = spark.read.csv(f"{DATA_DIR}/tarifs.csv", header=True, inferSchema=True)

    print("\n Tarif moyen par type :")
    print("\n Test")
    tarifs.groupBy("type") \
          .agg(avg("prix_fcfa").alias("prix_moyen")) \
          .orderBy("type") \
          .show(truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()

