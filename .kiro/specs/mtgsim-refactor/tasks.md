# Implementation Plan: MTGSim Refactor

## Overview

This implementation plan breaks down the MTGSim refactor into discrete coding tasks that build incrementally. The approach follows the suggested sequence from the refactor plan: configuration and reference repository layer first, then static mounts and CLI wiring, followed by real stats implementation and sync pipeline improvements.

## Tasks

- [x] 1. Create centralized configuration module
  - Create `src/mtgsim/config.py` with MTGSimConfig class
  - Implement properties for project_root, resources_dir, reference_dir, user_db_path, mtgjson_dir
  - Create singleton config instance
  - _Requirements: 1.1, 1.4_

- [x] 1.1 Write property test for configuration module
  - **Property 1: Configuration Centralization**
  - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

- [x] 2. Create reference repository layer
  - Create `src/mtgsim/reference/` package with `__init__.py`
  - Create `src/mtgsim/reference/repository.py` with ReferenceRepository class
  - Implement database connection management and helper methods
  - Add JSON decoding, pagination, and price join utilities
  - _Requirements: 2.1, 2.2, 2.5_

- [x] 2.1 Write property test for reference repository
  - **Property 2: Reference Database Unification**
  - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

- [x] 3. Create DTO mappers
  - Create `src/mtgsim/api/models/mappers.py` with DTOMapper class
  - Implement map_card_summary, map_deck_summary, map_set_summary methods
  - Ensure consistent field mapping and JSON handling
  - _Requirements: 3.1, 3.4_

- [x] 3.1 Write property test for DTO mappers
  - **Property 3: DTO Mapping Centralization**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

- [x] 4. Create price utilities
  - Create `src/mtgsim/api/data/pricing.py` with PriceUtility class
  - Implement TCGPlayer price lookup, multi-provider averaging, deck total calculation
  - Add bulk price lookup functionality
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 4.1 Write property test for price utilities
  - **Property 4: Price Utility Consolidation**
  - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

- [x] 5. Checkpoint - Core infrastructure complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Update database manager to use configuration
  - Modify `src/mtgsim/api/data/database.py` to use config module
  - Replace hardcoded REFERENCE_DB_DIR with config.mtgjson_dir
  - Update all path references to use centralized configuration
  - _Requirements: 1.2, 1.3_

- [x] 7. Refactor data modules to use reference repository
  - Update `src/mtgsim/api/data/cards.py` to use ReferenceRepository
  - Update `src/mtgsim/api/data/sets.py` to use ReferenceRepository  
  - Update `src/mtgsim/api/data/decks.py` to use ReferenceRepository
  - Remove duplicate SQL fragments and replace with repository methods
  - _Requirements: 2.3, 2.4_

- [x] 8. Update services to use DTO mappers and price utilities
  - Modify `src/mtgsim/api/services/card_service.py` to use DTOMapper and PriceUtility
  - Modify `src/mtgsim/api/services/deck_service.py` to use DTOMapper and PriceUtility
  - Modify `src/mtgsim/api/services/set_service.py` to use DTOMapper and PriceUtility
  - Remove manual dict construction and inline price queries
  - _Requirements: 3.2, 3.3, 4.4, 4.5_

- [x] 9. Fix static asset mounting in FastAPI
  - Update `src/mtgsim/api/main.py` to use Path objects for directory checks
  - Replace string existence checks with proper Path.exists() calls
  - Add graceful handling for missing static directories
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 9.1 Write property test for static asset handling
  - **Property 5: Static Asset Handling**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**

- [x] 10. Fix CLI command registration
  - Update `src/mtgsim/cli/card_commands.py` to use proper Typer app registration
  - Replace `@typer.Typer().command()` with `@card_app.command()`
  - Ensure all commands use declared app instances consistently
  - _Requirements: 6.1, 6.2, 6.4_

- [x] 10.1 Write property test for CLI command registration
  - **Property 6: CLI Command Registration**
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

- [-] 11. Checkpoint - Refactoring complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement real statistics service
  - Update `src/mtgsim/api/services/stats_service.py` to use ReferenceRepository
  - Implement get_home_stats with real database queries
  - Implement get_deck_stats with actual aggregations
  - Replace placeholder responses with computed data
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 12.1 Write property test for statistics service
  - **Property 7: Real Statistics Provision**
  - **Validates: Requirements 7.1, 7.2, 7.3, 7.4**

- [ ] 13. Implement real format and keyword endpoints
  - Update `src/mtgsim/api/data/keywords.py` to query reference databases
  - Implement actual format data retrieval from legalities
  - Replace hardcoded keyword lists with database queries
  - _Requirements: 7.2_

- [ ] 14. Create improved sync pipeline
  - Create `src/mtgsim/sync/pipeline.py` with SyncPipeline class
  - Implement download_with_checksum and extract_with_progress methods
  - Add structured logging with Python logging module
  - Implement streaming imports for decks and sets
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 14.1 Write property test for sync pipeline
  - **Property 8: Sync Pipeline Enhancement**
  - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

- [ ] 15. Update sync module to use improved pipeline
  - Modify `src/mtgsim/sync/mtgjson.py` to use SyncPipeline class
  - Replace print statements with logger calls
  - Update path references to use configuration module
  - Add progress feedback and checksum validation
  - _Requirements: 8.4, 8.5, 1.2_

- [ ] 16. Run existing test suite for backward compatibility
  - Execute `uv run pytest` to verify all existing tests pass
  - Verify CLI commands produce same output as before refactor
  - Test API endpoints return same response structures
  - _Requirements: 9.1, 9.2, 9.5_

- [ ] 16.1 Write property test for backward compatibility
  - **Property 9: Backward Compatibility Preservation**
  - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**

- [ ] 17. Final checkpoint - Complete refactor validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The refactor preserves all existing functionality while improving maintainability