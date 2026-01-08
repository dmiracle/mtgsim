# Health and Root Endpoint Tests

# Test root endpoint returns API info
GET http://localhost:8000/
HTTP 200
[Asserts]
jsonpath "$.name" == "MTG Webapp API"
jsonpath "$.version" exists
jsonpath "$.docs" == "/docs"
jsonpath "$.openapi" == "/openapi.json"
jsonpath "$.endpoints" exists


# Test health check endpoint
GET http://localhost:8000/health
HTTP 200
[Asserts]
jsonpath "$.status" == "healthy"


# Test OpenAPI spec is accessible
GET http://localhost:8000/openapi.json
HTTP 200
[Asserts]
jsonpath "$.openapi" startsWith "3."
jsonpath "$.info.title" == "MTG Webapp API"
jsonpath "$.paths" exists
