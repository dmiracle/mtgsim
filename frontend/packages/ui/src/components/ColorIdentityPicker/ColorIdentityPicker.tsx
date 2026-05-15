import { ManaIcon } from "@/components/ManaSymbols/ManaSymbols";

const COLORS = [
  { id: "W", label: "White" },
  { id: "U", label: "Blue" },
  { id: "B", label: "Black" },
  { id: "R", label: "Red" },
  { id: "G", label: "Green" },
  { id: "M", label: "Gold (multicolor)" },
  { id: "C", label: "Colorless" },
];

type ColorIdentityPickerProps = {
  selected: string[];
  onChange: (selected: string[]) => void;
  size?: "sm" | "md" | "lg";
};

const btnSize = { sm: "w-8 h-8", md: "w-10 h-10", lg: "w-12 h-12" };

export function ColorIdentityPicker({ selected, onChange, size = "md" }: ColorIdentityPickerProps) {
  function toggle(id: string) {
    if (selected.includes(id)) {
      onChange(selected.filter((c) => c !== id));
    } else {
      onChange([...selected, id]);
    }
  }

  return (
    <div className="inline-flex items-center gap-1.5">
      {COLORS.map((color) => {
        const active = selected.includes(color.id);
        return (
          <button
            key={color.id}
            onClick={() => toggle(color.id)}
            title={color.label}
            className={`${btnSize[size]} rounded-full inline-flex items-center justify-center transition-transform cursor-pointer group ${
              active ? "scale-110" : "hover:scale-110"
            }`}
          >
            <span className={`transition-all duration-150 ${active ? "" : "grayscale opacity-35 group-hover:grayscale-0 group-hover:opacity-70"}`}>
              <ManaIcon
                symbol={color.id}
                size={size}
                shadow={active}
                glowing={active}
              />
            </span>
          </button>
        );
      })}
    </div>
  );
}
