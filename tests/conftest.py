NO_TESTS_COLLECTED = 5
SUCCESS = 0


def pytest_sessionfinish(session, exitstatus):
    if exitstatus == NO_TESTS_COLLECTED and session.config.getoption("-k"):
        session.exitstatus = SUCCESS
