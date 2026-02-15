"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const PRESET_DEALBREAKERS = [
  "Slow pacing",
  "Jump scares",
  "Excessive violence",
  "Sad endings",
  "Love triangles",
  "Predictable plot",
  "Cheesy dialogue",
  "Shaky camera",
  "Animal harm",
  "Heavy gore",
  "Long runtime (3h+)",
  "Subtitles required",
];

interface DealbreakerInputProps {
  selected: string[];
  onChange: (dealbreakers: string[]) => void;
}

export function DealbreakerInput({
  selected,
  onChange,
}: DealbreakerInputProps) {
  const [custom, setCustom] = useState("");

  function togglePreset(item: string) {
    if (selected.includes(item)) {
      onChange(selected.filter((d) => d !== item));
    } else {
      onChange([...selected, item]);
    }
  }

  function addCustom() {
    const trimmed = custom.trim();
    if (trimmed && !selected.includes(trimmed)) {
      onChange([...selected, trimmed]);
      setCustom("");
    }
  }

  function removeItem(item: string) {
    onChange(selected.filter((d) => d !== item));
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-sm font-semibold text-text-secondary mb-1">
          Save me from...
        </h3>
        <p className="text-xs text-text-tertiary mb-3">
          Pick things you want to avoid. We&apos;ll make sure your picks
          don&apos;t have them.
        </p>
      </div>

      {/* Preset chips */}
      <div className="flex flex-wrap gap-2">
        {PRESET_DEALBREAKERS.map((item) => {
          const isSelected = selected.includes(item);
          return (
            <button
              key={item}
              onClick={() => togglePreset(item)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                isSelected
                  ? "bg-error/15 text-error border border-error/30"
                  : "bg-bg-tertiary text-text-secondary border border-glass-border hover:border-error/20"
              }`}
            >
              {isSelected && (
                <span className="mr-1">&times;</span>
              )}
              {item}
            </button>
          );
        })}
      </div>

      {/* Custom input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={custom}
          onChange={(e) => setCustom(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && addCustom()}
          placeholder="Add your own..."
          className="flex-1 px-3 py-2 rounded-lg bg-bg-secondary border border-glass-border text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-accent/50"
        />
        <button
          onClick={addCustom}
          disabled={!custom.trim()}
          className="px-3 py-2 rounded-lg bg-error/10 text-error text-sm font-medium disabled:opacity-40 transition-opacity"
        >
          Add
        </button>
      </div>

      {/* Selected dealbreakers */}
      <AnimatePresence>
        {selected.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="flex flex-wrap gap-1.5"
          >
            {selected
              .filter((d) => !PRESET_DEALBREAKERS.includes(d))
              .map((item) => (
                <motion.button
                  key={item}
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.8, opacity: 0 }}
                  onClick={() => removeItem(item)}
                  className="px-2.5 py-1 rounded-full text-xs bg-error/15 text-error border border-error/30"
                >
                  &times; {item}
                </motion.button>
              ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
