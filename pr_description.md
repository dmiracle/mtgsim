# Domain-API Consolidation: Core Infrastructure Implementation

## Overview

This PR implements the core infrastructure for the domain-API consolidation feature, completing tasks 1-6 of the implementation plan. The changes establish a unified domain database architecture that consolidates reference data and domain models while maintaining full backward compatibility.

## Key Changes

### 1. Domain Database Schema & Models ✅
- **Enhanced Domain Models**: Extended `DomainCard`, `DomainSet`, and `DomainDeck` with all fields required by API responses
- **Reference Table Models**: Added `MTGJsonCard`, `MTGJsonSet`, `MTGJsonDeck` models for complete MTGJSON data copies
- **Migration Infrastructure**: Implemented `MigrationLog`, `SchemaVersion`, and `DataIntegrityCheck` for tracking operations
- **Relationship Support**: Added proper SQLModel relationships with link tables for colors, types, and subtypes

### 2. Reference Table Sync System ✅
- **CLI Commands**: Implemented `domain sync-reference` and `domain sync-mtgjson` commands
- **Table Copying**: Added `copy_table_with_prefix()` utility for syncing reference data with `mtgjson_` prefix
- **Schema Validation**: Added pre-sync validation to ensure source database compatibility
- **Integrity Verification**: Post-sync row count verification with detailed logging

### 3. Domain Entity Management ✅
- **Entity Addition Commands**: Implemented `domain add-card`, `domain add-set`, and `domain add-deck` CLI commands
- **Data Transformation**: Added transformation functions from reference models to enhanced domain models
- **Collection Tracking**: Added metadata fields for tracking user-selected entities with timestamps and sources
- **Mana Cost Parsing**: Implemented parsing of mana cost strings into individual color components

### 4. Data Access Layer Refactoring ✅
- **Scope-Based Querying**: Updated data access classes to support `user`, `reference`, and `combined` scopes
- **Domain Database Integration**: Modified `CardsData`, `SetsData`, `DecksData` to query unified domain database
- **Conversion Utilities**: Added comprehensive conversion functions between reference and domain models
- **API Compatibility**: Maintained existing error handling and response formats

### 5. API Service Layer Updates ✅
- **Dual Model Support**: Updated services to handle both domain and reference card types seamlessly
- **Collection Management**: Added logic to distinguish between user collection and reference data
- **Response Consistency**: Ensured identical API response structures across all scopes
- **Enhanced Endpoints**: Added collection management capabilities while preserving existing functionality

### 6. Comprehensive Property-Based Testing ✅
- **Domain Model Completeness**: Tests verify all API fields have corresponding domain model fields
- **Sync Integrity**: Property tests ensure reference table sync preserves all data with correct prefixes
- **Sync Idempotence**: Tests verify repeated sync operations produce identical results
- **Entity Addition Correctness**: Tests ensure domain entities preserve all reference data during transformation
- **API Response Compatibility**: Tests verify identical response structures across user/reference scopes
- **Collection Management Consistency**: Tests ensure collection operations maintain data integrity
- **Query Compatibility**: Tests verify reference table queries work identically in domain database

## Architecture Benefits

### Unified Data Access
- Single domain database contains both reference tables (`mtgjson_*`) and user domain tables
- Eliminates API dependency on multiple reference databases
- Enables efficient scope-based querying (user collection vs all available data)

### Enhanced Domain Models
- Domain models now contain all data needed for API responses
- Proper relationships and computed properties for complex data access
- Metadata tracking for user collection management

### Backward Compatibility
- All existing API endpoints return identical response structures
- Same query parameters and filtering options continue to work
- Graceful error handling maintained throughout

### Scalable Collection Management
- Users can selectively add cards/sets/decks to their domain tables
- Efficient querying of user collection vs reference data
- Proper tracking of addition timestamps and data sources

## Testing Coverage

- **Property-Based Tests**: 10 comprehensive property tests covering universal correctness properties
- **Unit Tests**: Focused tests for CLI commands, data transformations, and API endpoints
- **Integration Tests**: End-to-end testing of sync operations and collection management
- **Hypothesis Framework**: Generates thousands of test cases to verify properties across all inputs

## Database Schema

The domain database now contains:
- **Reference Tables**: Complete copies of MTGJSON data with `mtgjson_` prefix
- **Domain Tables**: User-selected entities with enhanced fields and relationships
- **Migration Tables**: Comprehensive logging and integrity tracking
- **Link Tables**: Proper normalization for colors, types, and subtypes

## CLI Commands Added

```bash
# Initialize domain database
uv run mtgsim domain init

# Sync reference data
uv run mtgsim domain sync-reference

# Add entities to collection
uv run mtgsim domain add-card <uuid>
uv run mtgsim domain add-set <code>
uv run mtgsim domain add-deck <uuid>

# Check status
uv run mtgsim domain status
```

## API Enhancements

- **Scope Parameter**: All endpoints now support `?scope=user|reference|combined`
- **Collection Status**: All responses include `in_collection` field
- **Identical Responses**: Same JSON structure regardless of data source
- **Enhanced Metadata**: Domain entities include collection timestamps and sources

## Performance Improvements

- **Single Database**: Eliminates need for multiple database connections
- **Indexed Queries**: Proper indexing on UUID, name, set_code, and other frequently queried fields
- **Efficient Relationships**: SQLModel relationships enable optimized joins
- **Selective Loading**: Users only load data they need into domain tables

## Next Steps (Future PRs)

- Task 7: Rollback and comprehensive logging capabilities
- Task 8: Architectural boundary validation and final compatibility testing
- Task 9: Complete system validation and performance optimization

## Testing Instructions

```bash
# Run all tests
uv run pytest

# Run property-based tests specifically
uv run pytest tests/test_*_property*.py -v

# Test CLI commands
uv run mtgsim domain init
uv run mtgsim domain sync-reference
uv run mtgsim domain status

# Test API with different scopes
curl "http://localhost:8000/api/cards?scope=user"
curl "http://localhost:8000/api/cards?scope=reference"
curl "http://localhost:8000/api/cards?scope=combined"
```

## Breaking Changes

None. This implementation maintains full backward compatibility with existing API consumers.

## Version Bump

Bumped patch version to 0.2.4 to reflect the substantial infrastructure improvements while maintaining API compatibility.