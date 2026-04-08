import { useRef } from "react";
import type { MtgaImportResult } from "@/types/api";

type MtgaImportModalProps = {
  open: boolean;
  importing?: boolean;
  result?: MtgaImportResult;
  onImport: (file: File) => void;
  onClose: () => void;
};

export function MtgaImportModal({ open, importing = false, result, onImport, onClose }: MtgaImportModalProps) {
  const fileRef = useRef<HTMLInputElement>(null);

  if (!open) return null;

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) onImport(file);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) onImport(file);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={onClose}>
      <div className="bg-bg-secondary border border-border rounded-xl w-full max-w-md shadow-xl" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <h2 className="text-sm font-semibold text-text-primary">Import MTGA Collection</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary text-lg leading-none">&times;</button>
        </div>

        <div className="p-4 space-y-4">
          {!result ? (
            <>
              <p className="text-xs text-text-muted">
                Export your collection from MTGA as a CSV file, then upload it here.
              </p>

              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => fileRef.current?.click()}
                className="border-2 border-dashed border-border rounded-lg p-8 text-center cursor-pointer hover:border-accent transition-colors"
              >
                <input ref={fileRef} type="file" accept=".csv" onChange={handleFile} className="hidden" />
                {importing ? (
                  <p className="text-sm text-text-muted">Importing...</p>
                ) : (
                  <>
                    <p className="text-sm text-text-secondary">Drop CSV file here</p>
                    <p className="text-xs text-text-muted mt-1">or click to browse</p>
                  </>
                )}
              </div>
            </>
          ) : (
            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-2">
                <div className="bg-bg-tertiary rounded-lg p-3 text-center">
                  <p className="text-lg font-bold text-success">{result.matched}</p>
                  <p className="text-[10px] text-text-muted">Matched</p>
                </div>
                <div className="bg-bg-tertiary rounded-lg p-3 text-center">
                  <p className="text-lg font-bold text-accent">{result.created}</p>
                  <p className="text-[10px] text-text-muted">Created</p>
                </div>
                <div className="bg-bg-tertiary rounded-lg p-3 text-center">
                  <p className="text-lg font-bold text-text-primary">{result.updated}</p>
                  <p className="text-[10px] text-text-muted">Updated</p>
                </div>
              </div>

              {result.unmatched.length > 0 && (
                <div className="space-y-1">
                  <p className="text-xs text-warning font-medium">{result.unmatched.length} unmatched cards:</p>
                  <div className="max-h-32 overflow-y-auto bg-bg-tertiary rounded-lg p-2">
                    {result.unmatched.map((name) => (
                      <p key={name} className="text-xs text-text-muted">{name}</p>
                    ))}
                  </div>
                </div>
              )}

              <button
                onClick={onClose}
                className="w-full text-xs font-medium px-3 py-2 rounded bg-accent text-white hover:bg-accent-hover transition-colors"
              >
                Done
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
