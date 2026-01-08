#!/bin/bash
# Run all Hurl API tests
# Usage: ./run_tests.sh [--test] [--report]
#
# Options:
#   --test    Run in test mode (fail on first error)
#   --report  Generate HTML report
#
# Requirements:
#   - API must be running at http://localhost:8000
#   - hurl must be installed (brew install hurl)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default options
TEST_MODE=""
REPORT_MODE=""

# Parse arguments
for arg in "$@"; do
    case $arg in
        --test)
            TEST_MODE="--test"
            ;;
        --report)
            REPORT_MODE="--report-html $SCRIPT_DIR/report.html"
            ;;
    esac
done

echo "Running Hurl API tests..."
echo "========================="

# Run all .hurl files in order
hurl $TEST_MODE $REPORT_MODE --variables-file /dev/null \
    "$SCRIPT_DIR/health.hurl" \
    "$SCRIPT_DIR/cards.hurl" \
    "$SCRIPT_DIR/decks.hurl" \
    "$SCRIPT_DIR/sets.hurl" \
    "$SCRIPT_DIR/prices.hurl" \
    "$SCRIPT_DIR/stats.hurl" \
    "$SCRIPT_DIR/keywords.hurl" \
    "$SCRIPT_DIR/collection.hurl"

echo ""
echo "All tests passed!"
