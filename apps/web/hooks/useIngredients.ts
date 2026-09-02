import { useEffect, useState } from "react";

import { getIngredients } from "@/lib/api/ingredients";

/**
 * Kamus bahan untuk keperluan tampilan (`docs/content-schema.md` §A.10.3).
 *
 * Peta `canonical -> displayName` dipakai chip normalisasi agar user melihat
 * "Telur", bukan "egg". Kegagalan fetch TIDAK merusak halaman: peta kosong
 * membuat chip jatuh ke canonical name. Kamus adalah penyempurna tampilan,
 * bukan prasyarat fungsional.
 */
export function useIngredients() {
  const [displayNames, setDisplayNames] = useState<Record<string, string>>({});
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const controller = new AbortController();

    getIngredients({ signal: controller.signal })
      .then((response) => {
        if (controller.signal.aborted) return;

        const map: Record<string, string> = {};
        for (const ingredient of response.ingredients) {
          map[ingredient.name] = ingredient.displayName;
        }
        setDisplayNames(map);
        setReady(true);
      })
      .catch(() => {
        if (controller.signal.aborted) return;
        // Biarkan peta kosong — chip akan memakai canonical name.
        setReady(true);
      });

    return () => controller.abort();
  }, []);

  return { displayNames, ready };
}
