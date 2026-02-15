"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { analytics } from "@/lib/analytics";

interface FeedbackModalProps {
  open: boolean;
  onClose: () => void;
  movieTitle?: string;
  tmdbId?: number;
  sessionId?: string;
  onSubmit: (rating: number, comment?: string) => Promise<void>;
}

export function FeedbackModal({
  open,
  onClose,
  movieTitle,
  tmdbId,
  sessionId,
  onSubmit,
}: FeedbackModalProps) {
  const [rating, setRating] = useState<number | null>(null);
  const [comment, setComment] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    if (rating === null) return;
    setLoading(true);
    try {
      await onSubmit(rating, comment || undefined);
      analytics.feedbackSubmitted("rating", rating);
      setSubmitted(true);
    } finally {
      setLoading(false);
    }
  }

  function handleClose() {
    setRating(null);
    setComment("");
    setSubmitted(false);
    onClose();
  }

  if (!open) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        onClick={handleClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-sm rounded-2xl bg-bg-elevated border border-glass-border p-6 space-y-5"
        >
          {submitted ? (
            <div className="text-center space-y-3 py-4">
              <div className="text-4xl">&#127909;</div>
              <h3 className="text-lg font-semibold">Thanks for the feedback!</h3>
              <p className="text-sm text-text-secondary">
                This helps us make better recommendations for you.
              </p>
              <Button variant="primary" onClick={handleClose} className="mt-4">
                Done
              </Button>
            </div>
          ) : (
            <>
              <div className="text-center space-y-1">
                <h3 className="text-lg font-semibold">
                  {movieTitle
                    ? `Did you watch ${movieTitle}?`
                    : "How was the movie?"}
                </h3>
                <p className="text-sm text-text-secondary">
                  Rate it to improve your future picks
                </p>
              </div>

              {/* Star rating */}
              <div className="flex justify-center gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setRating(star)}
                    className="transition-transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-accent rounded"
                    aria-label={`${star} star${star > 1 ? "s" : ""}`}
                  >
                    <svg
                      className={`w-10 h-10 ${
                        rating !== null && star <= rating
                          ? "text-yellow-400"
                          : "text-bg-tertiary"
                      }`}
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                    </svg>
                  </button>
                ))}
              </div>

              {/* Optional comment */}
              {rating !== null && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                >
                  <textarea
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder="Any thoughts? (optional)"
                    rows={2}
                    className="w-full px-3 py-2 rounded-lg bg-bg-secondary border border-glass-border text-sm text-text-primary placeholder:text-text-tertiary resize-none focus:outline-none focus:ring-1 focus:ring-accent"
                  />
                </motion.div>
              )}

              <div className="flex gap-3">
                <Button variant="ghost" onClick={handleClose} className="flex-1">
                  Skip
                </Button>
                <Button
                  variant="primary"
                  onClick={handleSubmit}
                  disabled={rating === null || loading}
                  className="flex-1"
                >
                  {loading ? "Saving..." : "Submit"}
                </Button>
              </div>
            </>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
