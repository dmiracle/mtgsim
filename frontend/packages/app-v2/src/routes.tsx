import { createBrowserRouter, Navigate } from "react-router-dom";
import { HomePage } from "@/pages/HomePage";
import { StudyPage } from "@/pages/StudyPage";

export const router = createBrowserRouter([
  { path: "/", element: <HomePage /> },
  { path: "/study", element: <StudyPage /> },
  { path: "*", element: <Navigate to="/" replace /> },
]);
