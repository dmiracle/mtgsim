import type { CardCollection } from "@/types/api";

type CollectionStatusProps = {
  owns: boolean;
  collection: CardCollection | null;
  onAddToCollection: () => void;
};

export function CollectionStatus({ owns, collection, onAddToCollection }: CollectionStatusProps) {
  if (!owns || !collection) {
    return (
      <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
        <h3 className="text-sm font-medium text-text-secondary">Collection</h3>
        <p className="text-xs text-text-muted">Not in your collection</p>
        <button
          onClick={onAddToCollection}
          className="w-full text-xs font-medium px-3 py-2 rounded bg-accent text-white hover:bg-accent-hover transition-colors"
        >
          Add to Collection
        </button>
      </div>
    );
  }

  const rows: [string, string | number][] = [
    ["Owned", collection.quantity_owned],
    ["Owned (Foil)", collection.quantity_owned_foil],
    ["Wanted", collection.quantity_wanted],
    ["Wanted (Foil)", collection.quantity_wanted_foil],
  ];

  if (collection.condition) rows.push(["Condition", collection.condition.replace("_", " ")]);

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
      <h3 className="text-sm font-medium text-text-secondary">Collection</h3>
      <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1">
        {rows.map(([label, value]) => (
          <div key={label} className="contents">
            <dt className="text-xs text-text-muted text-right">{label}</dt>
            <dd className="text-xs text-text-primary capitalize">{value}</dd>
          </div>
        ))}
      </dl>
      {collection.notes && (
        <p className="text-xs text-text-muted italic border-t border-border pt-2">{collection.notes}</p>
      )}
    </div>
  );
}
