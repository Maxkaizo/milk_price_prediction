# Unit Testing

## commands

pytest tests/unit/test_check_file_availability.py
pytest tests/unit/test_notify_telegram.py 

## Testing log

### First Test

(milk_price_prediction) maxkaizo@max:~/milk_price_prediction$ pytest tests/unit/test_check_file_availability.py
=========================================================================== test session starts ============================================================================
platform linux -- Python 3.12.3, pytest-8.4.1, pluggy-1.6.0
rootdir: /home/maxkaizo/milk_price_prediction
plugins: anyio-4.9.0, Faker-37.5.3
collected 2 items                                                                                                                                                          

tests/unit/test_check_file_availability.py ..                                                                                                                        [100%]

============================================================================= warnings summary =============================================================================
tests/unit/test_check_file_availability.py::test_future_date_returns_false
tests/unit/test_check_file_availability.py::test_past_date_returns_false
  /home/maxkaizo/.local/share/virtualenvs/milk_price_prediction-mju8LJeN/lib/python3.12/site-packages/botocore/auth.py:422: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    datetime_now = datetime.datetime.utcnow()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====================================================================== 2 passed, 2 warnings in 3.55s =======================================================================
(milk_price_prediction) maxkaizo@max:~/milk_price_prediction$ 

### Second Test

(milk_price_prediction) maxkaizo@max:~/milk_price_prediction$ pytest tests/unit/test_notify_telegram.py 
=========================================================================== test session starts ============================================================================
platform linux -- Python 3.12.3, pytest-8.4.1, pluggy-1.6.0
rootdir: /home/maxkaizo/milk_price_prediction
plugins: anyio-4.9.0, Faker-37.5.3
collected 1 item                                                                                                                                                           

tests/unit/test_notify_telegram.py .                                                                                                                                 [100%]

============================================================================ 1 passed in 1.55s =============================================================================
(milk_price_prediction) maxkaizo@max:~/milk_price_prediction$ 

# Integration Testing

## command
pytest tests/integration/test_prepare_dataset_integration.py 

## Log


(milk_price_prediction) maxkaizo@max:~/milk_price_prediction$ pytest tests/integration/test_prepare_dataset_integration.py 
=========================================================================== test session starts ============================================================================
platform linux -- Python 3.12.3, pytest-8.4.1, pluggy-1.6.0
rootdir: /home/maxkaizo/milk_price_prediction
plugins: anyio-4.9.0, Faker-37.5.3
collected 1 item                                                                                                                                                           

tests/integration/test_prepare_dataset_integration.py .                                                                                                              [100%]

============================================================================= warnings summary =============================================================================
tests/integration/test_prepare_dataset_integration.py::test_dataset_generation_hash
  /home/maxkaizo/.local/share/virtualenvs/milk_price_prediction-mju8LJeN/lib/python3.12/site-packages/fsspec/registry.py:298: UserWarning: Your installed version of s3fs is very old and known to cause
  severe performance issues, see also https://github.com/dask/dask/issues/10276
  
  To fix, you should specify a lower version bound on s3fs, or
  update the current installation.
  
    warnings.warn(s3_msg)

tests/integration/test_prepare_dataset_integration.py: 470 warnings
  /home/maxkaizo/.local/share/virtualenvs/milk_price_prediction-mju8LJeN/lib/python3.12/site-packages/botocore/auth.py:422: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    datetime_now = datetime.datetime.utcnow()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================================================================ 1 passed, 471 warnings in 61.13s (0:01:01) ================================================================
(milk_price_prediction) maxkaizo@max:~/milk_price_prediction$ 


