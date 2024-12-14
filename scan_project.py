import os
import mimetypes
from pathlib import Path


def scan_project_files(root_dir='.'):
    """
    Recursively scan directory and output filenames and their content.
    Binary files (like images) will only have their filenames listed.

    Args:
        root_dir (str): Root directory to start scanning from
    """
    # Initialize mimetypes
    mimetypes.init()

    # Text file extensions to always read
    text_extensions = {
        '.txt', '.py', '.js', '.html', '.css', '.json', '.md',
        '.yaml', '.yml', '.toml', '.ini', '.cfg'
    }

    # Virtual environment directory names
    venv_patterns = {
        'venv', 'env', '.venv', '.env',
        'virtualenv', 'virtual_env',
        'Lib/site-packages',  # Common in Windows venvs
        'lib/site-packages',  # Common in Unix venvs
        'lib/python',  # Catches lib/python3.x/site-packages
    }

    # Directories and files to ignore
    ignore_patterns = {
        # Output directory
        'project_contents',
        # Git directories
        '.git',
        # Python cache directories
        '__pycache__',
        # Node modules
        'node_modules',
        # IDE directories
        '.idea', '.vscode',
        # Build directories
        'build', 'dist',
        # Compiled Python files
        '.pyc',
        # Package directories
        'egg-info',
    }

    def should_ignore(path):
        """Check if the path should be ignored"""
        path_str = str(Path(path))

        # Check for virtual environment patterns
        for venv_pattern in venv_patterns:
            if venv_pattern in path_str:
                return True

        # Check other ignore patterns
        for ignore in ignore_patterns:
            if ignore in path_str:
                return True

        # Ignore this script itself
        if Path(path).name == os.path.basename(__file__):
            return True

        return False

    def is_text_file(file_path):
        """Determine if a file is a text file based on mimetype or extension"""
        mime_type, _ = mimetypes.guess_type(file_path)
        extension = Path(file_path).suffix.lower()

        if extension in text_extensions:
            return True
        if mime_type and mime_type.startswith('text/'):
            return True
        return False

    def process_file(file_path):
        """Process a single file and return its information"""
        try:
            if is_text_file(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return f"\n{'=' * 80}\nFile: {file_path}\nContent:\n{content}\n"
            else:
                return f"\n{'=' * 80}\nBinary File: {file_path}\n"
        except Exception as e:
            return f"\n{'=' * 80}\nError reading {file_path}: {str(e)}\n"

    # Create output directory if it doesn't exist
    output_dir = Path('project_contents')
    output_dir.mkdir(exist_ok=True)

    # Walk through directory and process files
    all_content = []
    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in place to skip ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(d)]

        for file in files:
            file_path = Path(root) / file
            # Skip ignored files
            if should_ignore(file_path):
                continue
            all_content.append(process_file(file_path))

    # Write to output file
    output_file = output_dir / 'project_contents.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_content))

    print(f"Project contents have been written to {output_file}")


if __name__ == '__main__':
    scan_project_files()