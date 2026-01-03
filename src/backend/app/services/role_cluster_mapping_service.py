"""
AI-powered role cluster mapping service.
Maps organization-specific roles to SE role clusters using OpenAI.

Based on the SE framework by Ulf Koenemann et al.
Reference: "Identification of stakeholder-specific Systems Engineering competencies for industry"

Updated January 2026:
- Added Training Program Cluster mapping for Phase 3 "Macro Planning"
- LLM now returns both SE Role Cluster (for competency mapping) and
  Training Program Cluster (for Phase 3 training organization)
"""

import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
import uuid


class RoleClusterMappingService:
    """Service for mapping organization roles to SE role clusters"""

    def __init__(self, db_session=None):
        """
        Initialize the service

        Args:
            db_session: SQLAlchemy database session (optional, for standalone use)
        """
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        # Use gpt-4o-mini for cost-effective role mapping (90% cheaper than gpt-4-turbo)
        # Supports JSON mode and provides good reasoning for role classification
        self.model = "gpt-4o-mini"
        self.db_session = db_session

    def get_all_role_clusters_from_db(self):
        """Fetch all 14 SE role clusters from database"""
        if not self.db_session:
            raise ValueError("Database session not provided")

        from app.models import RoleCluster
        clusters = self.db_session.query(RoleCluster).order_by(RoleCluster.id).all()
        return [
            {
                'id': cluster.id,
                'name': cluster.role_cluster_name,
                'description': cluster.role_cluster_description
            }
            for cluster in clusters
        ]

    def get_all_role_clusters_static(self) -> List[Dict[str, Any]]:
        """
        Get all 14 SE role clusters (static version for POC)
        This can be used when database is not available
        """
        return [
            {
                'id': 1,
                'name': 'Customer',
                'description': 'Party that orders or uses the service/product with influence on system design.'
            },
            {
                'id': 2,
                'name': 'Customer Representative',
                'description': 'Interface between customer and company, voice for customer requirements.'
            },
            {
                'id': 3,
                'name': 'Project Manager',
                'description': 'Responsible for project planning, coordination, and achieving goals within constraints.'
            },
            {
                'id': 4,
                'name': 'System Engineer',
                'description': 'Oversees requirements, system decomposition, interfaces, and integration planning.'
            },
            {
                'id': 5,
                'name': 'Specialist Developer',
                'description': 'Develops in specific areas (software, hardware, etc.) based on system specifications.'
            },
            {
                'id': 6,
                'name': 'Production Planner/Coordinator',
                'description': 'Prepares product realization and transfer to customer.'
            },
            {
                'id': 7,
                'name': 'Production Employee',
                'description': 'Handles implementation, assembly, manufacture, and product integration.'
            },
            {
                'id': 8,
                'name': 'Quality Engineer/Manager',
                'description': 'Ensures quality standards are maintained and cooperates with V&V.'
            },
            {
                'id': 9,
                'name': 'Verification and Validation (V&V) Operator',
                'description': 'Performs system verification and validation activities.'
            },
            {
                'id': 10,
                'name': 'Service Technician',
                'description': 'Handles installation, commissioning, training, maintenance, and repair.'
            },
            {
                'id': 11,
                'name': 'Process and Policy Manager',
                'description': 'Develops internal guidelines and monitors process compliance.'
            },
            {
                'id': 12,
                'name': 'Internal Support',
                'description': 'Provides advisory and support during development (IT, qualification, SE support).'
            },
            {
                'id': 13,
                'name': 'Innovation Management',
                'description': 'Focuses on commercial implementation of products/services and new business models.'
            },
            {
                'id': 14,
                'name': 'Management',
                'description': 'Decision-makers providing company vision, goals, and project oversight.'
            }
        ]

    def get_training_program_clusters_static(self) -> List[Dict[str, Any]]:
        """
        Get the 6 Training Program Clusters for Phase 3 "Macro Planning"

        IMPORTANT: These are NOT the same as the 14 SE Role Clusters.
        - 14 SE Role Clusters: Used for competency profile mapping (Phase 1/2)
        - 6 Training Program Clusters: Used for training organization (Phase 3)

        Training Program Clusters group organization roles into sensible
        training cohorts from an organizational perspective.
        """
        return [
            {
                'id': 1,
                'key': 'engineers',
                'name': 'Engineers',
                'training_program_name': 'SE for Engineers',
                'description': 'Technical practitioners who design, develop, and implement systems',
                'typical_roles': ['Software Engineers', 'Hardware Engineers', 'System Engineers',
                                  'Test Engineers', 'Requirements Engineers', 'System Architects']
            },
            {
                'id': 2,
                'key': 'managers',
                'name': 'Managers',
                'training_program_name': 'SE for Managers',
                'description': 'Leadership roles responsible for planning, coordination, and decision-making',
                'typical_roles': ['Project Managers', 'Department Heads', 'Team Leads',
                                  'Product Managers', 'Program Managers']
            },
            {
                'id': 3,
                'key': 'executives',
                'name': 'Executives',
                'training_program_name': 'SE for Executives',
                'description': 'Senior leadership with strategic oversight',
                'typical_roles': ['Directors', 'VPs', 'C-Level Executives', 'Senior Management']
            },
            {
                'id': 4,
                'key': 'support_staff',
                'name': 'Support Staff',
                'training_program_name': 'SE for Support Staff',
                'description': 'Roles providing technical and operational support',
                'typical_roles': ['Quality Engineers', 'Configuration Managers', 'IT Support',
                                  'Documentation Specialists']
            },
            {
                'id': 5,
                'key': 'external_partners',
                'name': 'External Partners',
                'training_program_name': 'SE for Partners',
                'description': 'Customer-facing and supplier-facing roles',
                'typical_roles': ['Customer Representatives', 'Account Managers',
                                  'Supplier Managers', 'Sales Engineers']
            },
            {
                'id': 6,
                'key': 'operations',
                'name': 'Operations',
                'training_program_name': 'SE for Operations',
                'description': 'Roles focused on production, deployment, and maintenance',
                'typical_roles': ['Production Engineers', 'Service Technicians',
                                  'Field Engineers', 'Operations Staff']
            }
        ]

    def get_training_program_clusters_from_db(self):
        """Fetch the 6 Training Program Clusters from database"""
        if not self.db_session:
            raise ValueError("Database session not provided")

        from sqlalchemy import text
        result = self.db_session.execute(
            text("SELECT id, cluster_key, cluster_name, training_program_name, description FROM training_program_cluster ORDER BY id")
        )
        return [
            {
                'id': row.id,
                'key': row.cluster_key,
                'name': row.cluster_name,
                'training_program_name': row.training_program_name,
                'description': row.description
            }
            for row in result
        ]

    def build_mapping_prompt(self,
                            org_role_title: str,
                            org_role_description: str,
                            org_role_responsibilities: Optional[List[str]] = None,
                            org_role_skills: Optional[List[str]] = None,
                            role_clusters: Optional[List[Dict[str, Any]]] = None,
                            training_program_clusters: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Build the prompt for OpenAI to map a role to both:
        1. SE Role Clusters (14 clusters for competency mapping)
        2. Training Program Clusters (6 clusters for Phase 3 training organization)
        """

        if role_clusters is None:
            role_clusters = self.get_all_role_clusters_static()

        if training_program_clusters is None:
            training_program_clusters = self.get_training_program_clusters_static()

        # Format SE role clusters for the prompt
        se_clusters_text = "\n".join([
            f"{cluster['id']}. **{cluster['name']}**: {cluster['description']}"
            for cluster in role_clusters
        ])

        # Format Training Program Clusters for the prompt
        tp_clusters_text = "\n".join([
            f"{cluster['id']}. **{cluster['name']}** ({cluster['training_program_name']}): {cluster['description']}"
            for cluster in training_program_clusters
        ])

        # Build role information section
        role_info = f"**Role Title**: {org_role_title}\n\n**Role Description**: {org_role_description}"

        if org_role_responsibilities:
            role_info += f"\n\n**Key Responsibilities**:\n" + "\n".join([f"- {r}" for r in org_role_responsibilities])

        if org_role_skills:
            role_info += f"\n\n**Required Skills**:\n" + "\n".join([f"- {s}" for s in org_role_skills])

        prompt = f"""You are an expert in Systems Engineering role classification based on the SE framework developed by Ulf Koenemann et al. at Fraunhofer IEM.

Your task is to analyze the provided organization role and determine:
1. The best matching **SE Role Cluster** (for competency profile mapping)
2. The best matching **Training Program Cluster** (for training organization in Phase 3)

## Organization Role to Analyze:

{role_info}

## PART A: 14 SE Role Clusters (for competency profile mapping)

These clusters define the competency profiles needed for different SE roles:

{se_clusters_text}

## PART B: 6 Training Program Clusters (for training organization)

These clusters group roles into training cohorts. This is DIFFERENT from SE Role Clusters:

{tp_clusters_text}

## Instructions:

### SE Role Cluster Assignment:

1. Analyze the role's responsibilities, skills, and description carefully
2. **CRITICAL: Check if this is a Systems Engineering role first**
   - SE roles involve: requirements, design, integration, testing, V&V, technical coordination, production, quality, service
   - SE roles can include: project management, process management, innovation management, technical support
   - SE roles are primarily technical/engineering-focused with product/system development context
3. **EXCLUDE these PURE business roles completely** (return empty mappings array):
   - **Pure Payroll/Benefits**: Employee compensation, benefits administration, payroll processing
   - **Pure Finance/Accounting**: Bookkeeping, financial reporting, tax preparation
   - **Pure Marketing**: Advertising campaigns, brand management, social media marketing
   - **Pure Sales**: Sales quotas, commission management, CRM systems (NOT technical sales)
   - **Pure Legal**: Contract law, litigation, legal counsel (NOT engineering compliance)
   - **Pure Administration**: Office management, facilities management, receptionist
4. Identify which SE role cluster(s) best match this role **ONLY if there is strong alignment**
5. Provide a confidence score (0-100%) for each mapping
6. **ONLY include mappings with confidence >= 80%**
7. Mark the strongest match as the primary mapping

### Training Program Cluster Assignment:

8. **ALWAYS assign a Training Program Cluster** if the role has any SE Role Cluster mapping
9. Choose based on organizational perspective (how people are typically grouped for training):
   - **Engineers (1)**: Hands-on technical practitioners (developers, architects, testers)
   - **Managers (2)**: Mid-level leadership (project managers, team leads, department heads)
   - **Executives (3)**: Senior leadership (directors, VPs, C-level)
   - **Support Staff (4)**: Supporting functions (QA, config mgmt, IT support, documentation)
   - **External Partners (5)**: Customer/supplier facing (account mgrs, sales engineers)
   - **Operations (6)**: Production and maintenance (field engineers, service technicians)

## Response Format (JSON):

Return your analysis in the following JSON format:

{{
  "se_role_mappings": [
    {{
      "cluster_id": 4,
      "cluster_name": "System Engineer",
      "confidence_score": 92,
      "reasoning": "Detailed explanation of why this cluster matches",
      "matched_responsibilities": ["Specific responsibility 1", "Specific responsibility 2"],
      "is_primary": true
    }}
  ],
  "training_program_cluster": {{
    "cluster_id": 1,
    "cluster_name": "Engineers",
    "training_program_name": "SE for Engineers",
    "reasoning": "This role involves hands-on technical work, making it suitable for the Engineers training program"
  }},
  "overall_analysis": "Brief summary of the role's primary focus and how it fits into the SE framework. If no good SE cluster match exists, explain why."
}}

IMPORTANT:
- Return ONLY valid JSON, no additional text or markdown formatting
- Use exact cluster names and IDs from the lists provided above
- **SE Role Mappings: ONLY include with confidence >= 80%**
- **Training Program Cluster: ALWAYS assign if any SE role mapping exists**
- If SE role is pure business (non-SE), return "se_role_mappings": [] AND "training_program_cluster": null
- If SE mappings exist, mark exactly ONE as "is_primary": true (the best match)
- Order SE mappings by confidence_score (highest first)
"""

        return prompt

    def map_single_role(self,
                       org_role_title: str,
                       org_role_description: str,
                       org_role_responsibilities: Optional[List[str]] = None,
                       org_role_skills: Optional[List[str]] = None,
                       role_clusters: Optional[List[Dict[str, Any]]] = None,
                       training_program_clusters: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Use AI to map a single organization role to:
        1. SE Role Clusters (for competency profile mapping)
        2. Training Program Cluster (for Phase 3 training organization)

        Args:
            org_role_title: The title of the organization's role
            org_role_description: Description of what this role does
            org_role_responsibilities: List of key responsibilities
            org_role_skills: List of required skills
            role_clusters: Optional list of SE role clusters (uses static if not provided)
            training_program_clusters: Optional list of training program clusters (uses static if not provided)

        Returns:
            {
                'mappings': [  # Backward-compatible SE role mappings
                    {
                        'cluster_name': '...',
                        'cluster_id': X,
                        'confidence_score': 85,
                        'reasoning': '...',
                        'matched_responsibilities': [...],
                        'is_primary': true
                    }
                ],
                'se_role_mappings': [  # Same as mappings, for clarity
                    ...
                ],
                'training_program_cluster': {  # NEW: Training Program Cluster for Phase 3
                    'cluster_id': 1,
                    'cluster_name': 'Engineers',
                    'training_program_name': 'SE for Engineers',
                    'reasoning': '...'
                },
                'overall_analysis': '...'
            }
        """

        if role_clusters is None:
            role_clusters = self.get_all_role_clusters_static()

        if training_program_clusters is None:
            training_program_clusters = self.get_training_program_clusters_static()

        prompt = self.build_mapping_prompt(
            org_role_title,
            org_role_description,
            org_role_responsibilities,
            org_role_skills,
            role_clusters,
            training_program_clusters
        )

        try:
            print(f"[INFO] Mapping role: {org_role_title}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in Systems Engineering role classification based on the SE framework. Always return valid JSON with both SE Role Cluster and Training Program Cluster assignments."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more deterministic results
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Handle both old format (mappings) and new format (se_role_mappings)
            se_mappings = result.get('se_role_mappings', result.get('mappings', []))

            # Validate and enrich SE role cluster IDs
            role_clusters_map = {rc['name']: rc['id'] for rc in role_clusters}

            for mapping in se_mappings:
                cluster_name = mapping.get('cluster_name', '')
                cluster_id = mapping.get('cluster_id')

                if not cluster_id:
                    # Try to find exact match
                    cluster_id = role_clusters_map.get(cluster_name)

                    if not cluster_id:
                        # Try fuzzy matching (case-insensitive, partial match)
                        for name, cid in role_clusters_map.items():
                            if cluster_name.lower() in name.lower() or name.lower() in cluster_name.lower():
                                cluster_id = cid
                                mapping['cluster_name'] = name  # Update to exact name
                                break

                mapping['cluster_id'] = cluster_id

                if not cluster_id:
                    print(f"[WARNING] Could not find SE cluster ID for: {cluster_name}")

            # Validate Training Program Cluster
            tp_cluster = result.get('training_program_cluster')
            if tp_cluster:
                tp_clusters_map = {tc['name']: tc for tc in training_program_clusters}
                tp_name = tp_cluster.get('cluster_name', '')
                tp_id = tp_cluster.get('cluster_id')

                if not tp_id:
                    # Try to find by name
                    matched_tp = tp_clusters_map.get(tp_name)
                    if matched_tp:
                        tp_cluster['cluster_id'] = matched_tp['id']
                        tp_cluster['training_program_name'] = matched_tp.get('training_program_name', f"SE for {tp_name}")
                    else:
                        # Try fuzzy match
                        for name, tc in tp_clusters_map.items():
                            if tp_name.lower() in name.lower() or name.lower() in tp_name.lower():
                                tp_cluster['cluster_id'] = tc['id']
                                tp_cluster['cluster_name'] = name
                                tp_cluster['training_program_name'] = tc.get('training_program_name', f"SE for {name}")
                                break

                if not tp_cluster.get('cluster_id'):
                    print(f"[WARNING] Could not find Training Program Cluster ID for: {tp_name}")

            # Build normalized result with both old and new format
            normalized_result = {
                'mappings': se_mappings,  # Backward compatible
                'se_role_mappings': se_mappings,  # Explicit new field
                'training_program_cluster': tp_cluster,  # NEW for Phase 3
                'overall_analysis': result.get('overall_analysis', '')
            }

            se_count = len(se_mappings)
            tp_info = f", Training Program: {tp_cluster['cluster_name']}" if tp_cluster and tp_cluster.get('cluster_name') else ""
            print(f"[SUCCESS] Mapped {org_role_title} to {se_count} SE cluster(s){tp_info}")

            return normalized_result

        except Exception as e:
            print(f"[ERROR] AI mapping failed for {org_role_title}: {str(e)}")
            return {
                'mappings': [],
                'se_role_mappings': [],
                'training_program_cluster': None,
                'overall_analysis': f'Error during AI analysis: {str(e)}',
                'error': str(e)
            }

    def map_multiple_roles(self,
                          roles: List[Dict[str, Any]],
                          role_clusters: Optional[List[Dict[str, Any]]] = None,
                          training_program_clusters: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Map multiple roles at once to both SE Role Clusters and Training Program Clusters

        Args:
            roles: List of role dictionaries with keys:
                   - title (required)
                   - description (required)
                   - responsibilities (optional list)
                   - skills (optional list)
            role_clusters: Optional list of SE role clusters
            training_program_clusters: Optional list of training program clusters

        Returns:
            {
                'batch_id': '...',
                'total_roles': 5,
                'total_se_mappings': 12,
                'total_mappings': 12,  # Backward compatible
                'training_cluster_distribution': {
                    'Engineers': 3,
                    'Managers': 2
                },
                'results': [
                    {
                        'role_title': '...',
                        'mappings': [...],
                        'se_role_mappings': [...],
                        'training_program_cluster': {...},
                        'overall_analysis': '...'
                    }
                ]
            }
        """

        if role_clusters is None:
            role_clusters = self.get_all_role_clusters_static()

        if training_program_clusters is None:
            training_program_clusters = self.get_training_program_clusters_static()

        batch_id = str(uuid.uuid4())
        results = []
        total_se_mappings = 0
        training_cluster_distribution = {}

        print(f"[INFO] Starting batch mapping for {len(roles)} roles (batch_id: {batch_id})")

        for i, role_data in enumerate(roles, 1):
            role_title = role_data.get('title')
            role_description = role_data.get('description', '')
            role_responsibilities = role_data.get('responsibilities', [])
            role_skills = role_data.get('skills', [])

            print(f"[INFO] Processing role {i}/{len(roles)}: {role_title}")

            # Get AI mapping
            mapping_result = self.map_single_role(
                role_title,
                role_description,
                role_responsibilities,
                role_skills,
                role_clusters,
                training_program_clusters
            )

            se_mappings = mapping_result.get('se_role_mappings', mapping_result.get('mappings', []))
            total_se_mappings += len(se_mappings)

            # Track training cluster distribution
            tp_cluster = mapping_result.get('training_program_cluster')
            if tp_cluster and tp_cluster.get('cluster_name'):
                tp_name = tp_cluster['cluster_name']
                training_cluster_distribution[tp_name] = training_cluster_distribution.get(tp_name, 0) + 1

            results.append({
                'role_title': role_title,
                'role_description': role_description,
                'mappings': se_mappings,  # Backward compatible
                'se_role_mappings': se_mappings,
                'training_program_cluster': tp_cluster,  # NEW
                'overall_analysis': mapping_result.get('overall_analysis', ''),
                'error': mapping_result.get('error')
            })

        print(f"[SUCCESS] Batch mapping complete. Total SE mappings: {total_se_mappings}")
        if training_cluster_distribution:
            print(f"[INFO] Training Program Cluster distribution: {training_cluster_distribution}")

        return {
            'batch_id': batch_id,
            'total_roles': len(roles),
            'total_se_mappings': total_se_mappings,
            'total_mappings': total_se_mappings,  # Backward compatible
            'training_cluster_distribution': training_cluster_distribution,
            'results': results
        }

    def calculate_coverage(self,
                          mappings: List[Dict[str, Any]],
                          role_clusters: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Analyze which role clusters are present in the organization's mapped roles

        NOTE: Organizations are NOT expected to have all 14 role clusters.
        This analysis is purely informational to show which SE role clusters
        are represented in the organization's structure.

        Args:
            mappings: List of confirmed mappings with 'cluster_id' field
            role_clusters: Optional list of role clusters

        Returns:
            {
                'total_available_clusters': 14,
                'mapped_count': 6,
                'mapped_clusters': [...],
                'mapped_cluster_names': ['System Engineer', 'Specialist Developer', ...]
            }
        """

        if role_clusters is None:
            role_clusters = self.get_all_role_clusters_static()

        # Get unique cluster IDs that are mapped
        mapped_cluster_ids = set()
        for mapping in mappings:
            if isinstance(mapping, dict) and 'cluster_id' in mapping:
                mapped_cluster_ids.add(mapping['cluster_id'])

        mapped_clusters = [c for c in role_clusters if c['id'] in mapped_cluster_ids]
        mapped_cluster_names = [c['name'] for c in mapped_clusters]

        return {
            'total_available_clusters': len(role_clusters),
            'mapped_count': len(mapped_clusters),
            'mapped_clusters': mapped_clusters,
            'mapped_cluster_names': mapped_cluster_names
        }
