#!/usr/bin/env python3
"""Card embedding clustering visualization.

This script demonstrates the vector embeddings feature by:
1. Loading card data and generating embeddings
2. Reducing 384-dim embeddings to 2D using t-SNE
3. Clustering cards by semantic similarity
4. Creating interactive visualizations

Run from the mtgdb package directory:
    python examples/clustering_visualization.py
"""

import struct
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mtgdb import MJCard, init_db
from mtgdb.embeddings import (
    EMBEDDING_DIMENSIONS,
    generate_embeddings,
    init_vec_tables,
    register_sqlite_vec,
)
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sqlalchemy import text
from sqlmodel import Session, select


def load_embeddings_from_db(session: Session, field_source: str = "oracle", limit: int = 2000):
    """Load embeddings and card metadata from the database."""
    # Get embeddings from vec table
    results = session.execute(
        text("""
            SELECT card_uuid, embedding
            FROM vec_card_embeddings
            WHERE field_source = :field_source
            LIMIT :limit
        """),
        {"field_source": field_source, "limit": limit},
    ).fetchall()

    if not results:
        return [], [], []

    uuids = [r[0] for r in results]
    embeddings = []
    for r in results:
        # Unpack binary embedding data
        emb_bytes = r[1]
        emb = struct.unpack(f"{EMBEDDING_DIMENSIONS}f", emb_bytes)
        embeddings.append(emb)

    # Fetch card metadata
    cards = session.exec(select(MJCard).where(MJCard.uuid.in_(uuids))).all()
    card_map = {c.uuid: c for c in cards}

    # Align cards with embeddings
    aligned_cards = [card_map.get(uuid) for uuid in uuids]

    return aligned_cards, np.array(embeddings), uuids


def get_card_color(card: MJCard) -> str:
    """Get a display color based on card's color identity."""
    if not card or not card.colors:
        return "#888888"  # Colorless - gray

    colors = card.colors
    if len(colors) > 1:
        return "#CFB53B"  # Multicolor - gold

    color_map = {
        "W": "#F8F6D8",  # White - cream
        "U": "#0E68AB",  # Blue
        "B": "#150B00",  # Black
        "R": "#D3202A",  # Red
        "G": "#00733E",  # Green
    }
    return color_map.get(colors[0], "#888888")


def get_card_type_marker(card: MJCard) -> str:
    """Get marker style based on card type."""
    if not card or not card.types:
        return "o"

    types = card.types
    if "Creature" in types:
        return "o"  # Circle
    elif "Instant" in types:
        return "^"  # Triangle up
    elif "Sorcery" in types:
        return "s"  # Square
    elif "Enchantment" in types:
        return "D"  # Diamond
    elif "Artifact" in types:
        return "p"  # Pentagon
    elif "Planeswalker" in types:
        return "*"  # Star
    elif "Land" in types:
        return "h"  # Hexagon
    return "o"


def main():
    print("=" * 60, flush=True)
    print("MTG Card Embedding Clustering Visualization", flush=True)
    print("=" * 60, flush=True)

    # Initialize database with sqlite-vec
    print("\n[1/5] Initializing database...")
    engine = init_db()
    register_sqlite_vec(engine)
    init_vec_tables(engine)

    with Session(engine) as session:
        # Check if we have cards
        card_count = session.exec(select(MJCard)).first()
        if not card_count:
            print("\nERROR: No cards found in database!")
            print("Please run the MTGJSON sync first:")
            print('  python -c "from mtgdb.sync import sync_all; sync_all()"')
            sys.exit(1)

        # Check for existing embeddings
        result = session.execute(
            text("SELECT COUNT(*) FROM vec_card_embeddings WHERE field_source = 'oracle'")
        ).fetchone()
        embedding_count = result[0] if result else 0

        if embedding_count < 100:
            print(f"\n[2/5] Generating embeddings (found {embedding_count}, need more)...")
            print("      This may take a few minutes on first run...")
            count = generate_embeddings(session, field_source="oracle", batch_size=512)
            print(f"      Generated {count} embeddings")
        else:
            print(f"\n[2/5] Using existing embeddings ({embedding_count} found)")

        # Load embeddings
        print("\n[3/5] Loading embeddings from database...")
        max_cards = 3000  # Limit for visualization performance
        cards, embeddings, uuids = load_embeddings_from_db(session, field_source="oracle", limit=max_cards)
        print(f"      Loaded {len(cards)} card embeddings")

        if len(cards) < 10:
            print("\nERROR: Not enough embeddings for visualization!")
            sys.exit(1)

    # Dimensionality reduction with t-SNE
    print("\n[4/5] Reducing dimensions with t-SNE (this may take a minute)...")
    perplexity = min(30, len(cards) - 1)
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42, max_iter=1000, learning_rate="auto", init="pca")
    coords_2d = tsne.fit_transform(embeddings)
    print("      Done!")

    # Clustering
    print("\n[5/5] Clustering cards...")
    n_clusters = min(12, len(cards) // 50)  # Adaptive cluster count
    n_clusters = max(5, n_clusters)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(embeddings)
    print(f"      Created {n_clusters} clusters")

    # Create visualizations
    print("\n" + "=" * 60)
    print("Creating visualizations...")
    print("=" * 60)

    # Figure 1: Colored by MTG color identity
    fig1, ax1 = plt.subplots(figsize=(14, 10))

    for i, card in enumerate(cards):
        if card is None:
            continue
        color = get_card_color(card)
        marker = get_card_type_marker(card)
        ax1.scatter(
            coords_2d[i, 0],
            coords_2d[i, 1],
            c=color,
            marker=marker,
            s=30,
            alpha=0.7,
            edgecolors="white",
            linewidths=0.5,
        )

    ax1.set_title(
        "MTG Cards by Semantic Similarity\n(Color = MTG Color Identity, Shape = Card Type)",
        fontsize=14,
        fontweight="bold",
    )
    ax1.set_xlabel("t-SNE Dimension 1")
    ax1.set_ylabel("t-SNE Dimension 2")

    # Add legend for colors
    legend_elements = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="#F8F6D8",
            markersize=10,
            label="White",
            markeredgecolor="gray",
        ),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#0E68AB", markersize=10, label="Blue"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#150B00", markersize=10, label="Black"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#D3202A", markersize=10, label="Red"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#00733E", markersize=10, label="Green"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#CFB53B", markersize=10, label="Multicolor"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#888888", markersize=10, label="Colorless"),
    ]
    ax1.legend(handles=legend_elements, loc="upper right", title="Color Identity")

    plt.tight_layout()
    output_path1 = Path("card_similarity_by_color.png")
    fig1.savefig(output_path1, dpi=150, bbox_inches="tight")
    print(f"\nSaved: {output_path1.absolute()}")

    # Figure 2: Colored by cluster
    fig2, ax2 = plt.subplots(figsize=(14, 10))

    scatter = ax2.scatter(
        coords_2d[:, 0],
        coords_2d[:, 1],
        c=cluster_labels,
        cmap="tab20",
        s=30,
        alpha=0.7,
        edgecolors="white",
        linewidths=0.5,
    )

    ax2.set_title(
        f"MTG Cards Clustered by Oracle Text Similarity\n({n_clusters} clusters)", fontsize=14, fontweight="bold"
    )
    ax2.set_xlabel("t-SNE Dimension 1")
    ax2.set_ylabel("t-SNE Dimension 2")

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label("Cluster")

    plt.tight_layout()
    output_path2 = Path("card_similarity_clusters.png")
    fig2.savefig(output_path2, dpi=150, bbox_inches="tight")
    print(f"Saved: {output_path2.absolute()}")

    # Figure 3: Annotated cluster centers with example cards
    fig3, ax3 = plt.subplots(figsize=(16, 12))

    scatter = ax3.scatter(
        coords_2d[:, 0], coords_2d[:, 1], c=cluster_labels, cmap="tab20", s=20, alpha=0.5, edgecolors="none"
    )

    # Find representative cards for each cluster (closest to centroid)
    cluster_examples = {}
    for cluster_id in range(n_clusters):
        mask = cluster_labels == cluster_id
        cluster_coords = coords_2d[mask]
        cluster_cards = [c for c, m in zip(cards, mask) if m and c is not None]

        if len(cluster_coords) > 0 and len(cluster_cards) > 0:
            centroid = cluster_coords.mean(axis=0)
            distances = np.linalg.norm(cluster_coords - centroid, axis=1)
            closest_idx = np.argmin(distances)

            if closest_idx < len(cluster_cards):
                example_card = cluster_cards[closest_idx]
                cluster_examples[cluster_id] = {"card": example_card, "centroid": centroid, "size": mask.sum()}

    # Annotate clusters
    for cluster_id, info in cluster_examples.items():
        card = info["card"]
        centroid = info["centroid"]
        size = info["size"]

        # Draw cluster centroid marker
        ax3.scatter(centroid[0], centroid[1], c="red", s=100, marker="x", linewidths=2)

        # Add annotation with card name
        label = f"Cluster {cluster_id}\n({size} cards)\ne.g. {card.name[:20]}"
        ax3.annotate(
            label,
            xy=(centroid[0], centroid[1]),
            xytext=(10, 10),
            textcoords="offset points",
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
        )

    ax3.set_title("MTG Card Clusters with Example Cards\n(Red X = Cluster Centroid)", fontsize=14, fontweight="bold")
    ax3.set_xlabel("t-SNE Dimension 1")
    ax3.set_ylabel("t-SNE Dimension 2")

    plt.tight_layout()
    output_path3 = Path("card_clusters_annotated.png")
    fig3.savefig(output_path3, dpi=150, bbox_inches="tight")
    print(f"Saved: {output_path3.absolute()}")

    # Print cluster summary
    print("\n" + "=" * 60)
    print("Cluster Summary")
    print("=" * 60)

    for cluster_id in sorted(cluster_examples.keys()):
        info = cluster_examples[cluster_id]
        card = info["card"]
        size = info["size"]

        # Get a few example cards from this cluster
        mask = cluster_labels == cluster_id
        cluster_cards = [c for c, m in zip(cards, mask) if m and c is not None][:5]
        example_names = [c.name for c in cluster_cards]

        print(f"\nCluster {cluster_id} ({size} cards):")
        print(f"  Examples: {', '.join(example_names)}")
        if card.oracle_text:
            oracle_preview = card.oracle_text[:80] + "..." if len(card.oracle_text) > 80 else card.oracle_text
            print(f'  Sample oracle text: "{oracle_preview}"')

    # Show plots
    print("\n" + "=" * 60)
    print("Displaying visualizations...")
    print("Close the plot windows to exit.")
    print("=" * 60)

    plt.show()


if __name__ == "__main__":
    main()
