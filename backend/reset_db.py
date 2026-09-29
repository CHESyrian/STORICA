#!/usr/bin/env python3

from pathlib import Path
import subprocess
import sys

import psycopg2


# ============================================================
# PostgreSQL configuration
# ============================================================

DB_NAME = "storica_db"
DB_USER = "admin"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"

# ============================================================
# Superuser configuration
# ============================================================

SUPERUSER_USERNAME = "admin"
SUPERUSER_EMAIL = "admin@storica.com"
SUPERUSER_PASSWORD = "password"

# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
MANAGE_PY = PROJECT_ROOT / "manage.py"


# ============================================================
# Helpers
# ============================================================

def run_command(*args: str) -> None:
    """Run a command and exit if it fails."""
    print(f"\n$ {' '.join(args)}")
    print("-" * 60)

    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        check=False,
    )

    if result.returncode != 0:
        print("\nERROR: Command failed.")
        sys.exit(result.returncode)


def remove_migrations() -> None:
    """Remove migration files while preserving __init__.py."""
    print("\n[1/5] Removing migration files...")

    deleted = 0

    for migrations_dir in PROJECT_ROOT.rglob("migrations"):
        if not migrations_dir.is_dir():
            continue

        for file in migrations_dir.iterdir():
            if not file.is_file():
                continue

            if file.name == "__init__.py":
                continue

            if file.suffix in {".py", ".pyc"}:
                print(f"  Deleting: {file.relative_to(PROJECT_ROOT)}")
                file.unlink()
                deleted += 1

    print(f"\nDeleted {deleted} migration files.")


def recreate_database() -> None:
    """Drop and recreate the PostgreSQL database."""
    print(f"\n[2/5] Recreating database: {DB_NAME}")

    connection = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )

    connection.autocommit = True

    try:
        with connection.cursor() as cursor:

            print("  Terminating existing connections...")

            cursor.execute(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s
                  AND pid <> pg_backend_pid();
                """,
                (DB_NAME,),
            )

            print(f"  Dropping database: {DB_NAME}")

            cursor.execute(
                f'DROP DATABASE IF EXISTS "{DB_NAME}";'
            )

            print(f"  Creating database: {DB_NAME}")

            cursor.execute(
                f'CREATE DATABASE "{DB_NAME}" OWNER "{DB_USER}";'
            )

    finally:
        connection.close()

    print("Database recreated successfully.")


def create_migrations() -> None:
    """Generate fresh Django migrations."""
    print("\n[3/5] Creating migrations...")

    run_command(
        sys.executable,
        "manage.py",
        "makemigrations",
    )


def apply_migrations() -> None:
    """Apply Django migrations."""
    print("\n[4/5] Applying migrations...")

    run_command(
        sys.executable,
        "manage.py",
        "migrate",
    )


def create_superuser() -> None:
    """Create the default Django superuser."""
    print("\n[5/5] Creating superuser...")

    command = [
        sys.executable,
        "manage.py",
        "shell",
        "-c",
        (
            "from django.contrib.auth import get_user_model; "
            "User = get_user_model(); "
            "username = 'admin'; "
            "email = 'admin@storica.com'; "
            "password = 'password'; "
            "user, created = User.objects.get_or_create("
            "username=username, "
            "defaults={'email': email, 'is_staff': True, "
            "'is_superuser': True}"
            "); "
            "user.email = email; "
            "user.set_password(password); "
            "user.is_staff = True; "
            "user.is_superuser = True; "
            "user.save(); "
            "print('Superuser created successfully.' if created "
            "else 'Superuser already existed and was updated.')"
        ),
    ]

    run_command(*command)


# ============================================================
# Main
# ============================================================

def main() -> None:
    """Reset Django migrations and PostgreSQL database."""
    print("=" * 65)
    print("Django + PostgreSQL Complete Reset")
    print("=" * 65)

    if not MANAGE_PY.exists():
        print("\nERROR: manage.py was not found.")
        print(f"Expected: {MANAGE_PY}")
        sys.exit(1)

    print(f"\nProject : {PROJECT_ROOT}")
    print(f"Database: {DB_NAME}")
    print(f"User    : {DB_USER}")

    print("\nWARNING!")
    print("This operation will permanently delete:")
    print("  - All Django migration files")
    print("  - All data in the PostgreSQL database")
    print("  - All existing users/data")

    confirmation = input(
        "\nType RESET to continue: "
    ).strip()

    if confirmation != "RESET":
        print("\nOperation cancelled.")
        return

    remove_migrations()
    recreate_database()
    create_migrations()
    apply_migrations()
    create_superuser()

    print("\n" + "=" * 65)
    print("RESET COMPLETED SUCCESSFULLY")
    print("=" * 65)

    print("\nAdmin account:")
    print(f"  Username: {SUPERUSER_USERNAME}")
    print(f"  Email:    {SUPERUSER_EMAIL}")
    print(f"  Password: {SUPERUSER_PASSWORD}")


if __name__ == "__main__":
    main()

