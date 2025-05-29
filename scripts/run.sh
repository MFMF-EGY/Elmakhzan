#!/bin/bash
name=$(basename $0)
db_password="000600"

if [ "$name" = "setup_database.sh" ]; then
  # check if mariadb is installed
  if ! [ -x "$(command -v mariadb)" ]; then
    echo 'Error: mariadb is not installed.' >&2
    exit 1
  fi
  # check if mariadb is running if not start it
  if ! systemctl is-active --quiet mariadb; then
    sudo systemctl start mariadb
  fi
  # check if MainDB database exists if not create it
  mariadb -u root -p"$db_password" -e "
    CREATE DATABASE IF NOT EXISTS MainDB;
    USE MainDB;
    CREATE TABLE IF NOT EXISTS Projects_Table (
      Project_ID INT AUTO_INCREMENT,
      Project_Name VARCHAR(255) NOT NULL,
      Project_Description TEXT,
      PRIMARY KEY (Project_ID)
    );"
fi
