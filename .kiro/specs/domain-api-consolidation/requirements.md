# Requirements Document

## Introduction

This feature consolidates the domain models and API models by extending the domain models to contain all data needed by the API, eliminating the API's dependency on reference databases. The API will use a unified domain database instead of multiple reference databases, with migrations to populate domain tables from reference data.

## Glossary

- **Domain_Database**: The unified SQLite database containing domain models with all necessary data for the application
- **Reference_Database**: The existing MTGJSON SQLite databases (AllSets.sqlite, AllDecks.sqlite, etc.) used as data sources
- **Domain_Model**: SQLModel classes representing the core business entities with full data requirements
- **API_Model**: Pydantic response models used by FastAPI endpoints
- **Migration_System**: CLI commands that populate domain database tables from reference database data
- **Data_Access_Layer**: The API data layer that queries databases

## Requirements

### Requirement 1

**User Story:** As a developer, I want unified domain models that contain all necessary data, so that the API can operate independently of reference databases.

#### Acceptance Criteria

1. THE Domain_Model SHALL contain all fields required by current API_Model responses
2. THE Domain_Model SHALL use SQLModel for database table definitions and Pydantic compatibility
3. THE Domain_Model SHALL include proper relationships between entities (cards, sets, decks, prices)
4. THE Domain_Model SHALL support all current API filtering and querying requirements
5. THE Domain_Model SHALL maintain backward compatibility with existing domain interfaces

### Requirement 2

**User Story:** As a system administrator, I want migration commands to populate domain tables, so that the domain database contains all necessary reference data.

#### Acceptance Criteria

1. WHEN a migration command is executed, THE Migration_System SHALL copy relevant data from Reference_Database to Domain_Database
2. THE Migration_System SHALL handle data transformation between reference and domain schemas
3. THE Migration_System SHALL support incremental updates to avoid full rebuilds
4. THE Migration_System SHALL validate data integrity after migration
5. THE Migration_System SHALL provide progress feedback during long-running operations

### Requirement 3

**User Story:** As an API consumer, I want the same response format and functionality, so that existing integrations continue working after the consolidation.

#### Acceptance Criteria

1. THE API SHALL return identical response structures as before consolidation
2. THE API SHALL support all existing query parameters and filtering options
3. THE API SHALL maintain the same performance characteristics for common operations
4. THE API SHALL generate API_Model responses from Domain_Model data
5. THE API SHALL not access Reference_Database directly after consolidation

### Requirement 4

**User Story:** As a developer, I want the Data_Access_Layer to use domain models, so that all database interactions are centralized and consistent.

#### Acceptance Criteria

1. THE Data_Access_Layer SHALL query only the Domain_Database
2. THE Data_Access_Layer SHALL use SQLModel ORM capabilities for type-safe queries
3. THE Data_Access_Layer SHALL convert Domain_Model instances to API_Model responses
4. THE Data_Access_Layer SHALL handle relationships and joins through SQLModel relationships
5. THE Data_Access_Layer SHALL maintain existing error handling and edge case behavior

### Requirement 5

**User Story:** As a developer, I want CLI commands to manage domain database updates, so that I can keep domain data synchronized with reference sources.

#### Acceptance Criteria

1. WHEN reference data is updated, THE CLI SHALL provide commands to refresh domain data
2. THE CLI SHALL support selective updates for specific entity types (cards, sets, decks)
3. THE CLI SHALL validate domain database schema before performing updates
4. THE CLI SHALL provide rollback capabilities for failed migrations
5. THE CLI SHALL log all migration activities for debugging and auditing

### Requirement 6

**User Story:** As a developer, I want proper separation between domain and API concerns, so that the architecture remains maintainable and extensible.

#### Acceptance Criteria

1. THE Domain_Model SHALL focus on business logic and data integrity
2. THE API_Model SHALL focus on request/response serialization and validation
3. THE Domain_Model SHALL not contain API-specific formatting or presentation logic
4. THE API_Model SHALL be generated from or mapped from Domain_Model data
5. THE system SHALL maintain clear boundaries between domain, data access, and API layers