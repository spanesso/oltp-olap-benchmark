import pytest

from nyc311_bench.db import read_sql, run_sql_file


class RecordingConnection:
    def __init__(self):
        self.executed = []

    def execute(self, sql):
        self.executed.append(sql)


def test_read_sql_returns_the_file_text(tmp_path):
    (tmp_path / "oltp").mkdir()
    (tmp_path / "oltp" / "q.sql").write_text("SELECT 1;\n")
    assert read_sql("oltp/q.sql", tmp_path) == "SELECT 1;\n"


def test_read_sql_reports_a_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="oltp/absent.sql"):
        read_sql("oltp/absent.sql", tmp_path)


def test_read_sql_refuses_paths_outside_the_sql_directory(tmp_path):
    sql_dir = tmp_path / "sql"
    sql_dir.mkdir()
    (tmp_path / "secret.sql").write_text("SELECT 'no';")
    with pytest.raises(ValueError, match="escapes"):
        read_sql("../secret.sql", sql_dir)


def test_run_sql_file_executes_the_whole_file(tmp_path):
    (tmp_path / "schema.sql").write_text("CREATE TABLE a (x int);\nCREATE TABLE b (y int);\n")
    connection = RecordingConnection()
    run_sql_file(connection, "schema.sql", tmp_path)
    assert connection.executed == ["CREATE TABLE a (x int);\nCREATE TABLE b (y int);\n"]
