#!/bin/bash
run_makemigrations() {
    python manage.py makemigrations
}

run_migrate() {
    python manage.py migrate
}

run_server() {
    python manage.py runserver
}

echo "╭───────╮"
echo "│  🐍   │ Order Predection System"
echo "│       │"
echo "│ 1. Dev Server"
echo "│ 2. Run makemigrations"
echo "│ 3. Run migrate"
echo "│ 4. Exit"
echo "╰───────╯"

read -p "Enter your choice (1/2/3/4): " choice

case $choice in
    1)
        run_server
        ;;
    2)
        run_migrate
        ;;
    3)
        run_makemigrations
        ;;
    4)
        echo "Exiting."
        ;;
    *)
        echo "Invalid choice. Please enter 1, 2, 3, or 4."
        ;;
esac