import { Suspense } from "react";

import { Spinner } from "@/components/ui";

import { MessagesView } from "./messages-view";

export default function MessagesPage() {
  return (
    <Suspense fallback={<Spinner />}>
      <MessagesView />
    </Suspense>
  );
}
