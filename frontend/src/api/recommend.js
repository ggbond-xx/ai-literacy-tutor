import http from "./http";

export function fetchRecommendOverview(targetConceptId) {
  const params = targetConceptId ? { target_concept_id: targetConceptId } : {};
  return http.get("/recommend/overview", { params });
}
