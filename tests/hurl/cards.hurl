# Cards Endpoint Tests

# Test cards list endpoint - default parameters
GET http://localhost:8000/api/cards
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists
jsonpath "$.pagination.page" == 1
jsonpath "$.pagination.limit" == 50


# Test cards list with search query
GET http://localhost:8000/api/cards?q=Lightning
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test cards list with owns filter
GET http://localhost:8000/api/cards?owns=true
HTTP 200
[Asserts]
jsonpath "$.data" isCollection


# Test cards list with wants filter
GET http://localhost:8000/api/cards?wants=true
HTTP 200
[Asserts]
jsonpath "$.data" isCollection


# Test cards list with set filter
GET http://localhost:8000/api/cards?set=LEA
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test cards list with rarity filter
GET http://localhost:8000/api/cards?rarity=mythic
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test cards list with type filter
GET http://localhost:8000/api/cards?type=Creature
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test cards list with color filter
GET http://localhost:8000/api/cards?colors=R
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test cards list with price range
GET http://localhost:8000/api/cards?price_min=1&price_max=10
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test cards list with sorting
GET http://localhost:8000/api/cards?sort=price&order=desc
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test cards list with pagination
GET http://localhost:8000/api/cards?page=1&limit=10
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination.page" == 1
jsonpath "$.pagination.limit" == 10


# Test cards list - combined filters
GET http://localhost:8000/api/cards?q=Dragon&type=Creature&colors=R&rarity=rare&limit=5
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination.limit" == 5


# Capture a card UUID for subsequent tests
GET http://localhost:8000/api/cards?limit=1
HTTP 200
[Captures]
card_uuid: jsonpath "$.data[0].uuid"
[Asserts]
jsonpath "$.data[0].uuid" exists
jsonpath "$.data[0].name" exists
jsonpath "$.data[0].owns" exists
jsonpath "$.data[0].total_owned" exists


# Test get single card by UUID
GET http://localhost:8000/api/cards/{{card_uuid}}
HTTP 200
[Asserts]
jsonpath "$.uuid" exists
jsonpath "$.name" exists
jsonpath "$.prices" exists
jsonpath "$.legalities" exists
jsonpath "$.owns" exists
jsonpath "$.total_owned" exists


# Test card not found
GET http://localhost:8000/api/cards/00000000-0000-0000-0000-000000000000
HTTP 404


# Test invalid sort order
GET http://localhost:8000/api/cards?order=invalid
HTTP 422


# Test page must be positive
GET http://localhost:8000/api/cards?page=0
HTTP 422


# Test limit bounds
GET http://localhost:8000/api/cards?limit=101
HTTP 422
