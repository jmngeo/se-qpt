"""
Find most similar role cluster using distance metrics (from Derik's system)
Uses Euclidean, Manhattan, and Cosine distances on competency vectors
"""
import numpy as np
from sqlalchemy import func
from sqlalchemy.orm import Session
from models import db, RoleCompetencyMatrix


def find_most_similar_role_cluster(organization_id, user_scores):
    """
    Finds the most similar role cluster based on Euclidean, Manhattan, and Cosine distances.

    Parameters:
    - organization_id: int, the ID of the organization to filter the query.
    - user_scores: list of dicts with 'competency_id' and 'score' keys

    Returns:
    - list: role_cluster_ids with minimum Euclidean distance (primary metric)
    """
    # Query the database for competency values grouped by role_cluster_id and competency_id
    results = (
        db.session.query(
            RoleCompetencyMatrix.role_cluster_id,
            RoleCompetencyMatrix.competency_id,
            func.sum(RoleCompetencyMatrix.role_competency_value).label('role_competency_value')
        )
        .filter(RoleCompetencyMatrix.organization_id == organization_id)
        .group_by(RoleCompetencyMatrix.competency_id, RoleCompetencyMatrix.role_cluster_id)
        .order_by(RoleCompetencyMatrix.role_cluster_id)
        .all()
    )

    # Organize the results into vectors for each role cluster
    role_clusters = {}
    for row in results:
        role_cluster_id = row.role_cluster_id
        competency_id = row.competency_id
        competency_value = row.role_competency_value

        if role_cluster_id not in role_clusters:
            role_clusters[role_cluster_id] = {}
        role_clusters[role_cluster_id][competency_id] = competency_value

    # Create competency vectors
    all_competency_ids = sorted(
        {row.competency_id for row in results}
    )

    # Create a mapping of competency_id to score from user_scores
    user_scores_map = {entry['competency_id']: entry['score'] for entry in user_scores}

    # Build the new role vector using user_scores_map
    new_role_vector = np.array([user_scores_map.get(c_id, 0) for c_id in all_competency_ids])

    # Ensure consistent ordering of competencies
    existing_roles = {
        role_cluster: np.array([role_clusters[role_cluster].get(c_id, 0) for c_id in all_competency_ids])
        for role_cluster in role_clusters
    }

    # Define distance functions
    def euclidean_distance(vec1, vec2):
        return np.linalg.norm(vec1 - vec2)

    def manhattan_distance(vec1, vec2):
        return np.sum(np.abs(vec1 - vec2))

    def cosine_distance(vec1, vec2):
        dot_product = np.dot(vec1, vec2)
        magnitude1 = np.linalg.norm(vec1)
        magnitude2 = np.linalg.norm(vec2)
        if magnitude1 == 0 or magnitude2 == 0:
            return 1.0  # Maximum distance if either vector is zero
        return 1 - (dot_product / (magnitude1 * magnitude2))

    # Compute distances
    distances = {
        "euclidean": {},
        "manhattan": {},
        "cosine": {}
    }

    for role, vec in existing_roles.items():
        distances["euclidean"][role] = euclidean_distance(new_role_vector, vec)
        distances["manhattan"][role] = manhattan_distance(new_role_vector, vec)
        distances["cosine"][role] = cosine_distance(new_role_vector, vec)

    # Find all role clusters with the minimum distance for each metric
    closest_roles = {
        metric: [
            role for role, distance in roles.items()
            if distance == min(roles.values())
        ]
        for metric, roles in distances.items()
    }

    # Log the results
    print(f"[find_most_similar_role] Distances by metric: {distances}")
    print(f"[find_most_similar_role] Closest roles: {closest_roles}")

    # Return the role cluster IDs and distance info for confidence calculation
    euclidean_role_ids = closest_roles["euclidean"]
    min_euclidean_distance = min(distances["euclidean"].values()) if distances["euclidean"] else 999

    # Count how many metrics agree on the best role
    best_role_id = euclidean_role_ids[0] if euclidean_role_ids else None
    metric_agreement = sum([
        best_role_id in closest_roles["euclidean"],
        best_role_id in closest_roles["manhattan"],
        best_role_id in closest_roles["cosine"]
    ]) if best_role_id else 0

    return {
        'role_ids': euclidean_role_ids,
        'min_distance': min_euclidean_distance,
        'metric_agreement': metric_agreement,
        'distances': distances
    }
