import { Outlet } from "react-router-dom"
import GlossaryOverlay from "../shared/GlossaryOverlay"
import Sidebar from "./Sidebar"

export default function AppShell() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-6">
        <Outlet />
      </main>
      <GlossaryOverlay />
    </div>
  )
}
