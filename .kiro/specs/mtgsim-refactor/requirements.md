# Requirements Document

## Introduction

This specification defines the requirements for refactoring the MTGSim codebase to eliminate code duplication, centralize configuration management, unify database access patterns, and improve maintainability. The refactor addresses pain points in the current architecture while preserving all existing functionality.

## Glossary

- **Reference_Database**: Read-only SQLite databases containing MTGJSON data (AllPrintings, AllPrices, AllDecks, AllSets)
- **Personal_Collection**: User's personal card collection stored in SQLModel-based database
- **Configuration_Module**: Centralized module for managing project paths and settings
- **Reference_Repository**: Abstraction layer for accessing reference databases
- **DTO_Mapper**: Data Transfer Object mapper for converting database rows to Pydantic models
- **Price_Utility**: Centralized pricing calculation and lookup functionality
- **Stats_Service**: Service providing real statistics from reference databases
- **Sync_Pipeline**: Process for downloading and importing MTGJSON data

## Requirements

### Requirement 1: Centralized Configuration Management

**User Story:** As a developer, I want centralized configuration management, so that path resolution and settings are consistent across the application.

#### Acceptance Criteria

1. THE Configuration_Module SHALL provide standardized paths for project root, resources directory, reference directory, and user database
2. WHEN any module needs path resolution, THE Configuration_Module SHALL be used instead of ad-hoc path construction
3. THE Configuration_Module SHALL replace all instances of `Path.home() / ".mtgsim"` usage across sync, data, and CLI modules
4. THE Configuration_Module SHALL provide a single source of truth for all application paths

### Requirement 2: Unified Reference Database Access

**User Story:** As a developer, I want unified reference database access, so that SQL queries and database operations are consistent and reusable.

#### Acceptance Criteria

1. THE Reference_Repository SHALL provide read-only connections to AllPrintings, AllPrices, AllDecks, and AllSets databases
2. THE Reference_Repository SHALL provide helper methods for JSON decoding, pagination, and price joins
3. WHEN accessing reference data, THE Reference_Repository SHALL be used instead of raw sqlite3 operations
4. THE Reference_Repository SHALL eliminate duplicate SQL fragments across api/data modules
5. THE Reference_Repository SHALL provide consistent error handling for database operations

### Requirement 3: Normalized Data Transfer Objects

**User Story:** As a developer, I want normalized DTO mapping, so that database row to model conversion is consistent and maintainable.

#### Acceptance Criteria

1. THE DTO_Mapper SHALL provide centralized row-to-model conversion for card, set, and deck summaries
2. WHEN converting database rows to Pydantic models, THE DTO_Mapper SHALL be used instead of manual dict construction
3. THE DTO_Mapper SHALL eliminate duplicate mapping logic across card_service, deck_service, and set_service
4. THE DTO_Mapper SHALL ensure consistent data structure across all API responses

### Requirement 4: Centralized Price Utilities

**User Story:** As a developer, I want centralized price utilities, so that pricing calculations are consistent and reusable across the application.

#### Acceptance Criteria

1. THE Price_Utility SHALL provide TCGPlayer price lookup functionality
2. THE Price_Utility SHALL provide multi-provider price averaging capabilities
3. THE Price_Utility SHALL provide deck total price calculation functionality
4. WHEN price calculations are needed, THE Price_Utility SHALL be used instead of inline queries
5. THE Price_Utility SHALL eliminate duplicate price lookup logic across cards, sets, and decks modules

### Requirement 5: Fixed Static Asset Mounting

**User Story:** As a developer, I want proper static asset mounting, so that the FastAPI application starts correctly without import errors.

#### Acceptance Criteria

1. WHEN checking for static asset directories, THE System SHALL use Path objects instead of string existence checks
2. THE System SHALL properly mount web and webapp directories when they exist
3. THE System SHALL handle missing static directories gracefully without raising exceptions
4. THE System SHALL provide consistent static asset serving across all endpoints

### Requirement 6: Corrected CLI Command Registration

**User Story:** As a developer, I want proper CLI command registration, so that Typer commands are consistently registered and discoverable.

#### Acceptance Criteria

1. THE CLI_System SHALL use consistent command registration patterns across all modules
2. WHEN registering Typer commands, THE CLI_System SHALL use the declared app instances instead of creating new ones
3. THE CLI_System SHALL ensure all commands are properly discoverable through help and dispatch
4. THE CLI_System SHALL eliminate brittle command registration patterns

### Requirement 7: Real Statistics and Format Data

**User Story:** As a user, I want real statistics and format data, so that the API provides accurate information from the reference databases.

#### Acceptance Criteria

1. THE Stats_Service SHALL compute real totals, histograms, and recent sets from reference databases
2. THE Stats_Service SHALL provide actual format and keyword data instead of placeholder responses
3. WHEN requesting statistics, THE Stats_Service SHALL return current data from the reference databases
4. THE Stats_Service SHALL provide consistent data structures for all statistical endpoints

### Requirement 8: Improved Sync Pipeline

**User Story:** As a developer, I want an improved sync pipeline, so that MTGJSON data synchronization is more efficient and reliable.

#### Acceptance Criteria

1. THE Sync_Pipeline SHALL provide download and decompress helpers with checksum validation
2. THE Sync_Pipeline SHALL include modification time guards to avoid unnecessary downloads
3. THE Sync_Pipeline SHALL stream deck and set imports to avoid full-table deletes when unnecessary
4. THE Sync_Pipeline SHALL use structured logging instead of print statements
5. THE Sync_Pipeline SHALL provide progress feedback during long-running operations

### Requirement 9: Preserved Functionality

**User Story:** As a user, I want all existing functionality preserved, so that the refactor doesn't break current features.

#### Acceptance Criteria

1. THE Refactored_System SHALL maintain all existing CLI command functionality
2. THE Refactored_System SHALL maintain all existing API endpoint behavior
3. THE Refactored_System SHALL maintain all existing data access patterns for end users
4. THE Refactored_System SHALL maintain backward compatibility for all public interfaces
5. WHEN the refactor is complete, THE Refactored_System SHALL pass all existing tests