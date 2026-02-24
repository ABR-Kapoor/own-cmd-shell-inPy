import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

BUILTINS = {"echo", "exit", "type", "pwd", "cd"}
REDIRECTS = {
    ">": ("stdout", "w"),
    ">>": ("stdout", "a"),
    "1>": ("stdout", "w"),
    "1>>": ("stdout", "a"),
    "2>": ("stderr", "w"),
    "2>>": ("stderr", "a"),
}


def ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def parse_command(line: str):
    tokens = shlex.split(line, posix=True)
    if not tokens:
        return None
    argv = []
    stdout_target = None
    stderr_target = None
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token in REDIRECTS and i + 1 < len(tokens):
            stream, mode = REDIRECTS[token]
            target = (tokens[i + 1], mode)
            if stream == "stdout":
                stdout_target = target
            else:
                stderr_target = target
            i += 2
            continue
        argv.append(token)
        i += 1
    return argv, stdout_target, stderr_target


def write_text(text: str, target, default_stream) -> None:
    if target:
        path, mode = target
        ensure_parent(path)
        with open(path, mode, encoding="utf-8") as f:
            f.write(text)
    else:
        default_stream.write(text)


def run_builtin(argv, stdout_target, stderr_target) -> bool:
    cmd = argv[0]
    args = argv[1:]
    if cmd == "exit":
        code = int(args[0]) if args else 0
        raise SystemExit(code)
    if cmd == "echo":
        write_text(" ".join(args) + "\n", stdout_target, sys.stdout)
        return True
    if cmd == "type":
        if not args:
            write_text("type: missing operand\n", stderr_target, sys.stderr)
            return True
        target = args[0]
        if target in BUILTINS:
            write_text(f"{target} is a shell builtin\n", stdout_target, sys.stdout)
        else:
            found = shutil.which(target)
            if found:
                write_text(f"{target} is {found}\n", stdout_target, sys.stdout)
            else:
                write_text(f"{target}: not found\n", stdout_target, sys.stdout)
        return True
    if cmd == "pwd":
        if args:
            write_text("pwd: too many arguments\n", stderr_target, sys.stderr)
        else:
            write_text(str(Path.cwd()) + "\n", stdout_target, sys.stdout)
        return True
    if cmd == "cd":
        target = args[0] if args else "~"
        target = os.path.expanduser(target)
        try:
            os.chdir(target)
        except OSError:
            write_text(f"cd: {target}: No such file or directory\n", stderr_target, sys.stderr)
        return True
    return False


def run_external(argv, stdout_target, stderr_target) -> None:
    stdout_handle = None
    stderr_handle = None
    if stdout_target:
        path, mode = stdout_target
        ensure_parent(path)
        stdout_handle = open(path, mode, encoding="utf-8")
    if stderr_target:
        path, mode = stderr_target
        ensure_parent(path)
        stderr_handle = open(path, mode, encoding="utf-8")
    try:
        subprocess.run(argv, stdout=stdout_handle, stderr=stderr_handle, check=False)
    finally:
        if stdout_handle:
            stdout_handle.close()
        if stderr_handle:
            stderr_handle.close()


def main() -> None:
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        line = input()
        parsed = parse_command(line)
        if not parsed:
            continue
        argv, stdout_target, stderr_target = parsed
        if not argv:
            continue
        if argv[0] in BUILTINS:
            try:
                run_builtin(argv, stdout_target, stderr_target)
            except SystemExit as exc:
                raise SystemExit(exc.code)
            continue
        if shutil.which(argv[0]):
            run_external(argv, stdout_target, stderr_target)
        else:
            write_text(f"{argv[0]}: command not found\n", stderr_target, sys.stderr)


if __name__ == "__main__":
    main()