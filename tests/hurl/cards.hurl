# Cards Endpoint Tests

# Test cards list endpoint - default parameters (combined scope may be empty)
GET http://localhost:8000/api/cards
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists
jsonpath "$.pagination.page" == 1
jsonpath "$.pagination.limit" == 50


# Test cards list with reference scope (has data)
GET http://localhost:8000/api/cards?scope=reference
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists
jsonpath "$.pagination.total" > 0
jsonpath "$.data[0].image_url" exists


# Test cards list with search query
GET http://localhost:8000/api/cards?q=Lightning&scope=reference
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test cards list with set filter
GET http://localhost:8000/api/cards?set=LEA&scope=reference
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test cards list with rarity filter
GET http://localhost:8000/api/cards?rarity=mythic&scope=reference
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test cards list with type filter
GET http://localhost:8000/api/cards?type=Creature&scope=reference
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test cards list with color filter
GET http://localhost:8000/api/cards?colors=R&scope=reference
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test cards list with price range
GET http://localhost:8000/api/cards?price_min=1&price_max=10&scope=reference
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test cards list with sorting
GET http://localhost:8000/api/cards?sort=price&order=desc&scope=reference
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test cards list with pagination
GET http://localhost:8000/api/cards?page=2&limit=10&scope=reference
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination.page" == 2
jsonpath "$.pagination.limit" == 10


# Test cards list - combined filters
GET http://localhost:8000/api/cards?q=Dragon&type=Creature&colors=R&rarity=rare&limit=5&scope=reference
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination.limit" == 5


# Capture a card UUID for subsequent tests
GET http://localhost:8000/api/cards?limit=1&scope=reference
HTTP 200
[Captures]
card_uuid: jsonpath "$.data[0].uuid"
[Asserts]
jsonpath "$.data[0].uuid" exists
jsonpath "$.data[0].name" exists


# Test get single card by UUID
GET http://localhost:8000/api/cards/{{card_uuid}}?scope=reference
HTTP 200
[Asserts]
jsonpath "$.uuid" exists
jsonpath "$.name" exists
jsonpath "$.prices" exists
jsonpath "$.legalities" exists


# Test get single card with combined scope
GET http://localhost:8000/api/cards/{{card_uuid}}?scope=combined
HTTP 200
[Asserts]
jsonpath "$.uuid" exists
jsonpath "$.name" exists


# Test card not found
GET http://localhost:8000/api/cards/00000000-0000-0000-0000-000000000000?scope=reference
HTTP 404


# Test invalid scope parameter
GET http://localhost:8000/api/cards?scope=invalid
HTTP 422


# Test invalid sort order
GET http://localhost:8000/api/cards?order=invalid
HTTP 422


# Test page must be positive
GET http://localhost:8000/api/cards?page=0
HTTP 422


# Test limit bounds
GET http://localhost:8000/api/cards?limit=101
HTTP 422
