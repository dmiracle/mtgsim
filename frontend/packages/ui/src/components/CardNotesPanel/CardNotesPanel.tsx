import { useState } from "react";
import type { CardNote } from "@/types/api";

export type CardNotesPanelProps = {
  notes: CardNote[];
  onCreate: (data: { body: string; title: string | null; kind: string }) => void;
  onUpdate: (id: number, data: { body: string; title: string | null; kind: string }) => void;
  onDelete: (id: number) => void;
};

type NoteDraft = { body: string; title: string; kind: string };

function NoteForm({
  initial,
  onSubmit,
  onCancel,
  submitLabel,
}: {
  initial: NoteDraft;
  onSubmit: (draft: NoteDraft) => void;
  onCancel: () => void;
  submitLabel: string;
}) {
  const [draft, setDraft] = useState(initial);

  return (
    <div className="bg-bg-tertiary border border-border rounded-lg p-3 space-y-2">
      <div className="flex gap-2">
        <input
          value={draft.title}
          onChange={(e) => setDraft({ ...draft, title: e.target.value })}
          placeholder="Title (optional)"
          className="flex-1 bg-bg-secondary border border-border rounded-lg px-3 py-1.5 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent"
        />
        <input
          value={draft.kind}
          onChange={(e) => setDraft({ ...draft, kind: e.target.value })}
          placeholder="kind"
          className="w-28 bg-bg-secondary border border-border rounded-lg px-3 py-1.5 text-xs text-text-secondary placeholder-text-muted focus:outline-none focus:border-accent"
        />
      </div>
      <textarea
        value={draft.body}
        onChange={(e) => setDraft({ ...draft, body: e.target.value })}
        placeholder="Write a note..."
        rows={3}
        className="w-full bg-bg-secondary border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent resize-none"
      />
      <div className="flex items-center gap-2">
        <button
          onClick={() => draft.body.trim() && onSubmit(draft)}
          disabled={!draft.body.trim()}
          className="text-xs px-3 py-1 rounded bg-accent text-white hover:bg-accent-hover transition-colors disabled:opacity-40"
        >
          {submitLabel}
        </button>
        <button onClick={onCancel} className="text-xs text-text-muted hover:text-text-primary transition-colors">
          Cancel
        </button>
      </div>
    </div>
  );
}

export function CardNotesPanel({ notes, onCreate, onUpdate, onDelete }: CardNotesPanelProps) {
  const [adding, setAdding] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);

  function submitDraft(draft: NoteDraft): { body: string; title: string | null; kind: string } {
    return { body: draft.body.trim(), title: draft.title.trim() || null, kind: draft.kind.trim() || "note" };
  }

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-text-secondary">
          Notes {notes.length > 0 && <span className="text-text-muted font-normal">({notes.length})</span>}
        </h3>
        {!adding && (
          <button
            onClick={() => setAdding(true)}
            className="text-xs text-accent hover:text-accent-hover transition-colors"
          >
            + Add note
          </button>
        )}
      </div>

      {adding && (
        <NoteForm
          initial={{ body: "", title: "", kind: "note" }}
          submitLabel="Save note"
          onSubmit={(draft) => {
            onCreate(submitDraft(draft));
            setAdding(false);
          }}
          onCancel={() => setAdding(false)}
        />
      )}

      {notes.length === 0 && !adding ? (
        <p className="text-xs text-text-muted">No notes for this card.</p>
      ) : (
        <div className="space-y-2">
          {notes.map((note) =>
            editingId === note.id ? (
              <NoteForm
                key={note.id}
                initial={{ body: note.body, title: note.title ?? "", kind: note.kind }}
                submitLabel="Update"
                onSubmit={(draft) => {
                  onUpdate(note.id, submitDraft(draft));
                  setEditingId(null);
                }}
                onCancel={() => setEditingId(null)}
              />
            ) : (
              <div key={note.id} className="group bg-bg-tertiary border border-border rounded-lg p-3 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="px-1.5 py-0.5 text-[10px] uppercase tracking-widest rounded bg-accent/10 text-accent font-semibold">
                    {note.kind}
                  </span>
                  {note.title && <span className="text-sm font-medium text-text-primary">{note.title}</span>}
                  <div className="ml-auto flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => setEditingId(note.id)}
                      className="text-xs text-text-muted hover:text-accent transition-colors"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => onDelete(note.id)}
                      className="text-xs text-text-muted hover:text-danger transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
                <p className="text-sm text-text-secondary whitespace-pre-wrap">{note.body}</p>
                <p className="text-[10px] text-text-muted">
                  {new Date(note.updated_at).toLocaleDateString()}
                </p>
              </div>
            ),
          )}
        </div>
      )}
    </div>
  );
}
