import argparse
import logging
from decimal import Decimal

import boto3
import pandas as pd
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def upload_data_to_dynamodb(table_name: str, csv_file_path: str):
    """
    Reads data from a CSV file and uploads it to the specified Amazon DynamoDB table.

    This function performs the following steps:
    1.  Initializes a Boto3 DynamoDB resource.
    2.  Validates the existence of the specified DynamoDB table.
    3.  Reads the CSV file into a pandas DataFrame.
    4.  Handles missing values by replacing them with `None`.
    5.  Converts float values to `Decimal` to ensure compatibility with DynamoDB.
    6.  Uses a batch writer to efficiently upload the data.

    Args:
        table_name: The name of the DynamoDB table.
        csv_file_path: The path to the CSV file.
    """
    try:
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(table_name)
        table.load()
        logging.info(f"Successfully connected to DynamoDB table: '{table_name}'")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logging.error(f"DynamoDB table '{table_name}' not found.")
        else:
            logging.error(f"An unexpected error occurred: {e}")
        return

    try:
        df = pd.read_csv(csv_file_path)
        logging.info(f"Successfully loaded data from '{csv_file_path}'")
    except FileNotFoundError:
        logging.error(f"CSV file not found at: '{csv_file_path}'")
        return

    df = df.where(pd.notnull(df), None)

    # Convert float columns to Decimal
    for col in df.select_dtypes(include=["float"]).columns:
        df[col] = df[col].apply(lambda x: Decimal(str(x)) if x is not None else None)

    try:
        with table.batch_writer() as batch:
            for _, row in df.iterrows():
                batch.put_item(Item=row.to_dict())
        logging.info(
            f"Successfully uploaded {len(df)} items to '{table_name}'"
        )
    except ClientError as e:
        logging.error(f"Failed to upload data to DynamoDB: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload data from a CSV file to an Amazon DynamoDB table."
    )
    parser.add_argument(
        "--table-name",
        type=str,
        required=True,
        help="The name of the DynamoDB table.",
    )
    parser.add_argument(
        "--csv-file",
        type=str,
        required=True,
        help="The path to the CSV file.",
    )
    args = parser.parse_args()

    upload_data_to_dynamodb(args.table_name, args.csv_file)