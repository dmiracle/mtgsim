import { useState } from "react";

type OracleTextInputProps = {
  value?: string;
  onChange: (text: string) => void;
  placeholder?: string;
  maxLines?: number;
};

export function OracleTextInput({
  value = "",
  onChange,
  placeholder = "Type the oracle text you remember...",
  maxLines = 6,
}: OracleTextInputProps) {
  const [text, setText] = useState(value);

  function handleChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    setText(e.target.value);
    onChange(e.target.value);
  }

  const lineCount = text.split("\n").length;

  return (
    <div className="space-y-1">
      <textarea
        value={text}
        onChange={handleChange}
        placeholder={placeholder}
        rows={Math.min(Math.max(3, lineCount + 1), maxLines)}
        className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2.5 text-sm text-text-primary placeholder-text-muted leading-relaxed resize-none focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-all"
      />
      {text && (
        <p className="text-[10px] text-text-muted text-right">
          {text.length} chars
        </p>
      )}
    </div>
  );
}
