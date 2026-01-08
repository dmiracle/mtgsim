# Statistics Endpoint Tests

# Test home stats endpoint
GET http://localhost:8000/api/stats/home
HTTP 200
[Asserts]
jsonpath "$.total_decks" >= 0
jsonpath "$.total_sets" >= 0
jsonpath "$.total_cards" >= 0
jsonpath "$.total_cards_with_prices" >= 0
jsonpath "$.format_distribution" exists
jsonpath "$.price_histogram" isCollection
jsonpath "$.recent_sets" isCollection
jsonpath "$.most_expensive_cards" isCollection


# Test home stats price histogram structure
GET http://localhost:8000/api/stats/home
HTTP 200
[Asserts]
jsonpath "$.price_histogram[0].range" exists
jsonpath "$.price_histogram[0].count" >= 0


# Test home stats recent sets structure
GET http://localhost:8000/api/stats/home
HTTP 200
[Asserts]
jsonpath "$.recent_sets[0].code" exists
jsonpath "$.recent_sets[0].name" exists
jsonpath "$.recent_sets[0].release_date" exists


# Test home stats most expensive cards structure
GET http://localhost:8000/api/stats/home
HTTP 200
[Asserts]
jsonpath "$.most_expensive_cards[0].name" exists
jsonpath "$.most_expensive_cards[0].price" >= 0
jsonpath "$.most_expensive_cards[0].set_code" exists


# Test deck stats endpoint
GET http://localhost:8000/api/stats/decks
HTTP 200
[Asserts]
jsonpath "$.by_format" exists
jsonpath "$.by_set" exists
jsonpath "$.by_color_combination" exists
jsonpath "$.price_distribution" isCollection
jsonpath "$.average_deck_price" >= 0
jsonpath "$.average_deck_size" >= 0


# Test deck stats price distribution structure
GET http://localhost:8000/api/stats/decks
HTTP 200
[Asserts]
jsonpath "$.price_distribution[0].range" exists
jsonpath "$.price_distribution[0].count" >= 0
