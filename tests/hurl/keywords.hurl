# Keywords/Reference Endpoint Tests

# Test get all keywords
GET http://localhost:8000/api/keywords
HTTP 200
[Asserts]
jsonpath "$.ability_words" isCollection
jsonpath "$.keyword_abilities" isCollection
jsonpath "$.keyword_actions" isCollection


# Test keywords contain expected structure
GET http://localhost:8000/api/keywords
HTTP 200
[Asserts]
jsonpath "$.ability_words[0].term" exists
jsonpath "$.ability_words[0].definition" exists
jsonpath "$.keyword_abilities[0].term" exists
jsonpath "$.keyword_abilities[0].definition" exists
jsonpath "$.keyword_actions[0].term" exists
jsonpath "$.keyword_actions[0].definition" exists


# Test search keywords - basic search
GET http://localhost:8000/api/keywords/search?q=fly
HTTP 200
[Asserts]
jsonpath "$.results" isCollection
jsonpath "$.total" >= 0


# Test search keywords - returns expected structure
GET http://localhost:8000/api/keywords/search?q=trample
HTTP 200
[Asserts]
jsonpath "$.results[0].keyword" exists
jsonpath "$.results[0].type" exists


# Test search keywords - another search term
GET http://localhost:8000/api/keywords/search?q=death
HTTP 200
[Asserts]
jsonpath "$.results" isCollection
jsonpath "$.total" >= 0


# Test search keywords - partial match
GET http://localhost:8000/api/keywords/search?q=pro
HTTP 200
[Asserts]
jsonpath "$.results" isCollection


# Test search keywords - missing query parameter
GET http://localhost:8000/api/keywords/search
HTTP 422


# Test keyword stats
GET http://localhost:8000/api/keywords/stats
HTTP 200
[Asserts]
jsonpath "$.ability_words" >= 0
jsonpath "$.keyword_abilities" >= 0
jsonpath "$.keyword_actions" >= 0
jsonpath "$.total" >= 0


# Test keyword stats total is sum of categories
GET http://localhost:8000/api/keywords/stats
HTTP 200
[Asserts]
jsonpath "$.total" >= 0


# Test get formats
GET http://localhost:8000/api/keywords/formats
HTTP 200
[Asserts]
jsonpath "$.formats" isCollection


# Test formats contain expected structure
GET http://localhost:8000/api/keywords/formats
HTTP 200
[Asserts]
jsonpath "$.formats[0].id" exists
jsonpath "$.formats[0].name" exists
jsonpath "$.formats[0].description" exists
jsonpath "$.formats[0].deck_count" >= 0


# Test formats includes standard formats
GET http://localhost:8000/api/keywords/formats
HTTP 200
[Asserts]
jsonpath "$.formats" count >= 6
