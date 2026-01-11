# Decks Endpoint Tests

# Test decks list endpoint - default parameters
GET http://localhost:8000/api/decks
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists
jsonpath "$.pagination.page" == 1
jsonpath "$.pagination.limit" == 50
jsonpath "$.filters" exists


# Test decks list with search query
GET http://localhost:8000/api/decks?q=Commander
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test decks list with format filter
GET http://localhost:8000/api/decks?format=commander
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test decks list with set filter
GET http://localhost:8000/api/decks?set=KLD
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test decks list with type filter (deck size)
GET http://localhost:8000/api/decks?type=100
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test decks list with color filter
GET http://localhost:8000/api/decks?colors=WU
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test decks list with source filter - precon
GET http://localhost:8000/api/decks?source=precon
HTTP 200
[Asserts]
jsonpath "$.data" isCollection


# Test decks list with source filter - user
GET http://localhost:8000/api/decks?source=user
HTTP 200
[Asserts]
jsonpath "$.data" isCollection


# Test decks list with card count range
GET http://localhost:8000/api/decks?card_count_min=60&card_count_max=100
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test decks list with price range
GET http://localhost:8000/api/decks?price_min=10&price_max=500
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test decks list with sorting by release_date
GET http://localhost:8000/api/decks?sort=release_date&order=desc
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test decks list with sorting by price
GET http://localhost:8000/api/decks?sort=price&order=asc
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test decks list with pagination
GET http://localhost:8000/api/decks?page=1&limit=5
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination.page" == 1
jsonpath "$.pagination.limit" == 5


# Capture a deck file for subsequent tests
GET http://localhost:8000/api/decks?limit=1
HTTP 200
[Captures]
deck_file: jsonpath "$.data[0].file"
[Asserts]
jsonpath "$.data[0].file" exists
jsonpath "$.data[0].name" exists
jsonpath "$.data[0].source" exists


# Test get single deck by file
GET http://localhost:8000/api/decks/{{deck_file}}
HTTP 200
[Asserts]
jsonpath "$.meta" exists
jsonpath "$.meta.file" exists
jsonpath "$.meta.name" exists
jsonpath "$.meta.source" exists
jsonpath "$.legality" exists
jsonpath "$.colors" isCollection
jsonpath "$.price" exists
jsonpath "$.stats" exists


# Test deck detail has expected stats structure
GET http://localhost:8000/api/decks/{{deck_file}}
HTTP 200
[Asserts]
jsonpath "$.stats.total_cards" >= 0
jsonpath "$.stats.unique_cards" >= 0
jsonpath "$.stats.mana_curve" exists
jsonpath "$.stats.type_distribution" exists
jsonpath "$.stats.rarity_distribution" exists


# Test deck cards have ownership info
GET http://localhost:8000/api/decks/{{deck_file}}
HTTP 200
[Asserts]
jsonpath "$.main_board" isCollection


# Test get raw deck JSON
GET http://localhost:8000/api/decks/{{deck_file}}/raw
HTTP 200
[Asserts]
header "Content-Type" contains "application/json"


# Test deck not found
GET http://localhost:8000/api/decks/nonexistent_deck_file_12345.json
HTTP 404


# Test invalid sort order
GET http://localhost:8000/api/decks?order=invalid
HTTP 422


# Test page must be positive
GET http://localhost:8000/api/decks?page=0
HTTP 422


# Test limit bounds
GET http://localhost:8000/api/decks?limit=101
HTTP 422
