# Implementation Plan: Domain-API Consolidation

## Overview

This implementation plan converts the domain-API consolidation design into discrete coding tasks. The approach focuses on building the domain database structure with reference table copies and enhanced domain tables, then updating the API to use this new architecture while maintaining backward compatibility.

## Tasks

- [x] 1. Set up domain database schema and models
  - Create domain database schema with reference and domain table structure
  - Define SQLModel classes for reference tables (mtgjson_*) and enhanced domain tables
  - Implement migration tracking table and logging infrastructure
  - _Requirements: 1.1, 1.2, 2.1_

- [x] 1.1 Write property test for domain model completeness
  - **Property 1: Domain Model Completeness**
  - **Validates: Requirements 1.1**

- [-] 2. Implement reference table sync system
  - [ ] 2.1 Create CLI commands for reference table synchronization
    - Implement `sync_reference` and `sync_mtgjson` CLI commands
    - Add table copying utilities with prefix support (mtgjson_*)
    - _Requirements: 2.1, 5.1_

  - [ ] 2.2 Write property test for reference table sync integrity
    - **Property 2: Reference Table Sync Integrity**
    - **Validates: Requirements 2.1, 2.2**

  - [ ] 2.3 Add validation and integrity checking for reference data
    - Implement schema validation before sync operations
    - Add data integrity verification after sync completion
    - _Requirements: 2.4, 5.3_

  - [ ]* 2.4 Write property test for sync operation idempotence
    - **Property 4: Sync Operation Idempotence**
    - **Validates: Requirements 2.3**

- [ ] 3. Build domain entity management system
  - [ ] 3.1 Implement CLI commands for adding entities to domain tables
    - Create `add_card`, `add_set`, and `add_deck` CLI commands
    - Build transformation logic from reference to enhanced domain models
    - _Requirements: 1.1, 2.2, 5.2_

  - [ ]* 3.2 Write property test for domain entity addition correctness
    - **Property 3: Domain Entity Addition Correctness**
    - **Validates: Requirements 1.1, 2.2**

  - [ ] 3.3 Add user collection management capabilities
    - Implement logic to track user-selected cards, sets, and decks
    - Add metadata fields for tracking addition timestamps and sources
    - _Requirements: 1.3, 6.1_

  - [ ]* 3.4 Write property test for selective entity addition
    - **Property 9: Selective Entity Addition**
    - **Validates: Requirements 5.2**

- [ ] 4. Checkpoint - Ensure domain database functionality works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Refactor data access layer for domain database
  - [ ] 5.1 Update data access classes to query domain database tables
    - Modify CardsData, SetsData, DecksData to use domain database
    - Implement scope-based querying (user vs reference vs combined)
    - _Requirements: 4.1, 4.2_

  - [ ]* 5.2 Write property test for reference table query compatibility
    - **Property 7: Reference Table Query Compatibility**
    - **Validates: Requirements 3.2, 4.1**

  - [ ] 5.3 Add conversion utilities between reference and domain models
    - Implement transformation functions for read-only reference data
    - Add utilities to convert between MTGJsonCard and Card models
    - _Requirements: 4.3, 4.4_

  - [ ]* 5.4 Write property test for domain to API model conversion
    - **Property 6: Domain to API Model Conversion**
    - **Validates: Requirements 3.4, 4.3**

  - [ ] 5.5 Maintain existing error handling and edge case behavior
    - Ensure error responses remain identical to current system
    - Handle missing data gracefully with appropriate fallbacks
    - _Requirements: 4.5_

- [ ] 6. Update API service layer for new architecture
  - [ ] 6.1 Modify service classes to handle both domain and reference cards
    - Update CardService, SetService, DeckService for new data flow
    - Add logic to distinguish between user collection and reference data
    - _Requirements: 3.4, 4.3_

  - [ ]* 6.2 Write property test for API response compatibility
    - **Property 5: API Response Compatibility**
    - **Validates: Requirements 3.1, 3.2**

  - [ ] 6.3 Add collection management endpoints
    - Implement API endpoints for adding/removing cards from user collection
    - Add endpoints to query user collection vs all available cards
    - _Requirements: 3.1, 3.2_

  - [ ]* 6.4 Write property test for collection management consistency
    - **Property 10: Collection Management Consistency**
    - **Validates: Requirements 4.1, 4.3**

- [ ] 7. Implement rollback and logging capabilities
  - [ ] 7.1 Add rollback functionality for failed operations
    - Implement transaction-based operations with rollback support
    - Add backup creation before major sync operations
    - _Requirements: 5.4_

  - [ ]* 7.2 Write property test for migration rollback consistency
    - **Property 11: Migration Rollback Consistency**
    - **Validates: Requirements 5.4**

  - [ ] 7.3 Implement comprehensive logging for migration activities
    - Add detailed logging for all sync and entity addition operations
    - Include progress reporting for long-running operations
    - _Requirements: 2.5, 5.5_

- [ ] 8. Ensure architectural boundaries and compatibility
  - [ ] 8.1 Validate layer separation and dependencies
    - Ensure domain models don't contain API-specific logic
    - Verify clear boundaries between domain, data access, and API layers
    - _Requirements: 6.1, 6.2, 6.3, 6.5_

  - [ ]* 8.2 Write property test for layer boundary enforcement
    - **Property 13: Layer Boundary Enforcement**
    - **Validates: Requirements 6.3, 6.5**

  - [ ] 8.3 Verify API backward compatibility
    - Ensure all existing API endpoints return identical response structures
    - Test that existing query parameters and filtering options work unchanged
    - _Requirements: 3.1, 3.2, 3.3_

- [ ]* 8.4 Write unit tests for error handling and edge cases
  - Test error conditions and edge cases for all new functionality
  - Verify graceful handling of missing reference data
  - _Requirements: 4.5, 5.4_

- [ ] 9. Final checkpoint - Complete system validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation of functionality
- Property tests validate universal correctness properties across the new architecture
- Unit tests validate specific examples and error conditions
- The implementation maintains strict backward compatibility while adding new collection management capabilities