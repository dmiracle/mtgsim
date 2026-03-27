import { useNavigate } from "react-router-dom";
import { useFlashcardStats } from "@/api/flashcard-hooks";
import { StudyHome } from "@/components/StudyHome/StudyHome";

const USER_ID = localStorage.getItem("flashcard_user_id") || "default_user";

export function HomePage() {
  const navigate = useNavigate();
  const { data: stats } = useFlashcardStats(USER_ID);

  return (
    <StudyHome
      modes={[
        {
          key: "flashcards",
          label: "Flashcard Study",
          description: "SRS-scheduled review from your collections",
          iconClass: "ms ms-flashback",
          badge: stats?.cards_due,
        },
      ]}
      onSelect={() => navigate("/study")}
    />
  );
}
