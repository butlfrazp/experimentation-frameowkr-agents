from logging import DEBUG, Handler, LogRecord
from typing import List

import pytest

from exp_platform_cli.logger import ExperimentLogger, SUCCESS_LEVEL


@pytest.fixture
def exp_logger() -> ExperimentLogger:
    """Each test gets an isolated logger instance to avoid handler reuse."""
    return ExperimentLogger(name="test.exp.logger", level=DEBUG)


def test_success_level_registered(exp_logger: ExperimentLogger) -> None:
    records: List[LogRecord] = []

    class CaptureHandler(Handler):
        def emit(self, record: LogRecord) -> None:  # type: ignore[override]
            records.append(record)

    handler = CaptureHandler(level=SUCCESS_LEVEL)
    exp_logger.logger.addHandler(handler)

    try:
        exp_logger.success("Experiment complete")
    finally:
        exp_logger.logger.removeHandler(handler)

    assert records, "Expected to capture at least one log record"
    record = records[0]
    assert record.levelno == SUCCESS_LEVEL
    assert record.getMessage() == "[success]Experiment complete[/]"


def test_banner_outputs_rule(exp_logger: ExperimentLogger, capsys: pytest.CaptureFixture[str]) -> None:
    exp_logger.banner("My Banner")
    captured = capsys.readouterr()
    assert "My Banner" in captured.out
