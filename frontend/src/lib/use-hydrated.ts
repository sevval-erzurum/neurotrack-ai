"use client";

import { useSyncExternalStore } from "react";

const noop = () => () => {};

/**
 * Hydration bitene kadar false, sonra true. Sunucu ve ilk istemci render'ı aynı kalır.
 *
 * TanStack Query hydration sırasında "sunucu görüntüsü" olarak önbellekteki güncel sonucu
 * döndürür. Ayrı Suspense bölümleri farklı zamanlarda hydrate olunca, sonra gelen bölüm
 * bu arada çekilmiş veriyle render edilir ve sunucu HTML'iyle uyuşmaz (React #418).
 * Veri odaklı bileşenleri bu kancanın arkasında render etmek bu yarışı ortadan kaldırır.
 */
export function useHydrated(): boolean {
  return useSyncExternalStore(
    noop,
    () => true,
    () => false,
  );
}
