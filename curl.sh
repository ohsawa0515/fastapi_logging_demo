#!/bin/bash

URL='http://localhost:8000'

# GET
curl ${URL}/

curl ${URL}/items/12?foo=bar

# POST
curl -X POST "${URL}/items/" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"name\":\"foo\",\"price\":1234,\"is_offer\":true}"

# PUT
curl -X PUT "${URL}/items/5678" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"name\":\"foo\",\"price\":100,\"is_offer\":true}"

# Occur error
curl ${URL}/exception
curl -X POST ${URL}/exception

# Validation error(price is invalid)
curl -X POST "${URL}/items/" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"name\":\"foo\",\"price\":abcd,\"is_offer\":true}"
