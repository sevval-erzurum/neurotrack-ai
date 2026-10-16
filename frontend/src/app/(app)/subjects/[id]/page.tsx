import { Suspense } from "react";

import { Spinner } from "@/components/ui";

import { SubjectView } from "./subject-view";

export default function SubjectPage() {
  return (
    <Suspense fallback={<Spinner />}>
      <SubjectView />
    </Suspense>
  );
}
