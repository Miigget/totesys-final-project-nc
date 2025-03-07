import pandas as pd
import json
import boto3
from src.transform.transform_utils.ingestion_s3_handler import (
    IngestionS3Handler,
)


class PandaTransformation:

    def transform_currency_data(self):
        try:
            ingestion_handler = IngestionS3Handler()
            raw_data = ingestion_handler.get_data_from_ingestion()
            with open("currencies_lookup.json", "r") as file:
                currencies_lookup = json.load(file)
            df_currency = pd.DataFrame(raw_data["currency"])
            df_currency.drop(
                columns=["created_at", "last_updated"], inplace=True
            )
            df_currency["currency_name"] = df_currency["currency_code"].map(
                currencies_lookup
            )
            return df_currency
        except Exception as e:
            print(e)
            return None

    def transform_location_data(self):
        try:
            ingestion_handler = IngestionS3Handler()
            raw_data = ingestion_handler.get_data_from_ingestion()
            df_location = pd.DataFrame(raw_data["address"])
            del df_location["created_at"]
            del df_location["last_updated"]
            df_location.rename(
                columns={"address_id": "location_id"}, inplace=True
            )
            return df_location
        except Exception as e:
            print(e)
            return None

    def transform_staff_data(self):
        try:
            ingestion_handler = IngestionS3Handler()
            raw_data = ingestion_handler.get_data_from_ingestion()
            df_staff = pd.DataFrame(raw_data["staff"])
            del df_staff["created_at"]
            del df_staff["last_updated"]
            df_department = pd.DataFrame(raw_data["department_all_data"])
            merged_df = pd.merge(
                df_staff, df_department, on="department_id", how="left"
            )
            del merged_df["department_id"]
            del merged_df["manager"]
            del merged_df["created_at"]
            del merged_df["last_updated"]
            return merged_df[
                [
                    "staff_id",
                    "first_name",
                    "last_name",
                    "department_name",
                    "location",
                    "email_address",
                ]
            ]
        except Exception as e:
            print(e)
            return None

    def transform_design_data(self):
        try:
            ingestion_handler = IngestionS3Handler()
            raw_data = ingestion_handler.get_data_from_ingestion()
            df_design = pd.DataFrame(raw_data["design"])
            del df_design["created_at"]
            del df_design["last_updated"]
            return df_design
        except Exception as e:
            print(e)
            return None

    def transform_counterparty_data(self):
        try:
            ingestion_handler = IngestionS3Handler()
            raw_data = ingestion_handler.get_data_from_ingestion()
            df_counterparty = pd.DataFrame(raw_data["counterparty"])
            del df_counterparty["created_at"]
            del df_counterparty["last_updated"]
            df_counterparty.rename(
                columns={"legal_address_id": "address_id"}, inplace=True
            )
            df_address = pd.DataFrame(raw_data["address_all_data"])
            merged_df = pd.merge(
                df_counterparty, df_address, on="address_id", how="left"
            )
            merged_df.rename(
                columns={
                    "address_line_1": "counterparty_legal_address_line_1",
                    "address_line_2": "counterparty_legal_address_line_2",
                    "district": "counterparty_legal_district",
                    "city": "counterparty_legal_city",
                    "postal_code": "counterparty_legal_postal_code",
                    "country": "counterparty_legal_country",
                    "phone": "counterparty_legal_phone_number",
                },
                inplace=True,
            )
            return merged_df[
                [
                    "counterparty_id",
                    "counterparty_legal_name",
                    "counterparty_legal_address_line_1",
                    "counterparty_legal_address_line_2",
                    "counterparty_legal_district",
                    "counterparty_legal_city",
                    "counterparty_legal_postal_code",
                    "counterparty_legal_country",
                    "counterparty_legal_phone_number",
                ]
            ]
        except Exception as e:
            print(e)
            return None

    def transform_sales_order_data(self):
        try:
            ingestion_handler = IngestionS3Handler()
            raw_data = ingestion_handler.get_data_from_ingestion()
            df_sales_order = pd.DataFrame(raw_data["sales_order"])
            df_sales_order[["created_date", "created_time"]] = df_sales_order[
                "created_at"
            ].str.split(" ", n=1, expand=True)
            df_sales_order[["last_updated_date", "last_updated_time"]] = (
                df_sales_order["last_updated"].str.split(" ", n=1, expand=True)
            )
            df_sales_order.rename(
                columns={"staff_id": "sales_staff_id"}, inplace=True
            )
            return df_sales_order[
                [
                    "sales_order_id",
                    "created_date",
                    "created_time",
                    "last_updated_date",
                    "last_updated_time",
                    "sales_staff_id",
                    "counterparty_id",
                    "units_sold",
                    "unit_price",
                    "currency_id",
                    "design_id",
                    "agreed_payment_date",
                    "agreed_delivery_date",
                    "agreed_delivery_location_id",
                ]
            ]
        except Exception as e:
            print(e)
            return None

    def transform_date_data(self):
        try:
            ingestion_handler = IngestionS3Handler()
            raw_data = ingestion_handler.get_data_from_ingestion()
            df_sales_order = pd.DataFrame(raw_data["sales_order"])

            date_columns = [
                "created_at",
                "last_updated",
                "agreed_payment_date",
                "agreed_delivery_date",
            ]
            all_dates = pd.Series()
            for col in date_columns:
                df_sales_order[col] = pd.to_datetime(
                    df_sales_order[col], errors="coerce"
                )
                all_dates = pd.concat([all_dates, df_sales_order[col]])

            dates = all_dates.dropna()
            dates = dates.drop_duplicates()
            dates = dates.sort_values()
            dates = dates.reset_index(drop=True)

            dim_date = pd.DataFrame({"date_id": dates})
            dim_date["year"] = dim_date["date_id"].dt.year
            dim_date["month"] = dim_date["date_id"].dt.month
            dim_date["day"] = dim_date["date_id"].dt.day
            dim_date["day_of_week"] = dim_date["date_id"].dt.dayofweek
            dim_date["day_name"] = dim_date["date_id"].dt.strftime("%A")
            dim_date["month_name"] = dim_date["date_id"].dt.strftime("%B")
            dim_date["quarter"] = dim_date["date_id"].dt.quarter

            return dim_date

        except Exception as e:
            print(f"Error creating dim_date: {e}")
            return None

    def returns_dictionary_of_dataframes(self):
        s3_client = boto3.client("s3")
        try:
            transform_currency_data = (
                PandaTransformation.transform_currency_data
            )
            df_currency = transform_currency_data(self)

            transform_location_data = (
                PandaTransformation.transform_location_data
            )
            df_location = transform_location_data(self)

            transform_staff_data = PandaTransformation.transform_staff_data
            df_staff = transform_staff_data(self)

            transform_design_data = PandaTransformation.transform_design_data
            df_design = transform_design_data(self)

            transform_counterparty_data = (
                PandaTransformation.transform_counterparty_data
            )
            df_counterparty = transform_counterparty_data(self)

            transform_sales_order_data = (
                PandaTransformation.transform_sales_order_data
            )
            df_sales_order = transform_sales_order_data(self)

            transform_date_data = PandaTransformation.transform_date_data
            df_date = transform_date_data(self, s3_client)

            initial_output = {
                "dim_currency": df_currency,
                "dim_location": df_location,
                "dim_staff": df_staff,
                "dim_design": df_design,
                "dim_counterparty": df_counterparty,
                "fact_sales_order": df_sales_order,
                "dim_date": df_date,
            }
            output = {}
            for key, value in initial_output.items():
                if value is not None:
                    output[key] = value
            return output
        except Exception as e:
            print(e)
            return None
