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

  const paperTotal = collection.quantity_owned + collection.quantity_owned_foil;
  const mtgaTotal = (collection.quantity_owned_mtga ?? 0) + (collection.quantity_owned_mtga_foil ?? 0);
  const grandTotal = paperTotal + mtgaTotal;

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-text-secondary">Collection</h3>
        <span className="text-xs font-semibold text-text-primary">{grandTotal} total</span>
      </div>

      {/* Paper */}
      {paperTotal > 0 && (
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Paper</span>
          </div>
          <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-0.5">
            <dt className="text-xs text-text-muted text-right">Owned</dt>
            <dd className="text-xs text-text-primary">{collection.quantity_owned}</dd>
            {collection.quantity_owned_foil > 0 && (
              <>
                <dt className="text-xs text-text-muted text-right">Foil</dt>
                <dd className="text-xs text-text-primary">{collection.quantity_owned_foil}</dd>
              </>
            )}
          </dl>
        </div>
      )}

      {/* MTGA */}
      {mtgaTotal > 0 && (
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">MTGA</span>
          </div>
          <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-0.5">
            <dt className="text-xs text-text-muted text-right">Owned</dt>
            <dd className="text-xs text-text-primary">{collection.quantity_owned_mtga ?? 0}</dd>
            {(collection.quantity_owned_mtga_foil ?? 0) > 0 && (
              <>
                <dt className="text-xs text-text-muted text-right">Foil</dt>
                <dd className="text-xs text-text-primary">{collection.quantity_owned_mtga_foil}</dd>
              </>
            )}
          </dl>
        </div>
      )}

      {/* Wanted */}
      {(collection.quantity_wanted > 0 || collection.quantity_wanted_foil > 0) && (
        <div className="space-y-1 border-t border-border pt-2">
          <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-0.5">
            {collection.quantity_wanted > 0 && (
              <>
                <dt className="text-xs text-text-muted text-right">Wanted</dt>
                <dd className="text-xs text-text-primary">{collection.quantity_wanted}</dd>
              </>
            )}
            {collection.quantity_wanted_foil > 0 && (
              <>
                <dt className="text-xs text-text-muted text-right">Wanted (Foil)</dt>
                <dd className="text-xs text-text-primary">{collection.quantity_wanted_foil}</dd>
              </>
            )}
          </dl>
        </div>
      )}

      {collection.condition && (
        <div className="border-t border-border pt-2">
          <span className="text-xs text-text-muted">Condition: </span>
          <span className="text-xs text-text-primary capitalize">{collection.condition.replace("_", " ")}</span>
        </div>
      )}

      {collection.notes && (
        <p className="text-xs text-text-muted italic border-t border-border pt-2">{collection.notes}</p>
      )}
    </div>
  );
}
