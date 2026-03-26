import { createBrowserRouter, Navigate } from "react-router-dom";

export const router = createBrowserRouter([
  {
    children: [
      {
        path: "/",
        element: (
          <div className="flex items-center justify-center min-h-screen bg-bg-primary text-text-primary">
            <div className="text-center space-y-4">
              <h1 className="text-4xl font-bold">MTG Sim v2</h1>
              <p className="text-text-secondary">New app shell — ready for development</p>
              <p className="text-sm text-text-muted">
                Importing shared components from <code className="text-accent">@mtgsim/ui</code>
              </p>
            </div>
          </div>
        ),
      },
      { path: "*", element: <Navigate to="/" replace /> },
    ],
  },
]);
