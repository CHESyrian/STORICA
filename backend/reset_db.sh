#!/usr/bin/env bash

set -e

# ============================================================
# PostgreSQL configuration
# ============================================================

DB_NAME="storica_db"
DB_USER="admin"
DB_PASSWORD="password"
DB_HOST="localhost"
DB_PORT="5432"

export PGPASSWORD="$DB_PASSWORD"

# ============================================================
# Superuser configuration
# ============================================================

SUPERUSER_USERNAME="admin"
SUPERUSER_EMAIL="admin@storica.com"
SUPERUSER_PASSWORD="password"


# ============================================================
# Colors
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'


# ============================================================
# Check Django project
# ============================================================

echo "============================================================"
echo " Django + PostgreSQL Complete Reset"
echo "============================================================"

if [[ ! -f "manage.py" ]]; then
    echo -e "${RED}ERROR: manage.py not found.${NC}"
    echo
    echo "Run this script from your Django project root."
    exit 1
fi


# ============================================================
# Display configuration
# ============================================================

echo
echo "Project : $(pwd)"
echo "Database: $DB_NAME"
echo "User    : $DB_USER"
echo "Host    : $DB_HOST"
echo "Port    : $DB_PORT"

echo
echo "Superuser:"
echo "  Username: $SUPERUSER_USERNAME"
echo "  Email   : $SUPERUSER_EMAIL"


# ============================================================
# Confirmation
# ============================================================

echo
echo -e "${RED}WARNING!${NC}"
echo
echo "This will permanently DELETE:"
echo "  - All Django migration files"
echo "  - All data in $DB_NAME"
echo "  - All existing users"
echo

read -r -p "Type RESET to continue: " CONFIRMATION

if [[ "$CONFIRMATION" != "RESET" ]]; then
    echo
    echo "Operation cancelled."
    exit 0
fi


# ============================================================
# 1. Remove migrations
# ============================================================

echo
echo "[1/5] Removing Django migration files..."
echo

find . \
    -type f \
    -path "*/migrations/*.py" \
    ! -name "__init__.py" \
    -print \
    -delete

find . \
    -type f \
    -path "*/migrations/*.pyc" \
    -print \
    -delete

echo
echo "Migration files removed."


# ============================================================
# 2. Drop database
# ============================================================

echo
echo "[2/5] Dropping PostgreSQL database..."

psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d postgres \
    -c "
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = '$DB_NAME'
          AND pid <> pg_backend_pid();
    " \
    > /dev/null

dropdb \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    --if-exists \
    "$DB_NAME"

echo "Database dropped."


# ============================================================
# 3. Create database
# ============================================================

echo
echo "[3/5] Creating PostgreSQL database..."

createdb \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -O "$DB_USER" \
    "$DB_NAME"

echo "Database created."


# ============================================================
# 4. Django migrations
# ============================================================

echo
echo "[4/5] Creating Django migrations..."

python manage.py makemigrations

echo
echo "Applying migrations..."

python manage.py migrate


# ============================================================
# 5. Create superuser
# ============================================================

echo
echo "[5/5] Creating superuser..."

python manage.py shell -c "
from django.contrib.auth import get_user_model

User = get_user_model()

username = '$SUPERUSER_USERNAME'
email = '$SUPERUSER_EMAIL'
password = '$SUPERUSER_PASSWORD'

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        'email': email,
        'is_staff': True,
        'is_superuser': True,
    }
)

user.email = email
user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.save()

if created:
    print('Superuser created successfully.')
else:
    print('Superuser already existed and was updated.')
"


# ============================================================
# Finished
# ============================================================

echo
echo "============================================================"
echo -e "${GREEN} RESET COMPLETED SUCCESSFULLY ${NC}"
echo "============================================================"

echo
echo "Admin account:"
echo "  Username: $SUPERUSER_USERNAME"
echo "  Email   : $SUPERUSER_EMAIL"
echo "  Password: $SUPERUSER_PASSWORD"

echo

unset PGPASSWORD
