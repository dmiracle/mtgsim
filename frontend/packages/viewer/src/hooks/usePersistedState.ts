import { useEffect, useState } from "react";

export function usePersistedState<T>(
  key: string,
  initial: T,
  storage: Storage = sessionStorage,
): [T, React.Dispatch<React.SetStateAction<T>>] {
  const [value, setValue] = useState<T>(() => {
    try {
      const stored = storage.getItem(key);
      if (stored === null) return initial;
      return JSON.parse(stored) as T;
    } catch {
      return initial;
    }
  });

  useEffect(() => {
    try {
      storage.setItem(key, JSON.stringify(value));
    } catch {
      // quota / private mode — silent
    }
  }, [key, value, storage]);

  return [value, setValue];
}
