# Sets Endpoint Tests

# Test sets list endpoint - default parameters
GET http://localhost:8000/api/sets
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists
jsonpath "$.pagination.page" == 1
jsonpath "$.pagination.limit" == 50
jsonpath "$.filters" exists
jsonpath "$.filters.types" isCollection
jsonpath "$.filters.blocks" isCollection


# Test sets list with search query
GET http://localhost:8000/api/sets?q=Dominaria
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test sets list with type filter
GET http://localhost:8000/api/sets?type=expansion
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test sets list with block filter
GET http://localhost:8000/api/sets?block=Ravnica
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test sets list with has_owned_cards filter
GET http://localhost:8000/api/sets?has_owned_cards=true
HTTP 200
[Asserts]
jsonpath "$.data" isCollection


# Test sets list with sorting by name
GET http://localhost:8000/api/sets?sort=name&order=asc
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test sets list with sorting by release_date desc (default)
GET http://localhost:8000/api/sets?sort=release_date&order=desc
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test sets list with sorting by size
GET http://localhost:8000/api/sets?sort=size&order=desc
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test sets list with pagination
GET http://localhost:8000/api/sets?page=1&limit=10
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination.page" == 1
jsonpath "$.pagination.limit" == 10


# Capture a set code for subsequent tests
GET http://localhost:8000/api/sets?limit=1
HTTP 200
[Captures]
set_code: jsonpath "$.data[0].code"
[Asserts]
jsonpath "$.data[0].code" exists
jsonpath "$.data[0].name" exists


# Test get single set by code
GET http://localhost:8000/api/sets/{{set_code}}
HTTP 200
[Asserts]
jsonpath "$.meta" exists
jsonpath "$.meta.code" exists
jsonpath "$.meta.name" exists
jsonpath "$.stats" exists
jsonpath "$.cards" exists
jsonpath "$.cards.data" isCollection
jsonpath "$.cards.pagination" exists


# Test set detail stats structure
GET http://localhost:8000/api/sets/{{set_code}}
HTTP 200
[Asserts]
jsonpath "$.stats.rarity_count" exists
jsonpath "$.stats.price" exists


# Test get set with card filters - by rarity
GET http://localhost:8000/api/sets/{{set_code}}?rarity=rare
HTTP 200
[Asserts]
jsonpath "$.cards.data" isCollection


# Test get set with card filters - by color
GET http://localhost:8000/api/sets/{{set_code}}?color=W
HTTP 200
[Asserts]
jsonpath "$.cards.data" isCollection


# Test get set with card filters - by type
GET http://localhost:8000/api/sets/{{set_code}}?type=Creature
HTTP 200
[Asserts]
jsonpath "$.cards.data" isCollection


# Test get set with owns filter
GET http://localhost:8000/api/sets/{{set_code}}?owns=true
HTTP 200
[Asserts]
jsonpath "$.cards.data" isCollection


# Test get set with card pagination
GET http://localhost:8000/api/sets/{{set_code}}?card_page=1&card_limit=10
HTTP 200
[Asserts]
jsonpath "$.cards.pagination.page" == 1
jsonpath "$.cards.pagination.limit" == 10


# Test get raw set JSON
GET http://localhost:8000/api/sets/{{set_code}}/raw
HTTP 200
[Asserts]
header "Content-Type" contains "application/json"


# Test set not found
GET http://localhost:8000/api/sets/NOTASET
HTTP 404


# Test invalid sort order
GET http://localhost:8000/api/sets?order=invalid
HTTP 422


# Test page must be positive
GET http://localhost:8000/api/sets?page=0
HTTP 422


# Test limit bounds
GET http://localhost:8000/api/sets?limit=101
HTTP 422
