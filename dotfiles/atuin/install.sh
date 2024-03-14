#!/usr/bin/env bash

bash <(curl --proto '=https' --tlsv1.2 -sSf https://setup.atuin.sh)

name="janez"
email="janez@gmail.com"
atuin register -u $name -e $email
atuin import auto
atuin sync
