# Stack Overflow - https://stackoverflow.com/questions/27064004/splitting-a-conftest-py-file-into-several-smaller-conftest-like-parts/27068195#27068195
pytest_plugins = [
    "tests.fixtures.fill_by_data",
    "tests.fixtures.write_and_read",
    "tests.fixtures.get_clients",
    "tests.fixtures.requests"
]