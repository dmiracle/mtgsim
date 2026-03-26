import { useState, useEffect, useRef } from "react";

type SearchInputProps = {
  value?: string;
  placeholder?: string;
  debounceMs?: number;
  onChange: (value: string) => void;
};

export function SearchInput({
  value: controlledValue,
  placeholder = "Search...",
  debounceMs = 300,
  onChange,
}: SearchInputProps) {
  const [localValue, setLocalValue] = useState(controlledValue ?? "");
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    if (controlledValue !== undefined) setLocalValue(controlledValue);
  }, [controlledValue]);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const val = e.target.value;
    setLocalValue(val);
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => onChange(val), debounceMs);
  }

  function handleClear() {
    setLocalValue("");
    clearTimeout(timerRef.current);
    onChange("");
  }

  return (
    <div className="relative">
      <input
        type="text"
        value={localValue}
        onChange={handleChange}
        placeholder={placeholder}
        className="w-full bg-bg-secondary border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent"
      />
      {localValue && (
        <button
          onClick={handleClear}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-secondary text-sm"
          aria-label="Clear search"
        >
          &times;
        </button>
      )}
    </div>
  );
}
