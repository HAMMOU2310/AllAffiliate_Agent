"""Root pytest configuration for AllAffiliate_Agent.

Registers custom markers to suppress warnings during normal test runs.
"""


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: marks tests that require real external API access "
        "(deselect with '-m not integration')",
    )
