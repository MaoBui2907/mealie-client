#!/usr/bin/env python3
"""
Advanced version bump script.

Usage::
    # Bump patch version
    python scripts/bump_version.py patch

    # Bump minor version
    python scripts/bump_version.py minor

    # Bump major version
    python scripts/bump_version.py major

    # Set explicit version
    python scripts/bump_version.py 1.2.3

    # Specify module file to update
    python scripts/bump_version.py patch --module-path src/mealie_client/__init__.py
"""
import re
import sys
import argparse
from pathlib import Path

def bump_version(version_str, bump_type="patch"):
    """Bump version based on semantic versioning."""
    parts = list(map(int, version_str.split('.')))
    
    if bump_type == "major":
        parts[0] += 1
        parts[1] = 0
        parts[2] = 0
    elif bump_type == "minor":
        parts[1] += 1
        parts[2] = 0
    elif bump_type == "patch":
        parts[2] += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return '.'.join(map(str, parts))

def update_pyproject_version(new_version):
    """Update version in pyproject.toml file."""
    pyproject_path = Path("pyproject.toml")
    
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found!")
        return False
    
    content = pyproject_path.read_text(encoding='utf-8')
    
    # Update version line
    version_pattern = r'version = "([^"]+)"'
    new_content = re.sub(version_pattern, f'version = "{new_version}"', content)
    
    if content == new_content:
        print("❌ Version line not found in pyproject.toml!")
        return False
    
    pyproject_path.write_text(new_content, encoding='utf-8')
    return True


def update_module_version(module_path: str, new_version: str) -> bool:
    """Update __version__ variable inside a given module file.

    Args:
        module_path: Path to the module file (relative to project root).
        new_version: The version string to set.

    Returns:
        True if update succeeded, False otherwise.
    """
    path = Path(module_path)
    if not path.exists():
        print(f"❌ Module file not found: {module_path}")
        return False

    content = path.read_text(encoding="utf-8")

    version_pattern = r'__version__\s*=\s*"[^"]+"'
    if not re.search(version_pattern, content):
        print("❌ __version__ declaration not found in module file!")
        return False

    new_content = re.sub(version_pattern, f'__version__ = "{new_version}"', content)
    path.write_text(new_content, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="Bump version in pyproject.toml")
    # Positional argument: bump_type or explicit version string
    parser.add_argument(
        "bump_type",
        nargs="?",
        default="patch",
        help=(
            "Type of version bump (patch|minor|major) or explicit version string. "
            "Defaults to 'patch' if omitted."
        ),
    )

    # Optional module path where __version__ is declared
    parser.add_argument(
        "--module-path",
        dest="module_path",
        default="src/mealie_client/__init__.py",
        help="Path to the module file containing __version__ variable to update",
    )
         
    args = parser.parse_args()

    # Allow direct version setting (e.g., 1.2.3)
    bump_type_or_version = args.bump_type
    
    # Read current version
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found!")
        sys.exit(1)
    
    content = pyproject_path.read_text(encoding='utf-8')
    version_match = re.search(r'version = "([^"]+)"', content)
    
    if not version_match:
        print("❌ Version not found in pyproject.toml!")
        sys.exit(1)
    
    current_version = version_match.group(1)

    # Determine new version based on user input
    semver_pattern = r"^\d+\.\d+\.\d+$"

    if re.match(semver_pattern, bump_type_or_version):
        new_version = bump_type_or_version
    elif bump_type_or_version in {"patch", "minor", "major"}:
        new_version = bump_version(current_version, bump_type_or_version)
    else:
        print(f"❌ Invalid argument: {bump_type_or_version}. Provide 'patch', 'minor', 'major' or an explicit version like 1.2.3")
        sys.exit(1)
    
    print(f"🔄 Bumping version: {current_version} → {new_version}")
    
    if update_pyproject_version(new_version):
        print("✅ pyproject.toml version updated!")
    else:
        print("❌ Failed to update version in pyproject.toml!")
        sys.exit(1)

    # Update module __version__
    if update_module_version(args.module_path, new_version):
        print(f"✅ {args.module_path} __version__ updated!")
    else:
        # Not fatal but warn user
        print("⚠️  Skipped updating module version (see message above).")

    print("💡 Remember to rebuild: pdm build")
    print(f"📦 Current version: {new_version}")

if __name__ == "__main__":
    main() 