import sys
import os
from pathlib import Path
import subprocess
import shlex

def locate_executable(command):
    path = os.getenv("PATH")
    for p in path.split(":"):
        cmd_path = Path(p) / command
        if cmd_path.is_file() and os.access(cmd_path, os.X_OK):
            return cmd_path
    return None

def process_redirect(command):
    output_file = None
    append_output_file = None
    error_file = None
    append_error_file = None
    if "2>>" in command:
        command, append_error_file = command.split("2>>", 1)
    elif "1>>" in command:
        command, append_output_file = command.split("1>>", 1)
    elif ">>" in command:
        command, append_output_file = command.split(">>", 1)
    elif "1>" in command:
        command, output_file = command.split("1>", 1)
    elif "2>" in command:
        command, error_file = command.split("2>", 1)
    elif ">" in command:
        command, output_file = command.split(">", 1)
    return command, output_file, append_output_file, error_file, append_error_file

def append_to_file(output_file, msg):
    with open(output_file, "a") as f:
        f.write(msg)

def write_to_file(output_file, msg):
    with open(output_file, "w") as f:
        f.write(msg)

def main():
    builtin_commands = ["type", "echo", "exit", "pwd", "cd"]
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        command = input()
        args, output_file, append_output_file, error_file, append_error_file = process_redirect(command)
        args = args.strip()
        if output_file:
            output_file = output_file.strip()
        if error_file:
            error_file = error_file.strip()
        if append_output_file:
            append_output_file = append_output_file.strip()
        if append_error_file:
            append_error_file = append_error_file.strip()
        tokens = shlex.split(args, posix=True)
        if tokens[0] == "exit" and len(tokens) > 1 and tokens[1] == "0":
            break
        elif tokens[0] == "echo":
            final_msg = " ".join(tokens[1:])
            if output_file:
                write_to_file(output_file, final_msg + "\n")
            elif error_file:
                write_to_file(error_file, "")
                print(final_msg)
            elif append_output_file:
                append_to_file(append_output_file, final_msg + "\n")
            elif append_error_file:
                append_to_file(append_error_file, final_msg)
            else:
                print(final_msg)
        elif tokens[0] == "type":
            if tokens[1] in builtin_commands:
                print(f"{tokens[1]} is a shell builtin")
            else:
                cmd_path = locate_executable(tokens[1])
                if cmd_path:
                    print(f"{tokens[1]} is {cmd_path}")
                else:
                    print(f"{tokens[1]}: not found")
        elif locate_executable(tokens[0]):
            executable_path = locate_executable(tokens[0])
            if output_file:
                with open(output_file, "w") as f:
                    subprocess.run([executable_path, *tokens[1:]], stdout=f)
            elif error_file:
                with open(error_file, "w") as f:
                    subprocess.run([executable_path, *tokens[1:]], stderr=f)
            elif append_output_file:
                with open(append_output_file, "a") as f:
                    subprocess.run([executable_path, *tokens[1:]], stdout=f)
            elif append_error_file:
                with open(append_error_file, "a") as f:
                    subprocess.run([executable_path, *tokens[1:]], stderr=f)
            else:
                subprocess.run([executable_path, *tokens[1:]])
        elif tokens[0] == "pwd":
            print(Path.cwd().resolve())
        elif tokens[0] == "cd":
            change_path = Path(tokens[1]).expanduser().resolve()
            if change_path.exists():
                os.chdir(change_path)
            else:
                print(f"cd: {change_path}: No such file or directory")
        else:
            print(f"{args}: command not found")

if __name__ == "__main__":
    main()
