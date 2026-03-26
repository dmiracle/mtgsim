import { createBrowserRouter, Navigate } from "react-router-dom";
import { AppLayout } from "@/components/AppLayout/AppLayout";
import { HomeRoute } from "@/pages/HomePage/HomeRoute";
import { DeckBrowserRoute } from "@/pages/DeckBrowserPage/DeckBrowserRoute";
import { DeckDetailRoute } from "@/pages/DeckDetailPage/DeckDetailRoute";
import { CardBrowserRoute } from "@/pages/CardBrowserPage/CardBrowserRoute";
import { CardDetailRoute } from "@/pages/CardDetailPage/CardDetailRoute";
import { SetBrowserRoute } from "@/pages/SetBrowserPage/SetBrowserRoute";
import { SetDetailRoute } from "@/pages/SetDetailPage/SetDetailRoute";
import { PriceExplorerRoute } from "@/pages/PriceExplorerPage/PriceExplorerRoute";
import { DraftSimulatorRoute } from "@/pages/DraftSimulatorPage/DraftSimulatorRoute";
import { ReferenceRoute } from "@/pages/ReferencePage/ReferenceRoute";
import { FlashcardDashboardRoute } from "@/pages/FlashcardDashboardPage/FlashcardDashboardRoute";
import { FlashcardStudyRoute } from "@/pages/FlashcardStudyPage/FlashcardStudyRoute";
import { FlashcardGenerateRoute } from "@/pages/FlashcardGeneratePage/FlashcardGenerateRoute";

export const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      { path: "/", element: <HomeRoute /> },
      { path: "/decks", element: <DeckBrowserRoute /> },
      { path: "/decks/:file", element: <DeckDetailRoute /> },
      { path: "/cards", element: <CardBrowserRoute /> },
      { path: "/cards/:uuid", element: <CardDetailRoute /> },
      { path: "/sets", element: <SetBrowserRoute /> },
      { path: "/sets/:code", element: <SetDetailRoute /> },
      { path: "/prices", element: <PriceExplorerRoute /> },
      { path: "/draft", element: <DraftSimulatorRoute /> },
      { path: "/reference", element: <ReferenceRoute /> },
      { path: "/flashcards", element: <FlashcardDashboardRoute /> },
      { path: "/flashcards/study", element: <FlashcardStudyRoute /> },
      { path: "/flashcards/generate", element: <FlashcardGenerateRoute /> },
      { path: "*", element: <Navigate to="/" replace /> },
    ],
  },
]);
