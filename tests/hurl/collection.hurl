# Collection Management Endpoint Tests

# First, get a card UUID from data
GET http://localhost:8000/api/cards?limit=1
HTTP 200
[Captures]
test_card_uuid: jsonpath "$.data[0].uuid"
[Asserts]
jsonpath "$.data[0].uuid" exists


# Test POST collection endpoint - add card to collection
POST http://localhost:8000/api/cards/{{test_card_uuid}}/collection?quantity_owned=4
HTTP 200
[Asserts]
header "Content-Type" contains "application/json"
jsonpath "$.success" == true


# Verify card shows as owned
GET http://localhost:8000/api/cards/{{test_card_uuid}}
HTTP 200
[Asserts]
jsonpath "$.owns" == true
jsonpath "$.total_owned" == 4


# Update quantities - add wanted
POST http://localhost:8000/api/cards/{{test_card_uuid}}/collection?quantity_owned=2&quantity_wanted=1
HTTP 200
[Asserts]
jsonpath "$.success" == true


# Verify updates
GET http://localhost:8000/api/cards/{{test_card_uuid}}
HTTP 200
[Asserts]
jsonpath "$.owns" == true
jsonpath "$.wants" == true
jsonpath "$.total_owned" == 2
jsonpath "$.total_wanted" == 1


# Test DELETE collection endpoint - remove card from collection
DELETE http://localhost:8000/api/cards/{{test_card_uuid}}/collection
HTTP 200
[Asserts]
header "Content-Type" contains "application/json"
jsonpath "$.success" == true


# Verify removed
GET http://localhost:8000/api/cards/{{test_card_uuid}}
HTTP 200
[Asserts]
jsonpath "$.owns" == false
jsonpath "$.total_owned" == 0
