"use client";
import ChatWindow from "@/components/chat/ChatWindow";
import { ErrorMessage, Loading } from "@/components/common/Status";
import { usePapers } from "@/lib/usePapers";
import { useWorkspace } from "@/lib/useWorkspace";

export default function ChatPage() {
  const { workspaceId, error } = useWorkspace();
  const { papers } = usePapers(workspaceId);
  return (
    <div className="space-y-4">
      <h1 className="text-3xl">Ask the papers</h1>
      <ErrorMessage message={error} />
      {workspaceId ? <ChatWindow workspaceId={workspaceId} papers={papers} /> : !error && <Loading text="Connecting to backend…" />}
    </div>
  );
}
