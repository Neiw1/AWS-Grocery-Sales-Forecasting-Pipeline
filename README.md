# AWS Grocery Sales Forecasting Pipeline

This project implements a serverless pipeline on AWS to forecast grocery sales. The architecture leverages S3, Lambda, and DynamoDB to create an automated workflow for data processing, feature engineering, model training, and prediction.

## Overall Architecture

The pipeline is designed as an event-driven, serverless architecture on AWS, as depicted in the architecture diagram. It automates the process of ingesting raw sales data, transforming it, and generating sales forecasts.

The workflow is as follows:

1.  **Data Ingestion:** A **User** uploads a `Raw CSV File` to the **Raw Data S3 Bucket**.

2.  **ETL Process:**
    *   The S3 upload event **Triggers** the **ETL Lambda**.
    *   The ETL Lambda performs two main tasks:
        *   It cleans and processes the data, saving the result to the **Cleaned Data S3 Bucket**.
        *   It **stores historic data** in **DynamoDB** for later use.

3.  **Prediction Process:**
    *   The new object in the **Cleaned Data S3 Bucket** **Triggers** the **Prediction Lambda**.
    *   The Prediction Lambda then:
        *   **Fetches historic data** from DynamoDB.
        *   Uses this data to **engineer features** and **make a prediction** using a pre-trained model.
        *   Saves the final forecast to the **Prediction Output S3 Bucket**.

This architecture ensures that the entire process, from data upload to prediction, is fully automated and scalable.

## Key Components

### Lambda Functions

*   `lambda functions/grocery-sale-etl.py`: The **ETL Lambda**. It is triggered by an upload to the Raw Data S3 Bucket. It cleans the data, stores it in DynamoDB, and saves a processed version to the Cleaned Data S3 Bucket.
*   `lambda functions/grocery-sale-prediction.py`: The **Prediction Lambda**. It is triggered by new data in the Cleaned Data S3 Bucket. It fetches historical data from DynamoDB, engineers features, and generates a sales forecast, which is saved to the Prediction Output S3 Bucket.

### Model Training

*   `model training/training.py`: This script trains the LightGBM regression model. It uses features such as store and item numbers, promotions, and sales lags to predict unit sales. The trained model is saved to `model.txt`.
*   `model training/model.txt`: The pre-trained LightGBM model file, which is loaded by the Prediction Lambda.

### Miscellaneous Scripts

*   `miscellaneous/data_prep.py`: A utility script to prepare and split the dataset for training and testing.
*   `miscellaneous/data_to_dynamodb.py`: A script to upload data from a CSV file to a DynamoDB table.

## Usage

1.  **Upload Data:** Place your raw sales data (e.g., `for_uploading.csv`) into the **Raw Data S3 Bucket**.
2.  **Automatic Processing:** The upload will automatically trigger the **ETL Lambda**, which processes the data and stores it.
3.  **Prediction Generation:** The processed data then triggers the **Prediction Lambda**, which generates the sales forecast.
4.  **Access Results:** The prediction results will be available in the **Prediction Output S3 Bucket** as a CSV file.

## File Descriptions

| File                                           | Description                                                                                             |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `for_uploading.csv`                            | A sample CSV file to be uploaded to the **Raw Data S3 Bucket**.                                         |
| `test_data1.csv`                               | Test data for prediction.                                                                               |
| `test_for_prediction.csv`                      | A sample of test data for prediction.                                                                   |
| `lambda functions/grocery-sale-etl.py`         | The ETL Lambda for data cleaning and storage.                                                           |
| `lambda functions/grocery-sale-prediction.py`  | The Prediction Lambda that performs sales forecasting using the trained model and historical data.      |
| `miscellaneous/data_prep.py`                   | A script for preparing and splitting the dataset.                                                       |
| `miscellaneous/data_to_dynamodb.py`            | A utility to upload CSV data to DynamoDB.                                                               |
| `model training/training.py`                   | The script used to train the sales forecasting model.                                                   |
| `model training/model.txt`                     | The trained LightGBM model.                                                                             |
