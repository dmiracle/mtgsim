import type { ReactNode } from "react";
import { SidebarNav } from "@/components/SidebarNav/SidebarNav";

type AppLayoutProps = {
  activeNav: string;
  onNavigate: (id: string) => void;
  children: ReactNode;
};

export function AppLayout({ activeNav, onNavigate, children }: AppLayoutProps) {
  return (
    <div className="flex h-screen bg-bg-primary text-text-primary">
      <SidebarNav activeId={activeNav} onNavigate={onNavigate} />
      <main className="flex-1 overflow-y-auto p-6">{children}</main>
    </div>
  );
}
