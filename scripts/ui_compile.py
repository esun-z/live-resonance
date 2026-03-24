import os
import subprocess
import sys

def compile_ui_files(ui_dir: str) -> None:
    for filename in os.listdir(ui_dir):
        if filename.endswith('.ui'):
            ui_path = os.path.join(ui_dir, filename)
            py_filename = f"ui_{os.path.splitext(filename)[0]}.py"
            py_path = os.path.join(ui_dir, py_filename)
            cmd = [
                'uv', 'run', 'pyside6-uic',
                ui_path, '-o', py_path
            ]
            print(f"Compiling {ui_path} -> {py_path}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error compiling {ui_path}:\n{result.stderr}")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ui_folder = os.path.join(project_root, 'ui')
    if not os.path.isdir(ui_folder):
        print(f"UI folder not found: {ui_folder}")
        sys.exit(1)
    compile_ui_files(ui_folder)
    print("UI compilation completed.")