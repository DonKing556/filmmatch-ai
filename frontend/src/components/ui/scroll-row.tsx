"use client";

import { useCallback, useState } from "react";
import useEmblaCarousel from "embla-carousel-react";
import { cn } from "@/lib/utils";

interface ScrollRowProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export function ScrollRow({ title, children, className }: ScrollRowProps) {
  const [emblaRef, emblaApi] = useEmblaCarousel({
    align: "start",
    containScroll: "trimSnaps",
    dragFree: true,
  });
  const [canScrollPrev, setCanScrollPrev] = useState(false);
  const [canScrollNext, setCanScrollNext] = useState(true);

  const onSelect = useCallback(() => {
    if (!emblaApi) return;
    setCanScrollPrev(emblaApi.canScrollPrev());
    setCanScrollNext(emblaApi.canScrollNext());
  }, [emblaApi]);

  const scrollPrev = useCallback(() => emblaApi?.scrollPrev(), [emblaApi]);
  const scrollNext = useCallback(() => emblaApi?.scrollNext(), [emblaApi]);

  // Register the callback
  if (emblaApi) {
    emblaApi.on("select", onSelect);
    emblaApi.on("init", onSelect);
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "ArrowRight") {
      e.preventDefault();
      scrollNext();
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      scrollPrev();
    }
  }

  return (
    <section className={cn("relative group", className)} aria-label={title ?? "Movie list"}>
      {title && (
        <h2 className="text-xl font-semibold text-text-primary mb-4 px-6">
          {title}
        </h2>
      )}
      <div
        className="overflow-hidden"
        ref={emblaRef}
        role="region"
        aria-roledescription="carousel"
        onKeyDown={handleKeyDown}
      >
        <div className="flex gap-3 px-6">{children}</div>
      </div>

      {/* Navigation arrows */}
      {canScrollPrev && (
        <button
          onClick={scrollPrev}
          className={cn(
            "absolute left-0 top-1/2 -translate-y-1/2 z-10",
            "w-12 h-full bg-gradient-to-r from-bg-primary/80 to-transparent",
            "flex items-center justify-start pl-2",
            "opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity",
            "text-text-primary hover:text-white"
          )}
          aria-label="Scroll left"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      )}
      {canScrollNext && (
        <button
          onClick={scrollNext}
          className={cn(
            "absolute right-0 top-1/2 -translate-y-1/2 z-10",
            "w-12 h-full bg-gradient-to-l from-bg-primary/80 to-transparent",
            "flex items-center justify-end pr-2",
            "opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity",
            "text-text-primary hover:text-white"
          )}
          aria-label="Scroll right"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      )}
    </section>
  );
}
