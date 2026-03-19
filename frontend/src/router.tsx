import { createBrowserRouter } from "react-router-dom"
import AppShell from "./components/layout/AppShell"
import CardDetailPage from "./pages/CardDetailPage"
import CardsPage from "./pages/CardsPage"
import DeckCreatePage from "./pages/DeckCreatePage"
import DeckDetailPage from "./pages/DeckDetailPage"
import DeckImportPage from "./pages/DeckImportPage"
import DecksPage from "./pages/DecksPage"
import DraftPage from "./pages/DraftPage"
import HomePage from "./pages/HomePage"
import PricesPage from "./pages/PricesPage"
import ReferencePage from "./pages/ReferencePage"
import SetDetailPage from "./pages/SetDetailPage"
import SetsPage from "./pages/SetsPage"

export const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { path: "/", element: <HomePage /> },
      { path: "/decks", element: <DecksPage /> },
      { path: "/decks/create", element: <DeckCreatePage /> },
      { path: "/decks/import", element: <DeckImportPage /> },
      { path: "/decks/:file", element: <DeckDetailPage /> },
      { path: "/cards", element: <CardsPage /> },
      { path: "/cards/:uuid", element: <CardDetailPage /> },
      { path: "/sets", element: <SetsPage /> },
      { path: "/sets/:code", element: <SetDetailPage /> },
      { path: "/prices", element: <PricesPage /> },
      { path: "/draft", element: <DraftPage /> },
      { path: "/reference", element: <ReferencePage /> },
    ],
  },
])
