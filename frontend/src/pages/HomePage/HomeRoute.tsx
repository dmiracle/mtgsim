import { useNavigate } from "react-router-dom";
import { HomePage } from "./HomePage";
import { homeStats } from "@/fixtures";

export function HomeRoute() {
  const navigate = useNavigate();
  return <HomePage stats={homeStats} onSetClick={(code) => navigate(`/sets/${code}`)} />;
}
