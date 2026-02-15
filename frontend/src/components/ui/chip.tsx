"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface ChipProps {
  label: string;
  selected?: boolean;
  onClick?: () => void;
  size?: "sm" | "md";
  icon?: React.ReactNode;
}

export function Chip({ label, selected, onClick, size = "md", icon }: ChipProps) {
  return (
    <motion.button
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full font-medium transition-all duration-200",
        "border",
        size === "sm" ? "px-3 py-1 text-xs" : "px-4 py-2 text-sm",
        selected
          ? "bg-accent/20 border-accent text-accent"
          : "bg-bg-tertiary border-glass-border text-text-secondary hover:text-text-primary hover:border-text-tertiary"
      )}
    >
      {icon}
      {label}
    </motion.button>
  );
}

interface ChipGroupProps {
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
  multiple?: boolean;
}

export function ChipGroup({ options, selected, onChange, multiple = true }: ChipGroupProps) {
  const toggle = (option: string) => {
    if (multiple) {
      onChange(
        selected.includes(option)
          ? selected.filter((s) => s !== option)
          : [...selected, option]
      );
    } else {
      onChange(selected.includes(option) ? [] : [option]);
    }
  };

  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => (
        <Chip
          key={option}
          label={option}
          selected={selected.includes(option)}
          onClick={() => toggle(option)}
        />
      ))}
    </div>
  );
}
