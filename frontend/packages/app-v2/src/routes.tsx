import { createBrowserRouter, Navigate } from "react-router-dom";
import { HomePage } from "@/pages/HomePage";
import { StudyPage } from "@/pages/StudyPage";
import { RecallPage } from "@/pages/RecallPage";

export const router = createBrowserRouter([
  { path: "/", element: <HomePage /> },
  { path: "/study", element: <StudyPage /> },
  { path: "/recall", element: <RecallPage /> },
  { path: "*", element: <Navigate to="/" replace /> },
]);
