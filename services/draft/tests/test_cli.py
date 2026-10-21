"""E4 骨架的单元测试。E5/E6 实现方法后，在这里继续添加测试。"""
from draft import __version__
from draft.cli import build_parser, main


def test_version(capsys):
    assert main(["version"]) == 0
    assert capsys.readouterr().out.strip() == f"draft {__version__}"


def test_smoke_defaults():
    args = build_parser().parse_args(["smoke"])
    assert args.fixture == "fixtures/draft"
    assert args.tag == "e4-smoke-broken:latest"


def test_smoke_reports_missing_docker(monkeypatch):
    from draft import smoke
    monkeypatch.setattr(smoke, "run", lambda cmd, timeout=600: (127, "docker: not found"))
    result = smoke.run_smoke("fixtures/draft", "t")
    assert result["passed"] is False
    assert "docker.sock" in result["hint"]


def test_smoke_keeps_error_line_before_log_tail(monkeypatch):
    from draft import smoke

    def fake_run(cmd, timeout=600):
        if cmd[:2] == ["docker", "version"]:
            return 0, "29.1.3"
        log = "/bin/sh: 1: make: not found\n" + "\n".join(f"later line {i}" for i in range(10))
        return 1, log

    monkeypatch.setattr(smoke, "run", fake_run)
    result = smoke.run_smoke("fixtures/draft", "e4-smoke-broken:test")
    assert result["passed"] is True
    assert result["make_error_line"] == "/bin/sh: 1: make: not found"
    assert all("make: not found" not in line for line in result["log_tail"])


def test_auto_build_requires_an_explicit_candidate():
    import pytest

    with pytest.raises(SystemExit):
        build_parser().parse_args(["auto-build", "--out", "work/test", "--expected-output", "hello E3"])


def test_auto_build_reports_success(monkeypatch, capsys):
    import json
    from draft import cli

    calls = []

    def fake_auto_build(*args):
        calls.append(args)
        return {"status": "SUCCEEDED", "candidate_source": args[-1]}

    monkeypatch.setattr(cli, "auto_build", fake_auto_build)
    code = main([
        "auto-build", "--candidate", "fixtures/ci-candidates/DeepSeek-E5.Dockerfile",
        "--out", "work/test", "--expected-output", "hello E3",
        "--candidate-source", "teaching-replay",
    ])
    assert code == 0
    assert json.loads(capsys.readouterr().out)["candidate_source"] == "teaching-replay"
    assert calls[0][-1] == "teaching-replay"
