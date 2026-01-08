# Prices Endpoint Tests

# Test prices list endpoint - default parameters
GET http://localhost:8000/api/prices
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists
jsonpath "$.pagination.page" == 1
jsonpath "$.pagination.limit" == 50
jsonpath "$.meta" exists
jsonpath "$.meta.last_updated" exists


# Test prices list with search query
GET http://localhost:8000/api/prices?q=Black%20Lotus
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test prices list with set filter
GET http://localhost:8000/api/prices?set=LEA
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test prices list with rarity filter
GET http://localhost:8000/api/prices?rarity=mythic
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test prices list with price range
GET http://localhost:8000/api/prices?price_min=10&price_max=100
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test prices list with sorting by average_usd (default)
GET http://localhost:8000/api/prices?sort=average_usd&order=desc
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test prices list with sorting by tcgplayer
GET http://localhost:8000/api/prices?sort=tcgplayer&order=desc
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test prices list with sorting by cardkingdom
GET http://localhost:8000/api/prices?sort=cardkingdom&order=asc
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test prices list with pagination
GET http://localhost:8000/api/prices?page=1&limit=10
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination.page" == 1
jsonpath "$.pagination.limit" == 10


# Capture a card UUID for price detail test
GET http://localhost:8000/api/prices?limit=1
HTTP 200
[Captures]
price_uuid: jsonpath "$.data[0].uuid"
[Asserts]
jsonpath "$.data[0].uuid" exists
jsonpath "$.data[0].name" exists
jsonpath "$.data[0].prices" exists


# Test price list item structure
GET http://localhost:8000/api/prices?limit=1
HTTP 200
[Asserts]
jsonpath "$.data[0].set_code" exists
jsonpath "$.data[0].rarity" exists
jsonpath "$.data[0].average_usd" exists


# Test get single price detail by UUID
GET http://localhost:8000/api/prices/{{price_uuid}}
HTTP 200
[Asserts]
jsonpath "$.uuid" exists
jsonpath "$.name" exists
jsonpath "$.set_code" exists
jsonpath "$.paper" exists
jsonpath "$.mtgo" exists


# Test price detail paper structure
GET http://localhost:8000/api/prices/{{price_uuid}}
HTTP 200
[Asserts]
jsonpath "$.paper.tcgplayer" exists
jsonpath "$.paper.cardkingdom" exists
jsonpath "$.paper.cardsphere" exists
jsonpath "$.paper.cardmarket" exists


# Test price not found
GET http://localhost:8000/api/prices/00000000-0000-0000-0000-000000000000
HTTP 404


# Test invalid sort order
GET http://localhost:8000/api/prices?order=invalid
HTTP 422


# Test page must be positive
GET http://localhost:8000/api/prices?page=0
HTTP 422


# Test limit bounds
GET http://localhost:8000/api/prices?limit=101
HTTP 422


# Test combined filters
GET http://localhost:8000/api/prices?q=Dragon&rarity=rare&price_min=5&limit=5
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination.limit" == 5
