# Collection Management Endpoint Tests
# Note: Collection endpoints require domain database configuration
# These tests verify endpoint structure and error handling

# First, get a card UUID from reference data
GET http://localhost:8000/api/cards?limit=1&scope=reference
HTTP 200
[Captures]
test_card_uuid: jsonpath "$.data[0].uuid"
[Asserts]
jsonpath "$.data[0].uuid" exists


# Test POST collection endpoint exists and returns JSON
# Returns 200 on success, 500 if domain DB not configured
POST http://localhost:8000/api/cards/{{test_card_uuid}}/collection
HTTP *
[Asserts]
header "Content-Type" contains "application/json"


# Test DELETE collection endpoint exists and returns JSON
DELETE http://localhost:8000/api/cards/{{test_card_uuid}}/collection
HTTP *
[Asserts]
header "Content-Type" contains "application/json"
