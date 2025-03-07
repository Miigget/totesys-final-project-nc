import pytest
import pandas as pd
from src.transform.transform_utils.transform_data_handler import (
    PandaTransformation,
)


@pytest.fixture(autouse=True)
def mock_aws_credentials(monkeypatch):
    """Mocked AWS Credentials for moto."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "test")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "test")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-2")
    monkeypatch.setenv("PROCESSED_S3_BUCKET_NAME", "test")


@pytest.fixture
def mock_currency_lookup(mocker):
    """Mock JSON currency lookup file."""
    mocker.patch(
        "builtins.open",
        mocker.mock_open(
            read_data='{"USD": "United States Dollar", "EUR": "Euro"}'
        ),
    )
    mocker.patch(
        "json.load",
        return_value={"USD": "United States Dollar", "EUR": "Euro"},
    )


@pytest.fixture
def mock_sales_order_data():
    return {
        "sales_order": [
            {
                "created_at": "2024-01-01 10:00:00",
                "last_updated": "2024-01-02 11:00:00",
                "agreed_payment_date": "2024-01-03 12:00:00",
                "agreed_delivery_date": "2024-01-04 13:00:00",
            },
            {
                "created_at": "2024-01-01 10:00:00",
                "last_updated": "2024-01-05 14:00:00",
                "agreed_payment_date": None,
                "agreed_delivery_date": "2024-01-01 15:00:00",
            },
        ]
    }


def test_returns_dictionary_of_dataframes_even_when_one_is_empty(
    mocker, mock_sales_order_data
):
    """Test function returns dictionary even if one dataframe is empty."""
    mocker.patch.object(
        PandaTransformation,
        "transform_currency_data",
        return_value=pd.DataFrame(mock_sales_order_data),
    )
    mocker.patch.object(
        PandaTransformation,
        "transform_location_data",
        return_value=pd.DataFrame(mock_sales_order_data),
    )
    mocker.patch.object(
        PandaTransformation,
        "transform_staff_data",
        return_value=pd.DataFrame(mock_sales_order_data),
    )
    mocker.patch.object(
        PandaTransformation,
        "transform_design_data",
        return_value=pd.DataFrame(mock_sales_order_data),
    )
    mocker.patch.object(
        PandaTransformation,
        "transform_counterparty_data",
        return_value=pd.DataFrame(mock_sales_order_data),
    )
    mocker.patch.object(
        PandaTransformation, "transform_date_data", return_value=None
    )
    mocker.patch.object(
        PandaTransformation,
        "transform_sales_order_data",
        return_value=pd.DataFrame(mock_sales_order_data),
    )

    test_instance = PandaTransformation()
    result = test_instance.returns_dictionary_of_dataframes()

    expected_keys = [
        "dim_currency",
        "dim_location",
        "dim_staff",
        "dim_design",
        "dim_counterparty",
        "fact_sales_order",
    ]

    assert len(result.keys()) == 6
    assert "dim_date" not in result.keys()
    assert list(result.keys()) == expected_keys
