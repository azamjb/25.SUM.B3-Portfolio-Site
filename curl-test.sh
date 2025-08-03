#!/bin/bash

API_URL="https://azam-portfolio.duckdns.org/timeline"

# MySQL/MariaDB Credentials
USER="myportfolio"
PASSWORD="mypassword"
DATABASE="myportfoliodb"


generate_random_name() {
    local names=("Ryan" "Alice" "Bob" "Charlie" "Diana" "Frank")
    echo "${names[$RANDOM % ${#names[@]}]}"
}

generate_random_email() {
    local name=$(generate_random_name | tr '[:upper:]' '[:lower:]')
    local domains=("gmail.com" "yahoo.com" "outlook.com" "example.com")
    local domain="${domains[$RANDOM % ${#domains[@]}]}"
    echo "${name}${RANDOM:0:2}@${domain}"
}

generate_random_content() {
    local actions=("Updated portfolio" "Fixed a bug" "Deployed new feature" "Initialized database" "Pushed new commit")
    echo "${actions[$RANDOM % ${#actions[@]}]} - ID: ${RANDOM}"
}

# This will generate a random date within the last year
generate_random_date() {
    local random_days_ago=$((RANDOM % 365 + 1))
    date -d "${random_days_ago} days ago" "+%a, %d %B %Y %H:%M:%S PST"
}


make_post_request() {
    local name=$(generate_random_name)
    local email=$(generate_random_email)
    local content=$(generate_random_content)

    local created_at=$(generate_random_date)

    echo "---------------------------------"
    echo "Sending POST request with data:"
    echo "Name: $name"
    echo "Email: $email"
    echo "Content: $content"
    echo "Created At: $created_at"
    echo "---------------------------------"


    curl --location "${API_URL}" \
         --form "name=${name}" \
         --form "email=${email}" \
         --form "content=${content}" \
         --form "created_at=${created_at}"
    
    echo -e "\n"
}

make_delete_request() {
    local table=$(mariadb -u $USER -p$PASSWORD -D $DATABASE -e 'SHOW TABLES;' | tail -n +2)
    local max_id=$(mariadb -u $USER -p$PASSWORD -D $DATABASE -e "SELECT id FROM $table WHERE id=(SELECT MAX(id) FROM $table);" | tail -n 1)
    
    # Print Debug
    # echo "Table: $table"
    # echo "Max_ID: $max_id" 
    echo "---------------------------------"
    echo "Sending DELETE request with using id $max_id:"
    echo "---------------------------------"

    curl --location --request DELETE "${API_URL}/${max_id}"
    echo -e "\n"
}


make_get_request() {
    echo "---------------------------------"
    echo "Sending GET request to ${API_URL}"
    echo "---------------------------------"
    curl --location "${API_URL}"
    echo -e "\n"
}

make_get_request
make_post_request
make_delete_request
make_get_request


