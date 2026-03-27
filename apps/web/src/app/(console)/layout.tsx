import { ConsoleShell } from "@/components/console-shell";
import { StewardProvider } from "@/lib/steward-store";

export default function ConsoleLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <StewardProvider>
      <ConsoleShell>{children}</ConsoleShell>
    </StewardProvider>
  );
}
