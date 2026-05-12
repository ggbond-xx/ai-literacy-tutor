from collections import defaultdict

from fastapi import Depends
from neo4j import Driver
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import mysql as mysql_db
from app.db.neo4j import get_neo4j_driver
from app.models.user_knowledge_status import UserKnowledgeStatus
from app.schemas.recommend import (
    LearningPathStep,
    RecommendedConcept,
    RecommendOverviewResponse,
    WeakPointItem,
)
from app.services.graph_catalog import get_graph_catalog
from app.services.json_store import get_recommendation_settings, list_learning_statuses


class RecommendationService:
    def __init__(self, driver: Driver):
        self.driver = driver

    def _load_prerequisite_graph(self) -> tuple[dict[str, dict], list[dict[str, str]]]:
        with self.driver.session(database=settings.neo4j_database) as session:
            concept_records = session.run(
                """
                MATCH (c:Concept)
                RETURN
                    elementId(c) AS id,
                    c.name AS name,
                    c.description AS description,
                    c.category AS category,
                    c.difficulty AS difficulty
                ORDER BY c.name
                """
            ).data()
            relation_records = session.run(
                """
                MATCH (pre:Concept)-[:PREREQUISITE_OF]->(post:Concept)
                RETURN elementId(pre) AS source, elementId(post) AS target
                """
            ).data()

        concepts = {}
        for record in concept_records:
            node_id = record["id"]
            concepts[node_id] = {
                "id": node_id,
                "name": record.get("name", ""),
                "description": record.get("description"),
                "category": record.get("category"),
                "difficulty": record.get("difficulty"),
            }

        relations = [
            {"source": item["source"], "target": item["target"]}
            for item in relation_records
            if item["source"] in concepts and item["target"] in concepts
        ]

        catalog_concepts, catalog_relations = get_graph_catalog()
        id_by_name = {concept["name"]: concept_id for concept_id, concept in concepts.items()}
        relation_keys = {(item["source"], item["target"]) for item in relations}

        for item in catalog_concepts:
            if item["name"] in id_by_name:
                concept_id = id_by_name[item["name"]]
                concepts[concept_id] = {
                    **concepts[concept_id],
                    "name": item["name"],
                    "description": item.get("description"),
                    "category": item.get("category"),
                    "difficulty": item.get("difficulty"),
                }
                continue

            concept_id = f"catalog:{item['slug']}"
            concepts[concept_id] = {
                "id": concept_id,
                "name": item["name"],
                "description": item.get("description"),
                "category": item.get("category"),
                "difficulty": item.get("difficulty"),
            }
            id_by_name[item["name"]] = concept_id

        for source_name, target_name, relation_type in catalog_relations:
            if relation_type != "PREREQUISITE_OF":
                continue
            source_id = id_by_name.get(source_name)
            target_id = id_by_name.get(target_name)
            if not source_id or not target_id:
                continue
            relation_key = (source_id, target_id)
            if relation_key in relation_keys:
                continue
            relations.append({"source": source_id, "target": target_id})
            relation_keys.add(relation_key)

        return concepts, relations

    def build_overview(
        self,
        user_id: int,
        db: Session,
        target_concept_id: str | None = None,
    ) -> RecommendOverviewResponse:
        concepts, relations = self._load_prerequisite_graph()
        recommendation_settings = get_recommendation_settings()
        recommendation_limit = int(recommendation_settings.get("recommendation_limit", 6))
        weak_point_limit = int(recommendation_settings.get("weak_point_limit", 5))
        path_limit = int(recommendation_settings.get("path_limit", 6))
        mastery_weight = float(recommendation_settings.get("mastery_weight", 1.0))
        in_progress_weight = float(recommendation_settings.get("in_progress_weight", 0.5))

        prerequisite_map: dict[str, list[str]] = defaultdict(list)
        unlock_map: dict[str, list[str]] = defaultdict(list)
        for relation in relations:
            prerequisite_map[relation["target"]].append(relation["source"])
            unlock_map[relation["source"]].append(relation["target"])

        if mysql_db.database_mode != "json-fallback":
            records = db.query(UserKnowledgeStatus).filter(UserKnowledgeStatus.user_id == user_id).all()
            status_map = {record.concept_id: record.status for record in records}
        else:
            records = list_learning_statuses(user_id)
            status_map = {record["concept_id"]: record["status"] for record in records}

        def readiness_score(concept_id: str) -> float:
            prerequisites = prerequisite_map.get(concept_id, [])
            if not prerequisites:
                return 1.0

            score_map = {0: 0.0, 1: in_progress_weight, 2: mastery_weight}
            score = sum(score_map.get(status_map.get(item, 0), 0.0) for item in prerequisites)
            return round(score / len(prerequisites) / max(mastery_weight, 1e-6), 2)

        def to_recommended(concept_id: str) -> RecommendedConcept:
            concept = concepts[concept_id]
            return RecommendedConcept(
                id=concept_id,
                name=concept["name"],
                category=concept["category"],
                description=concept["description"],
                difficulty=concept["difficulty"],
                status=status_map.get(concept_id, 0),
                readiness=readiness_score(concept_id),
                prerequisite_count=len(prerequisite_map.get(concept_id, [])),
                blocked_count=len(unlock_map.get(concept_id, [])),
            )

        total_concepts = len(concepts)
        mastered_count = sum(1 for status in status_map.values() if status == 2)
        in_progress_count = sum(1 for status in status_map.values() if status == 1)
        unlearned_count = total_concepts - mastered_count - in_progress_count

        weighted_progress = 0.0
        for concept_id in concepts:
            status = status_map.get(concept_id, 0)
            weighted_progress += {0: 0.0, 1: 0.5, 2: 1.0}.get(status, 0.0)
        progress_rate = round((weighted_progress / total_concepts) * 100) if total_concepts else 0

        candidate_ids = [concept_id for concept_id in concepts if status_map.get(concept_id, 0) != 2]
        sorted_candidates = sorted(
            candidate_ids,
            key=lambda concept_id: (
                -readiness_score(concept_id),
                0 if status_map.get(concept_id, 0) == 1 else 1,
                len(prerequisite_map.get(concept_id, [])),
                concepts[concept_id].get("difficulty") or 99,
                concepts[concept_id]["name"],
            ),
        )
        recommended_concepts = [to_recommended(concept_id) for concept_id in sorted_candidates[:recommendation_limit]]

        weak_point_ids = [
            concept_id
            for concept_id in concepts
            if status_map.get(concept_id, 0) == 0 and unlock_map.get(concept_id)
        ]
        weak_point_ids.sort(
            key=lambda concept_id: (
                -len(unlock_map.get(concept_id, [])),
                -(concepts[concept_id].get("difficulty") or 0),
                concepts[concept_id]["name"],
            )
        )
        weak_points = [
            WeakPointItem(
                concept=to_recommended(concept_id),
                impact_count=len(unlock_map.get(concept_id, [])),
            )
            for concept_id in weak_point_ids[:weak_point_limit]
        ]

        default_target_id = target_concept_id if target_concept_id in concepts else None
        if default_target_id is None and recommended_concepts:
            default_target_id = recommended_concepts[0].id

        def candidate_sort_key(concept_id: str) -> tuple:
            return (
                -readiness_score(concept_id),
                0 if status_map.get(concept_id, 0) == 1 else 1,
                -len(unlock_map.get(concept_id, [])),
                len(prerequisite_map.get(concept_id, [])),
                concepts[concept_id].get("difficulty") or 99,
                concepts[concept_id]["name"],
            )

        ordered_path_ids: list[str] = []
        if default_target_id:
            ordered_path_ids.append(default_target_id)
            visited_path_ids = {default_target_id}

            while len(ordered_path_ids) < path_limit:
                previous_concept_id = ordered_path_ids[-1]
                direct_unlocks = [
                    concept_id
                    for concept_id in unlock_map.get(previous_concept_id, [])
                    if concept_id not in visited_path_ids
                ]
                ready_unlocks = [
                    concept_id
                    for concept_id in direct_unlocks
                    if all(
                        prerequisite_id in visited_path_ids or status_map.get(prerequisite_id, 0) == 2
                        for prerequisite_id in prerequisite_map.get(concept_id, [])
                    )
                ]

                candidate_pool = ready_unlocks or direct_unlocks
                if not candidate_pool:
                    reachable_candidates: set[str] = set()
                    frontier = [concept_id for concept_id in ordered_path_ids]
                    seen_frontier = set(frontier)
                    while frontier:
                        current_id = frontier.pop(0)
                        for next_id in unlock_map.get(current_id, []):
                            if next_id in seen_frontier:
                                continue
                            seen_frontier.add(next_id)
                            frontier.append(next_id)
                            if next_id not in visited_path_ids:
                                reachable_candidates.add(next_id)
                    candidate_pool = list(reachable_candidates)

                if not candidate_pool:
                    break

                next_concept_id = sorted(candidate_pool, key=candidate_sort_key)[0]
                visited_path_ids.add(next_concept_id)
                ordered_path_ids.append(next_concept_id)

        learning_path = []
        for index, concept_id in enumerate(ordered_path_ids, start=1):
            if index == 1:
                reason = "作为你当前选择的起点知识点，建议先完成这一节点。"
            else:
                previous_concept_id = ordered_path_ids[index - 2]
                previous_name = concepts[previous_concept_id]["name"]
                if status_map.get(concept_id, 0) == 1:
                    reason = f"该节点与上一步“{previous_name}”直接衔接，且你已处于学习中，建议继续完成。"
                else:
                    reason = f"完成“{previous_name}”后，建议继续学习这一节点，作为后续进阶路径。"

            learning_path.append(
                LearningPathStep(
                    step=index,
                    concept=to_recommended(concept_id),
                    reason=reason,
                )
            )

        default_target = to_recommended(default_target_id) if default_target_id else None

        return RecommendOverviewResponse(
            progress_rate=progress_rate,
            total_concepts=total_concepts,
            mastered_count=mastered_count,
            in_progress_count=in_progress_count,
            unlearned_count=unlearned_count,
            recommended_concepts=recommended_concepts,
            weak_points=weak_points,
            default_target=default_target,
            learning_path=learning_path,
        )


def get_recommendation_service(driver: Driver = Depends(get_neo4j_driver)) -> RecommendationService:
    return RecommendationService(driver)
