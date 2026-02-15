import type { RecommendationRequest, RecommendationResponse } from "../types/recommendation";

const API_BASE = "/api/v1";

export async function getRecommendation(
  request: RecommendationRequest
): Promise<RecommendationResponse> {
  const res = await fetch(`${API_BASE}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }

  return res.json();
}
