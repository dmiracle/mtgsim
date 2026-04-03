import { useNavigate } from "react-router-dom";
import { useHomeStats } from "@/api/hooks";
import { HomePage } from "./HomePage";
import { homeStats as fallback } from "@/fixtures";

export function HomeRoute() {
  const navigate = useNavigate();
  const { data } = useHomeStats();

  return <HomePage stats={data ?? fallback} onSetClick={(code) => navigate(`/sets/${code}`)} />;
}
