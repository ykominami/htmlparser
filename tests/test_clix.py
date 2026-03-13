import argparse
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

import htmlparser.clix as clix_module
from htmlparser.clix import Clix, main


class FakeSubapp:
    def __init__(self) -> None:
        self.links_assoc: dict[str, dict[str, str]] = {}

    def run(self, env: Any) -> None:
        pattern = env.pattern
        if pattern is None:
            raise AssertionError("pattern must be set before run()")

        self.links_assoc[f"generated-{pattern}"] = {
            "title": f"title-{pattern}",
            "url": f"https://example.com/{pattern}",
        }


@pytest.fixture
def clix() -> Clix:
    return Clix("test cli")


def write_yaml(path: Path, data: Any) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def create_config_file(
    tmp_path: Path,
    *,
    config_data: dict[str, Any] | list[Any] | str,
) -> Path:
    config_path = tmp_path / "config.yaml"
    write_yaml(config_path, config_data)
    return config_path


def create_db_file(tmp_path: Path, data: dict[str, Any]) -> Path:
    db_path = tmp_path / "data.yaml"
    write_yaml(db_path, data)
    return db_path


def create_run_files(tmp_path: Path, *, patterns: list[str]) -> Path:
    app_config_path = tmp_path / "app.yaml"
    app_config_data: dict[str, Any] = {"base_path": ["."]}
    for pattern in patterns:
        app_config_data[pattern] = {}
    write_yaml(app_config_path, app_config_data)

    config_path = create_config_file(
        tmp_path,
        config_data={
            "db_kind": "yaml",
            "db_file": "data.yaml",
            "config_file": "app.yaml",
            "patterns": patterns,
        },
    )
    return config_path


def parse_args(clix: Clix, argv: list[str]) -> argparse.Namespace:
    parser = clix.cli.get_parser()
    return parser.parse_args(argv)


def run_main_with_argv(monkeypatch: pytest.MonkeyPatch, argv: list[str]) -> int:
    monkeypatch.setattr(sys, "argv", argv)
    return main()


def test_run_clear_count_and_print_list_text_commands_are_available(clix: Clix) -> None:
    run_args = parse_args(clix, ["run", "config.yaml"])
    clear_args = parse_args(clix, ["clear", "config.yaml"])
    count_args = parse_args(clix, ["count", "config.yaml"])
    print_args = parse_args(clix, ["print-list-text", "config.yaml"])

    assert run_args.command == "run"
    assert clear_args.command == "clear"
    assert count_args.command == "count"
    assert print_args.command == "print-list-text"
    assert callable(run_args.func)
    assert callable(clear_args.func)
    assert callable(count_args.func)
    assert callable(print_args.func)
    assert print_args.key == "title"


@pytest.mark.parametrize(
    "command",
    ["run", "clear", "count", "print-list-text"],
    ids=[
        "全コマンドでconfig_fileが必須引数として要求されること-run",
        "全コマンドでconfig_fileが必須引数として要求されること-clear",
        "全コマンドでconfig_fileが必須引数として要求されること-count",
        "全コマンドでconfig_fileが必須引数として要求されること-print-list-text",
    ],
)
def test_all_commands_require_config_file(clix: Clix, command: str) -> None:
    with pytest.raises(SystemExit):
        parse_args(clix, [command])


def test_existing_db_count_is_printed_and_zero_is_returned(
    clix: Clix, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    create_db_file(
        tmp_path,
        {
            "item1": {"title": "title-1", "url": "https://example.com/1"},
            "item2": {"title": "title-2", "url": "https://example.com/2"},
        },
    )
    config_path = create_config_file(
        tmp_path,
        config_data={"db_kind": "yaml", "db_file": "data.yaml"},
    )

    ret = clix.count_command(argparse.Namespace(config_file=str(config_path)))

    captured = capsys.readouterr()
    assert ret == 0
    assert "count=2" in captured.out


def test_empty_db_count_is_printed_as_zero_and_data_remains_empty(
    clix: Clix, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db_path = create_db_file(tmp_path, {})
    config_path = create_config_file(
        tmp_path,
        config_data={"db_kind": "yaml", "db_file": "data.yaml"},
    )

    ret = clix.count_command(argparse.Namespace(config_file=str(config_path)))

    captured = capsys.readouterr()
    assert ret == 0
    assert "count=0" in captured.out
    assert load_yaml(db_path) == {}


def test_print_list_text_uses_title_when_key_is_omitted(
    clix: Clix, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    create_db_file(
        tmp_path,
        {
            "item1": {"title": "title-1", "url": "https://example.com/1"},
            "item2": {"title": "title-2", "url": "https://example.com/2"},
        },
    )
    args = parse_args(
        clix,
        [
            "print-list-text",
            str(
                create_config_file(
                    tmp_path,
                    config_data={"db_kind": "yaml", "db_file": "data.yaml"},
                )
            ),
        ],
    )

    ret = clix.print_list_text_command(args)

    captured = capsys.readouterr()
    assert ret == 0
    assert "title-1" in captured.out
    assert "title-2" in captured.out


def test_print_list_text_uses_explicit_key_when_key_is_specified(
    clix: Clix, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    create_db_file(
        tmp_path,
        {
            "item1": {"title": "title-1", "url": "https://example.com/1"},
            "item2": {"title": "title-2", "url": "https://example.com/2"},
        },
    )
    config_path = create_config_file(
        tmp_path,
        config_data={"db_kind": "yaml", "db_file": "data.yaml"},
    )

    ret = clix.print_list_text_command(
        argparse.Namespace(config_file=str(config_path), key="url")
    )

    captured = capsys.readouterr()
    assert ret == 0
    assert "https://example.com/1" in captured.out
    assert "https://example.com/2" in captured.out


def test_clear_removes_all_db_entries_and_saves_empty_db(clix: Clix, tmp_path: Path) -> None:
    db_path = create_db_file(
        tmp_path,
        {
            "item1": {"title": "title-1", "url": "https://example.com/1"},
            "item2": {"title": "title-2", "url": "https://example.com/2"},
        },
    )
    config_path = create_config_file(
        tmp_path,
        config_data={"db_kind": "yaml", "db_file": "data.yaml"},
    )

    ret = clix.clear_command(argparse.Namespace(config_file=str(config_path)))

    assert ret == 0
    assert load_yaml(db_path) == {}


def test_clear_keeps_empty_db_empty(clix: Clix, tmp_path: Path) -> None:
    db_path = create_db_file(tmp_path, {})
    config_path = create_config_file(
        tmp_path,
        config_data={"db_kind": "yaml", "db_file": "data.yaml"},
    )

    ret = clix.clear_command(argparse.Namespace(config_file=str(config_path)))

    assert ret == 0
    assert load_yaml(db_path) == {}


def test_run_merges_existing_db_and_new_results_then_prints_count(
    clix: Clix,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(clix_module, "Subapp", FakeSubapp)
    db_path = create_db_file(
        tmp_path,
        {"item1": {"title": "title-1", "url": "https://example.com/1"}},
    )
    config_path = create_run_files(tmp_path, patterns=["pattern-a"])

    ret = clix.run_command(argparse.Namespace(config_file=str(config_path)))

    captured = capsys.readouterr()
    data = load_yaml(db_path)
    assert ret == 0
    assert "count=2" in captured.out
    assert data["item1"]["title"] == "title-1"
    assert data["generated-pattern-a"]["title"] == "title-pattern-a"


def test_run_processes_multiple_patterns_and_saves_all_results(
    clix: Clix,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(clix_module, "Subapp", FakeSubapp)
    db_path = create_db_file(tmp_path, {})
    config_path = create_run_files(tmp_path, patterns=["pattern-a", "pattern-b"])

    ret = clix.run_command(argparse.Namespace(config_file=str(config_path)))

    captured = capsys.readouterr()
    data = load_yaml(db_path)
    assert ret == 0
    assert "count=2" in captured.out
    assert set(data) == {"generated-pattern-a", "generated-pattern-b"}


def test_config_file_must_be_set_before_processing_starts(clix: Clix) -> None:
    with pytest.raises(ValueError, match="config_file is not set"):
        clix.count_command(argparse.Namespace())


def test_empty_config_file_is_rejected_before_processing_starts(clix: Clix) -> None:
    with pytest.raises(ValueError, match="config_file is empty"):
        clix.count_command(argparse.Namespace(config_file=""))


def test_config_yaml_must_contain_mapping(clix: Clix, tmp_path: Path) -> None:
    config_path = create_config_file(tmp_path, config_data=["not", "a", "mapping"])

    with pytest.raises(ValueError, match="config file must contain a mapping"):
        clix.count_command(argparse.Namespace(config_file=str(config_path)))


def test_db_file_is_required_for_runtime_initialization(clix: Clix, tmp_path: Path) -> None:
    config_path = create_config_file(tmp_path, config_data={"db_kind": "yaml"})

    with pytest.raises(ValueError, match="db_file is not set"):
        clix.count_command(argparse.Namespace(config_file=str(config_path)))


def test_db_kind_is_required_for_runtime_initialization(clix: Clix, tmp_path: Path) -> None:
    config_path = create_config_file(tmp_path, config_data={"db_file": "data.yaml"})

    with pytest.raises(ValueError, match="db_kind is not set"):
        clix.count_command(argparse.Namespace(config_file=str(config_path)))


def test_unsupported_db_kind_is_rejected(clix: Clix, tmp_path: Path) -> None:
    config_path = create_config_file(
        tmp_path,
        config_data={"db_kind": "unsupported", "db_file": "data.yaml"},
    )

    with pytest.raises(ValueError, match="unsupported db_kind=unsupported"):
        clix.count_command(argparse.Namespace(config_file=str(config_path)))


def test_run_fails_when_pattern_selection_is_invalid_and_does_not_save_partial_state(
    clix: Clix, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(clix_module, "Subapp", FakeSubapp)
    db_path = create_db_file(
        tmp_path,
        {"item1": {"title": "title-1", "url": "https://example.com/1"}},
    )
    app_config_path = tmp_path / "app.yaml"
    write_yaml(app_config_path, {"base_path": ["."]})
    config_path = create_config_file(
        tmp_path,
        config_data={
            "db_kind": "yaml",
            "db_file": "data.yaml",
            "config_file": "app.yaml",
            "patterns": ["missing-pattern"],
        },
    )

    before = db_path.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="invalid result ret=None pattern=missing-pattern"):
        clix.run_command(argparse.Namespace(config_file=str(config_path)))

    after = db_path.read_text(encoding="utf-8")
    assert after == before


def test_main_returns_zero_for_count_command_and_prints_count(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    create_db_file(
        tmp_path,
        {
            "item1": {"title": "title-1", "url": "https://example.com/1"},
            "item2": {"title": "title-2", "url": "https://example.com/2"},
        },
    )
    config_path = create_config_file(
        tmp_path,
        config_data={"db_kind": "yaml", "db_file": "data.yaml"},
    )

    ret = run_main_with_argv(monkeypatch, ["htmlparser", "count", str(config_path)])

    captured = capsys.readouterr()
    assert ret == 0
    assert "count=2" in captured.out


def test_main_uses_title_as_default_key_for_print_list_text(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    create_db_file(
        tmp_path,
        {
            "item1": {"title": "title-1", "url": "https://example.com/1"},
            "item2": {"title": "title-2", "url": "https://example.com/2"},
        },
    )
    config_path = create_config_file(
        tmp_path,
        config_data={"db_kind": "yaml", "db_file": "data.yaml"},
    )

    ret = run_main_with_argv(
        monkeypatch, ["htmlparser", "print-list-text", str(config_path)]
    )

    captured = capsys.readouterr()
    assert ret == 0
    assert "title-1" in captured.out
    assert "title-2" in captured.out


def test_main_returns_zero_for_run_command_and_saves_generated_results(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(clix_module, "Subapp", FakeSubapp)
    db_path = create_db_file(
        tmp_path,
        {"item1": {"title": "title-1", "url": "https://example.com/1"}},
    )
    config_path = create_run_files(tmp_path, patterns=["pattern-a"])

    ret = run_main_with_argv(monkeypatch, ["htmlparser", "run", str(config_path)])

    captured = capsys.readouterr()
    data = load_yaml(db_path)
    assert ret == 0
    assert "count=2" in captured.out
    assert data["item1"]["title"] == "title-1"
    assert data["generated-pattern-a"]["title"] == "title-pattern-a"


def test_main_exits_when_required_config_file_argument_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        run_main_with_argv(monkeypatch, ["htmlparser", "count"])

    assert exc_info.value.code == 2
