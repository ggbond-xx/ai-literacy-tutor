from fastapi import Depends
from neo4j import Driver

from app.core.config import settings
from app.db.neo4j import get_neo4j_driver
from app.schemas.graph import GraphEdge, GraphNode, GraphResponse
from app.services.graph_catalog import get_graph_catalog
from app.services.json_store import get_graph_overrides


class GraphService:
    def __init__(self, driver: Driver):
        self.driver = driver

    def get_full_graph(self) -> GraphResponse:
        query = """
        MATCH (c:Concept)
        OPTIONAL MATCH (c)-[r]->(related:Concept)
        RETURN collect(DISTINCT c) AS concepts, collect(DISTINCT {
            source: elementId(c),
            target: elementId(related),
            type: type(r)
        }) AS relations
        """
        with self.driver.session(database=settings.neo4j_database) as session:
            record = session.run(query).single()

        concepts = record["concepts"] if record else []
        relations = record["relations"] if record else []

        catalog_concepts, catalog_relations = get_graph_catalog()
        graph_overrides = get_graph_overrides()
        catalog_by_name = {item["name"]: item for item in catalog_concepts}
        for override in graph_overrides.get("concepts", []):
            name = override.get("name")
            if not name:
                continue
            catalog_by_name[name] = {
                **catalog_by_name.get(name, {}),
                **override,
            }
        catalog_concepts = list(catalog_by_name.values())
        override_relations = [
            (item.get("source_name"), item.get("target_name"), item.get("type", "RELATED_TO"))
            for item in graph_overrides.get("relations", [])
            if item.get("source_name") and item.get("target_name")
        ]
        relation_replacements = set(graph_overrides.get("relation_replacements", []))
        if relation_replacements:
            catalog_relations = [
                item
                for item in catalog_relations
                if item[0] not in relation_replacements and item[1] not in relation_replacements
            ]
        catalog_relations = [*catalog_relations, *override_relations]
        catalog_by_name = {item["name"]: item for item in catalog_concepts}
        nodes_by_name: dict[str, GraphNode] = {}
        id_by_name: dict[str, str] = {}

        for node in concepts:
            name = node.get("name", "")
            catalog_item = catalog_by_name.get(name, {})
            node_id = str(node.element_id if getattr(node, "element_id", None) else node.id)
            nodes_by_name[name] = GraphNode(
                id=node_id,
                name=name,
                description=catalog_item.get("description") or node.get("description"),
                category=catalog_item.get("category") or node.get("category"),
                difficulty=catalog_item.get("difficulty") or node.get("difficulty"),
                estimated_minutes=catalog_item.get("estimated_minutes"),
                key_points=catalog_item.get("key_points", []),
                text_material=catalog_item.get("text_material"),
                image_url=catalog_item.get("image_url"),
                video_title=catalog_item.get("video_title"),
                video_url=catalog_item.get("video_url"),
                resource_links=catalog_item.get("resource_links", []),
                study_tips=catalog_item.get("study_tips", []),
                common_mistakes=catalog_item.get("common_mistakes", []),
                practice_task=catalog_item.get("practice_task"),
                quiz=catalog_item.get("quiz", []),
                origin=catalog_item.get("origin") or "neo4j",
            )
            id_by_name[name] = node_id

        for item in catalog_concepts:
            if item["name"] in nodes_by_name:
                continue
            node_id = f"catalog:{item['slug']}"
            nodes_by_name[item["name"]] = GraphNode(
                id=node_id,
                name=item["name"],
                description=item.get("description"),
                category=item.get("category"),
                difficulty=item.get("difficulty"),
                estimated_minutes=item.get("estimated_minutes"),
                key_points=item.get("key_points", []),
                text_material=item.get("text_material"),
                image_url=item.get("image_url"),
                video_title=item.get("video_title"),
                video_url=item.get("video_url"),
                resource_links=item.get("resource_links", []),
                study_tips=item.get("study_tips", []),
                common_mistakes=item.get("common_mistakes", []),
                practice_task=item.get("practice_task"),
                quiz=item.get("quiz", []),
                origin=item.get("origin") or "catalog",
            )
            id_by_name[item["name"]] = node_id

        nodes = list(nodes_by_name.values())
        valid_ids = {node.id for node in nodes}
        links = [
            GraphEdge(source=item["source"], target=item["target"], type=item["type"])
            for item in relations
            if item["source"] and item["target"] and item["source"] in valid_ids and item["target"] in valid_ids
        ]

        existing_edges = {(edge.source, edge.target, edge.type) for edge in links}
        for source_name, target_name, relation_type in catalog_relations:
            source_id = id_by_name.get(source_name)
            target_id = id_by_name.get(target_name)
            if not source_id or not target_id:
                continue
            key = (source_id, target_id, relation_type)
            if key in existing_edges:
                continue
            links.append(GraphEdge(source=source_id, target=target_id, type=relation_type))
            existing_edges.add(key)

        return GraphResponse(nodes=nodes, links=links)


def get_graph_service(driver: Driver = Depends(get_neo4j_driver)) -> GraphService:
    return GraphService(driver)
