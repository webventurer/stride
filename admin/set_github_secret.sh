#!/bin/bash

cd ..

if [ -f .env ]; then
  export $(grep -v '^#' .env.keys | xargs)
else
  echo ".env.keys file not found!"
  exit 1
fi

gh secret set DOTENV_PRIVATE_KEY_VAULT -b"$DOTENV_PRIVATE_KEY_VAULT"
