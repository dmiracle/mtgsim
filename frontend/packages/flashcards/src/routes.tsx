import { createBrowserRouter, Navigate } from "react-router-dom";
import { HomePage } from "@/pages/HomePage";
import { StudyPage } from "@/pages/StudyPage";
import { GeneratePage } from "@/pages/GeneratePage";

export const router = createBrowserRouter([
  { path: "/", element: <HomePage /> },
  { path: "/study", element: <StudyPage /> },
  { path: "/generate", element: <GeneratePage /> },
  { path: "*", element: <Navigate to="/" replace /> },
]);
