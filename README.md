# AWS Grocery Sales Forecasting Pipeline

This project implements a serverless pipeline on AWS to forecast grocery sales. The architecture leverages S3, Lambda, and DynamoDB to create an automated workflow for data processing, feature engineering, model training, and prediction.

## Overall Architecture

The pipeline is designed as an event-driven, serverless architecture on AWS. It automates the process of ingesting raw sales data, transforming it, and generating sales forecasts.

The workflow is as follows:

1.  **Data Ingestion (S3):** The process begins when a user uploads a raw sales data file (in CSV format) to a designated "raw data" S3 bucket.

2.  **ETL and Data Storage (Lambda & DynamoDB):**
    *   The S3 upload event triggers the `grocery-sale-etl` Lambda function.
    *   This function performs initial data cleaning and transformation.
    *   It then stores this cleaned data into a DynamoDB table, which serves as a historical data store.
    *   Finally, it saves the processed file to a "processed data" S3 bucket, which acts as a trigger for the next step.

3.  **Prediction (Lambda, S3 & DynamoDB):**
    *   The new object in the "processed data" S3 bucket triggers the `grocery-sale-prediction` Lambda function.
    *   This function retrieves the processed data from the trigger event.
    *   It also queries the DynamoDB table to fetch historical data, which is used to calculate dynamic features like sales lags.
    *   The function loads a pre-trained LightGBM model from a separate S3 bucket.
    *   Using the combined data (processed data + calculated features), it generates sales predictions.
    *   The final predictions are saved as a CSV file to an "output" S3 bucket.

This architecture ensures that the entire process, from data upload to prediction, is fully automated and scalable.

## Key Components

### Lambda Functions

*   `lambda functions/grocery-sale-etl.py`: This function handles the Extract, Transform, and Load (ETL) process. It cleans the raw data from the initial S3 upload and stores the result in a DynamoDB table and a separate S3 bucket for processed data.
*   `lambda functions/grocery-sale-prediction.py`: This function is responsible for generating sales forecasts. It is triggered by new data in the processed S3 bucket. It loads the trained LightGBM model, retrieves historical data from DynamoDB to compute lag features, and runs the prediction. The output is saved in a CSV file in the output S3 bucket.

### Model Training

*   `model training/training.py`: This script trains the LightGBM regression model. It uses features such as store and item numbers, promotions, and sales lags to predict unit sales. The trained model is saved to `model.txt`.
*   `model training/model.txt`: The pre-trained LightGBM model file.

### Miscellaneous Scripts

*   `miscellaneous/data_prep.py`: A utility script to prepare and split the dataset for training and testing.
*   `miscellaneous/data_to_dynamodb.py`: A script to upload data from a CSV file to a DynamoDB table.

## Usage

1.  **Upload Data:** Place your raw sales data (e.g., `for_uploading.csv`) into the designated raw data S3 bucket.
2.  **Automatic Processing:** The upload will automatically trigger the `grocery-sale-etl` Lambda function, which processes the data and stores it.
3.  **Prediction Generation:** The processed data then triggers the `grocery-sale-prediction` Lambda, which generates the sales forecast.
4.  **Access Results:** The prediction results will be available in the output S3 bucket as a CSV file.

## File Descriptions

| File                                           | Description                                                                                             |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `for_uploading.csv`                            | A sample CSV file with data to be uploaded to the raw data S3 bucket.                                   |
| `test_data1.csv`                               | Test data for prediction.                                                                               |
| `test_for_prediction.csv`                      | A sample of test data for prediction.                                                                   |
| `lambda functions/grocery-sale-etl.py`         | The ETL Lambda function for data cleaning and feature engineering.                                      |
| `lambda functions/grocery-sale-prediction.py`  | The Lambda function that performs sales forecasting using the trained model and historical data from DynamoDB. |
| `miscellaneous/data_prep.py`                   | A script for preparing and splitting the dataset.                                                       |
| `miscellaneous/data_to_dynamodb.py`            | A utility to upload CSV data to DynamoDB.                                                               |
| `model training/training.py`                   | The script used to train the sales forecasting model.                                                   |
| `model training/model.txt`                     | The trained LightGBM model.                                                                             |
