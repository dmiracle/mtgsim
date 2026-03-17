# Vector Embeddings Implementation Plan for mtgdb

This document outlines the plan to add vector embedding support to mtgdb for semantic search capabilities over MTG card text.

## Goals

1. Enable semantic similarity search for card text (oracle text, flavor text, names)
2. Support OCR text matching to find cards from imperfect text input
3. Maintain SQLite as the database backend
4. Keep the implementation extensible for future use cases (deck recommendations, card clustering, etc.)

## Technology Selection

### Vector Storage: sqlite-vec

**Choice:** [sqlite-vec](https://github.com/asg017/sqlite-vec) (v0.1.6+)

**Rationale:**
- Successor to sqlite-vss, written by the same author
- Pure C with zero dependencies - runs anywhere SQLite runs
- Active development with Mozilla Builders sponsorship
- LangChain integration available
- Supports multiple vector types (float, int8, binary)
- SIMD-accelerated distance calculations (AVX/NEON)

**Alternatives Considered:**
- [sqlite-vss](https://github.com/asg017/sqlite-vss) - Predecessor, Faiss-based, reported stability issues
- [sqlite-vector](https://github.com/sqliteai/sqlite-vector) (by SQLite.AI) - Different project, less community adoption

**Installation:**
```bash
pip install sqlite-vec
```

### Embedding Model: sentence-transformers

**Choice:** [sentence-transformers](https://github.com/huggingface/sentence-transformers) with `all-MiniLM-L6-v2`

**Rationale:**
- Widely used, well-maintained library from Hugging Face
- 384-dimensional vectors (good balance of quality vs storage)
- Excellent Python 3.14 compatibility (via PyTorch)
- Large ecosystem of pre-trained models

**Note:** fastembed was initially considered but lacks Python 3.14 support due to onnxruntime dependency constraints.

**Installation:**
```bash
pip install sentence-transformers
```

## Architecture

### New Module Structure

```
src/mtgdb/
├── embeddings/
│   ├── __init__.py      # Public API exports
│   ├── models.py        # MJCardEmbedding SQLModel
│   ├── generate.py      # Embedding generation logic
│   ├── search.py        # Similarity search functions
│   └── backends/
│       ├── __init__.py
│       ├── base.py      # Abstract embedding backend
│       └── fastembed.py # FastEmbed implementation
```

### Database Model

New table `mj_card_embedding` to store vector embeddings:

```python
class MJCardEmbedding(SQLModel, table=True):
    """Vector embeddings for card text fields."""

    __tablename__ = "mj_card_embedding"

    id: int | None = Field(default=None, primary_key=True)
    card_uuid: str = Field(foreign_key="mj_card.uuid", index=True, unique=True)

    # Embedding metadata
    model_name: str = Field(index=True)  # e.g., "BAAI/bge-small-en-v1.5"
    model_version: str | None = None
    field_source: str = Field(index=True)  # "oracle_text", "combined", etc.

    # Timestamps for cache invalidation
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    source_hash: str | None = None  # Hash of source text for change detection
```

The actual vectors will be stored in a sqlite-vec virtual table:

```sql
CREATE VIRTUAL TABLE vec_card_embeddings USING vec0(
    embedding float[384],
    card_uuid TEXT,  -- partition key for filtering
    +field_source TEXT  -- auxiliary column
);
```

### Text Preprocessing

For optimal embedding quality, preprocess card text:

```python
def prepare_card_text(card: MJCard, include_flavor: bool = False) -> str:
    """Prepare card text for embedding generation."""
    parts = []

    # Card name provides important context
    parts.append(f"Card: {card.name}")

    # Type line for creature/spell type context
    if card.type_line:
        parts.append(f"Type: {card.type_line}")

    # Oracle text is the primary semantic content
    if card.oracle_text:
        parts.append(card.oracle_text)

    # Optionally include flavor text
    if include_flavor and card.flavor_text:
        parts.append(f"Flavor: {card.flavor_text}")

    return "\n".join(parts)
```

### Embedding Generation

Multiple embedding types to support different use cases:

| Embedding Type | Source Fields | Use Case |
|---------------|---------------|----------|
| `oracle` | name + type_line + oracle_text | Game mechanics similarity |
| `flavor` | name + flavor_text | Thematic/lore similarity |
| `combined` | All text fields | General similarity |
| `name_only` | name | Fuzzy name matching for OCR |

### Search API

```python
from mtgdb.embeddings import search_similar_cards, embed_text

# Search by text query
results = search_similar_cards(
    session,
    query="deals damage to all creatures",
    field_source="oracle",
    limit=10
)

# Search by embedding vector directly (for OCR integration)
embedding = embed_text("Lightnign Bolt")  # typo intentional
results = search_similar_cards(
    session,
    embedding=embedding,
    field_source="name_only",
    limit=5
)

# Result format
for card, distance in results:
    print(f"{card.name}: {distance:.4f}")
```

## Implementation Steps

### Phase 1: Core Infrastructure

1. **Add dependencies to pyproject.toml**
   - `sqlite-vec` for vector storage
   - `fastembed` for embedding generation
   - `xxhash` for fast source text hashing (optional)

2. **Create embeddings module structure**
   - Base abstract class for embedding backends
   - FastEmbed implementation
   - Model and configuration classes

3. **Create MJCardEmbedding model**
   - SQLModel definition
   - Migration/table creation logic

4. **sqlite-vec integration**
   - Extension loading in session.py
   - Virtual table creation
   - Helper functions for vector operations

### Phase 2: Embedding Generation

5. **Text preprocessing functions**
   - Card text preparation
   - Batch processing utilities
   - Source hash computation

6. **Embedding generation pipeline**
   - Single card embedding
   - Batch embedding with progress
   - Incremental updates (only changed cards)

7. **Sync integration**
   - Hook into existing sync pipeline
   - Post-sync embedding regeneration option
   - CLI command for manual regeneration

### Phase 3: Search API

8. **Search functions**
   - Text query to similar cards
   - Vector to similar cards
   - Filtered search (by set, format, etc.)

9. **OCR integration helpers**
   - Fuzzy name matching
   - Confidence scoring
   - Multi-result ranking

### Phase 4: Testing & Documentation

10. **Unit tests**
    - Model tests
    - Embedding generation tests
    - Search accuracy tests

11. **Integration tests**
    - Full pipeline tests
    - Performance benchmarks

12. **Documentation**
    - Usage examples
    - API reference
    - Performance characteristics

## Storage Considerations

### Vector Size Calculation

- ~95,000 unique cards in MTGJSON
- 384 dimensions × 4 bytes (float32) = 1,536 bytes per vector
- Total: ~146 MB for oracle embeddings alone
- With all embedding types: ~580 MB

### Optimization Options

1. **int8 quantization**: Reduce to 384 bytes per vector (75% savings)
2. **Selective embedding**: Only embed unique oracle texts (~30k unique)
3. **Lazy generation**: Generate on-demand, cache results

## Future Extensions

Once the core infrastructure is in place, these become straightforward:

- **Deck similarity**: Embed deck compositions for recommendation
- **Card clustering**: Group mechanically similar cards
- **Natural language queries**: "Find cards that destroy artifacts"
- **Cross-language search**: Using multilingual embedding models
- **Image embeddings**: CLIP-based card art similarity (different model)

## Dependencies Summary

```toml
[project.dependencies]
sqlite-vec = ">=0.1.6"
sentence-transformers = ">=3.0"
```

**Note:** The implementation uses sentence-transformers as a core dependency rather than optional, as embedding functionality is integral to the package's extended features.

## Implementation Status

**IMPLEMENTED** - The core embedding functionality has been implemented:

- `mtgdb.embeddings` module with generation, search, and sqlite-vec integration
- `MJCardEmbedding` model for metadata tracking
- `generate_embeddings()` for batch embedding generation
- `search_similar_cards()`, `search_by_name()`, `search_by_oracle_text()` for similarity search
- 18 passing tests covering all functionality

## References

- [sqlite-vec GitHub](https://github.com/asg017/sqlite-vec)
- [sentence-transformers](https://sbert.net/)
- [LangChain SQLiteVec Integration](https://docs.langchain.com/oss/python/integrations/vectorstores/sqlitevec)
