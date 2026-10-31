import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { FilterPage } from "./pages/FilterPage";
import { ReviewPage } from "./pages/ReviewPage";

const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 5 * 60_000, retry: 1 } } });

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<FilterPage />} />
          <Route path="/review" element={<ReviewPage />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
