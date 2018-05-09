#!/bin/bash

DEBUG=1 # VERBOSE=1
INSTALL=""
DEPCHECK=""
DEPS=wmctrl
LSBRELEASE=$(awk -F = '/^NAME/' /etc/os-release)
DIST_ID=$(awk -F = '/^ID=/{print $2}' /etc/os-release)

APT_PM="debian ubuntu"
ZYPPER_PM="suse" 
EOPKG_PM="solus"
YUM_PM="fedora centos"

# some implementation of debugging print statements
function debug() {
    if [[ $DEBUG -eq 1 ]]; then
        echo "$1"
    fi
}

echo "DIST_ID=$DIST_ID"
echo "Checking distribution ID for specifying package manager..."

# regex expression match operator '=~'
function contains() {
    echo "Checking if "$2" in "$1""
    [[ $1 =~ (^|[[:space:]])$2($|[[:space:]]) ]] && return 0 || return 1
}

if (contains "$APT_PM" "$DIST_ID"); then
    echo "Using apt..."
    INSTALL="apt install" 
elif (contains "$ZYPPER_PM" "$DIST_ID"); then
    echo "Using zypper..."
    INSTALL="zypper install" 
elif (contains "$EOPKG_PM" "$DIST_ID"); then
    echo "Using eopkg..."
    INSTALL="eopkg install"
elif (contains "$YUM_PM" "$DIST_ID"); then
    echo "Using yum..."
    INSTALL="yum install" 
fi

if [ -z INSTALL ]; then
    echo "No suitable package manager found. Exiting."
    exit 1
fi    

for P in "$DEPS"; do
    echo "Checking dependency: "$P""
    sudo $INSTALL "$P"
done
echo "Finished"