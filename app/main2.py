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
    elif "2>" in command:
        command, error_file = command.split("2>", 1)
    elif "1>>" in command:
        command, append_output_file = command.split("1>>", 1)
    elif ">>" in command:
        command, append_output_file = command.split(">>", 1)
    elif "1>" in command:
        command, output_file = command.split("1>", 1)
    elif ">" in command:
        command, output_file = command.split(">", 1)
    return (command.strip(),
            output_file.strip() if output_file else None,
            append_output_file.strip() if append_output_file else None,
            error_file.strip() if error_file else None,
            append_error_file.strip() if append_error_file else None)

def append_to_file(filepath, msg):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "a") as f:
        f.write(msg)

def write_to_file(filepath, msg):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(msg)

def main():
    builtin_commands = ["type", "echo", "cat", "exit", "pwd", "cd"]
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        line = input()
        cmd_line, out_file, app_out_file, err_file, app_err_file = process_redirect(line)
        tokens = shlex.split(cmd_line, posix=True)
        if not tokens:
            continue
        if tokens[0] == "exit":
            break
        elif tokens[0] == "echo":
            final_msg = " ".join(tokens[1:])
            # For echo, if error redirection is specified, write to file and do not print.
            if err_file:
                write_to_file(err_file, final_msg + "\n")
            elif app_err_file:
                append_to_file(app_err_file, final_msg + "\n")
                print(final_msg)
            elif out_file:
                write_to_file(out_file, final_msg + "\n")
            elif app_out_file:
                append_to_file(app_out_file, final_msg + "\n")
            else:
                print(final_msg)
        elif tokens[0] == "cat":
            final_output = ""
            if len(tokens) < 2:
                final_output = "cat: missing operand\n"
            else:
                for filename in tokens[1:]:
                    try:
                        with open(filename, "r") as f:
                            final_output += f.read()
                    except FileNotFoundError:
                        final_output += f"cat: {filename}: No such file or directory\n"
                    except Exception as e:
                        final_output += f"cat: {filename}: {str(e)}\n"
            if out_file:
                write_to_file(out_file, final_output)
            elif app_out_file:
                append_to_file(app_out_file, final_output)
            elif err_file:
                write_to_file(err_file, final_output)
            elif app_err_file:
                append_to_file(app_err_file, final_output)
            else:
                print(final_output, end="")
        elif tokens[0] == "type":
            if tokens[1] in builtin_commands:
                print(f"{tokens[1]} is a shell builtin")
            else:
                path_found = locate_executable(tokens[1])
                if path_found:
                    print(f"{tokens[1]} is {path_found}")
                else:
                    print(f"{tokens[1]}: not found")
        elif tokens[0] == "pwd":
            print(Path.cwd().resolve())
        elif tokens[0] == "cd":
            if len(tokens) < 2:
                print("cd: missing operand")
            else:
                target = Path(tokens[1]).expanduser().resolve()
                if target.exists():
                    os.chdir(target)
                else:
                    print(f"cd: {target}: No such file or directory")
        elif locate_executable(tokens[0]):
            exe_path = locate_executable(tokens[0])
            new_args = [os.path.basename(exe_path)] + tokens[1:]
            proc_kwargs = {}
            if out_file:
                os.makedirs(os.path.dirname(out_file), exist_ok=True)
                proc_kwargs["stdout"] = open(out_file, "w")
            if app_out_file:
                os.makedirs(os.path.dirname(app_out_file), exist_ok=True)
                proc_kwargs["stdout"] = open(app_out_file, "a")
            if err_file:
                os.makedirs(os.path.dirname(err_file), exist_ok=True)
                proc_kwargs["stderr"] = open(err_file, "w")
            if app_err_file:
                os.makedirs(os.path.dirname(app_err_file), exist_ok=True)
                proc_kwargs["stderr"] = open(app_err_file, "a")
            subprocess.run(new_args, executable=str(exe_path), **proc_kwargs)
            for stream in proc_kwargs.values():
                stream.close()
        else:
            print(f"{cmd_line}: command not found")

if __name__ == "__main__":
    main()