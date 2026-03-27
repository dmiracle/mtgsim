import { useNavigate } from "react-router-dom";
import { useFlashcardStats } from "@/api/flashcard-hooks";

const USER_ID = localStorage.getItem("flashcard_user_id") || "default_user";

export function HomePage() {
  const navigate = useNavigate();
  const { data: stats } = useFlashcardStats(USER_ID);
  const due = stats?.cards_due ?? 0;

  return (
    <div className="max-w-lg mx-auto px-4 py-12 min-h-screen">
      <div className="text-center mb-10">
        <i className="ms ms-planeswalker text-5xl text-accent" />
        <h1 className="text-3xl font-bold text-text-primary mt-3">MTG Study</h1>
      </div>

      <div className="space-y-3">
        <button
          onClick={() => navigate("/study")}
          className="w-full flex items-center gap-4 px-5 py-5 rounded-xl bg-bg-secondary border border-border hover:border-accent transition-colors text-left"
        >
          <i className="ms ms-flashback text-2xl text-accent" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-text-primary">Flashcard Study</p>
            <p className="text-xs text-text-muted">SRS-scheduled review from your collections</p>
          </div>
          {due > 0 && (
            <span className="bg-accent text-white text-xs font-bold px-2 py-0.5 rounded-full">
              {due}
            </span>
          )}
        </button>

        <button
          onClick={() => navigate("/recall")}
          className="w-full flex items-center gap-4 px-5 py-5 rounded-xl bg-bg-secondary border border-border hover:border-accent transition-colors text-left"
        >
          <i className="ms ms-creature text-2xl text-accent" />
          <div>
            <p className="text-sm font-semibold text-text-primary">Card Recall</p>
            <p className="text-xs text-text-muted">Pick sets and test your card knowledge</p>
          </div>
        </button>
      </div>
    </div>
  );
}
