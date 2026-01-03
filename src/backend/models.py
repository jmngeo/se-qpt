"""
SE-QPT Unified Database Models
Combines Marcel's methodology, Derik's competency assessment, MVP features, and RAG-LLM innovations

This file unifies three previously separate model files:
- models.py (SE-QPT main models)
- unified_models.py (Derik's competency assessment models
- mvp_models.py (MVP/simplified models)

Author: Integration Team
Date: 2025-10-20
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import json
import hashlib
import time
import math

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================
db = SQLAlchemy()


# =============================================================================
# SECTION 1: CORE ENTITIES (Derik's Foundation)
# =============================================================================

class Organization(db.Model):
    """
    Derik's organization table - EXTENDED for SE-QPT Phase 1
    Uses Derik's existing table structure with SE-QPT additions
    """
    __tablename__ = 'organization'

    # Derik's original fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    organization_name = db.Column(db.String(255), nullable=False, unique=True)
    organization_public_key = db.Column(db.String(50), nullable=False, unique=True,
                                       default='singleuser')

    # SE-QPT Phase 1 extensions (NEW COLUMNS - added via migration)
    size = db.Column(db.String(20))  # 'small', 'medium', 'large', 'enterprise'
    maturity_score = db.Column(db.Float)  # Overall maturity score (0-5)
    selected_archetype = db.Column(db.String(100))  # Selected qualification archetype
    phase1_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_public_key(org_name):
        """Generate unique organization public key"""
        base = f"{org_name}_{int(time.time() * 1000)}"
        hash_key = hashlib.sha256(base.encode()).hexdigest()[:16].upper()

        # Check uniqueness
        while Organization.query.filter_by(organization_public_key=hash_key).first():
            base = f"{org_name}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:4]}"
            hash_key = hashlib.sha256(base.encode()).hexdigest()[:16].upper()

        return hash_key

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.organization_name,
            'organization_code': self.organization_public_key,  # Alias for frontend compatibility
            'size': self.size,
            'maturity_score': self.maturity_score,
            'selected_archetype': self.selected_archetype,
            'phase1_completed': self.phase1_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Competency(db.Model):
    """
    Derik's 16 SE competencies
    Based on INCOSE competency framework
    """
    __tablename__ = 'competency'

    id = db.Column(db.Integer, primary_key=True)
    competency_name = db.Column(db.String(255), nullable=False)
    competency_area = db.Column(db.String(50))  # 'Core', 'Technical', 'Management', etc.
    description = db.Column(db.Text)
    why_it_matters = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.competency_name,
            'area': self.competency_area,
            'description': self.description,
            'why_it_matters': self.why_it_matters
        }


class CompetencyIndicator(db.Model):
    """
    Derik's competency indicators - specific observable behaviors for each competency
    Organized by proficiency level (1-4)
    """
    __tablename__ = 'competency_indicators'

    id = db.Column(db.Integer, primary_key=True)
    competency_id = db.Column(db.Integer, db.ForeignKey('competency.id'), nullable=True)
    level = db.Column(db.String(50), nullable=True)  # Can hold 'verstehen', 'beherrschen', 'kennen', 'anwenden'
    indicator_en = db.Column(db.Text, nullable=True)  # English indicator text
    indicator_de = db.Column(db.Text, nullable=True)  # German indicator text

    # Relationship to Competency
    competency = db.relationship('Competency', backref=db.backref('indicators', cascade="all, delete-orphan", lazy=True))


class RoleCluster(db.Model):
    """
    Standard SE Role Clusters (14 INCOSE Reference Roles)
    =====================================================

    This is a REFERENCE table containing standard Systems Engineering role definitions
    from INCOSE (International Council on Systems Engineering).

    IMPORTANT DISTINCTION:
    - role_cluster: Standard reference roles (this table) - READ ONLY
    - organization_roles: Organization-specific custom roles - USED IN PHASE 2 ALGORITHM

    Purpose: Provides standard role templates that organizations can:
    1. Select and customize for their organization (Phase 1 Task 2)
    2. Use as reference when defining custom roles

    Examples: "Systems Engineer", "Requirements Engineer", "Test Engineer"

    Note: The Phase 2 algorithm does NOT use this table directly.
          It uses organization_roles (user-defined roles from Phase 1).
    """
    __tablename__ = 'role_cluster'

    id = db.Column(db.Integer, primary_key=True)
    role_cluster_name = db.Column(db.String(255), nullable=False)
    role_cluster_description = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.role_cluster_name,
            'description': self.role_cluster_description
        }


class TrainingProgramCluster(db.Model):
    """
    Training Program Clusters for Phase 3 "Macro Planning"
    =======================================================

    Created: January 2026

    IMPORTANT: These are NOT the same as the 14 SE Role Clusters (role_cluster table).

    Distinction:
    - 14 SE Role Clusters (role_cluster): Used for competency profile mapping in Phase 1/2
    - 6 Training Program Clusters (this table): Used for organizing training delivery in Phase 3

    Purpose:
    - Group organization roles into sensible training cohorts from an organizational perspective
    - Enable "Role-Clustered Based View" in Phase 3 training structure

    The 6 Training Program Clusters:
    1. Engineers - Technical practitioners (developers, architects, testers)
    2. Managers - Mid-level leadership (project managers, team leads)
    3. Executives - Senior leadership (directors, VPs, C-level)
    4. Support Staff - Supporting functions (QA, config mgmt, IT support)
    5. External Partners - Customer/supplier facing roles
    6. Operations - Production, deployment, and maintenance roles

    Training Program Names:
    - "SE for Engineers", "SE for Managers", etc.
    """
    __tablename__ = 'training_program_cluster'

    id = db.Column(db.Integer, primary_key=True)
    cluster_key = db.Column(db.String(50), unique=True, nullable=False)
    cluster_name = db.Column(db.String(100), nullable=False)
    training_program_name = db.Column(db.String(100), nullable=False)  # e.g., "SE for Engineers"
    description = db.Column(db.Text)
    typical_org_roles = db.Column(db.Text)  # JSON array of example organization roles
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.cluster_key,
            'name': self.cluster_name,
            'training_program_name': self.training_program_name,
            'description': self.description,
            'typical_org_roles': json.loads(self.typical_org_roles) if self.typical_org_roles else []
        }


class OrganizationRoleMapping(db.Model):
    """
    AI-Powered Organization Role Mappings to SE-QPT Role Clusters
    ==============================================================

    Created via AI-powered role mapping feature in Phase 1 Task 2.

    Purpose:
    - Stores mappings of organization-specific job roles to standard SE role clusters
    - Uses OpenAI to automatically analyze role descriptions and suggest mappings
    - Provides confidence scores and reasoning for each mapping
    - Enables coverage analysis (which SE role clusters are covered/missing)

    How it works:
    1. Organization uploads their job role descriptions (title, description, responsibilities, skills)
    2. AI (GPT-4) analyzes each role and maps it to one or more SE role clusters
    3. AI provides confidence scores (0-100%) and reasoning for each mapping
    4. User reviews and confirms/rejects AI suggestions
    5. Confirmed mappings are used for coverage analysis

    Example:
    - Org Role: "Senior Embedded Software Developer"
    - AI Maps to:
      * Specialist Developer (85% confidence, PRIMARY)
      * System Engineer (40% confidence, SECONDARY)

    Note: This is OPTIONAL automation to help organizations quickly map their roles.
          Organizations can still manually select roles without using this feature.
    """
    __tablename__ = 'organization_role_mappings'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id', ondelete='CASCADE'), nullable=False)

    # Organization's custom role information
    org_role_title = db.Column(db.String(255), nullable=False)
    org_role_description = db.Column(db.Text)
    org_role_responsibilities = db.Column(db.Text)  # JSON array
    org_role_skills = db.Column(db.Text)  # JSON array

    # Mapping to SE role cluster (for competency profile)
    mapped_cluster_id = db.Column(db.Integer, db.ForeignKey('role_cluster.id'), nullable=False)

    # Mapping to Training Program Cluster (for Phase 3 training organization)
    # Added January 2026 for Phase 3 "Macro Planning"
    # Note: This is a DIFFERENT concept from mapped_cluster_id (14 SE Role Clusters vs 6 Training Program Clusters)
    training_program_cluster_id = db.Column(db.Integer, db.ForeignKey('training_program_cluster.id'), nullable=True)

    # AI analysis metadata
    confidence_score = db.Column(db.Numeric(5, 2))
    mapping_reasoning = db.Column(db.Text)
    matched_responsibilities = db.Column(db.Text)  # JSON array

    # User validation
    user_confirmed = db.Column(db.Boolean, default=False)
    confirmed_by = db.Column(db.Integer, db.ForeignKey('new_survey_user.id'))
    confirmed_at = db.Column(db.DateTime)

    # Source tracking
    upload_source = db.Column(db.String(50))  # 'manual', 'file_upload', 'api', 'ai_batch'
    upload_batch_id = db.Column(db.String(36))  # UUID

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = db.relationship('Organization', backref='role_mappings')
    role_cluster = db.relationship('RoleCluster', backref='org_mappings')
    training_program_cluster = db.relationship('TrainingProgramCluster', backref='org_mappings')

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        result = {
            'id': self.id,
            'organization_id': self.organization_id,
            'org_role_title': self.org_role_title,
            'org_role_description': self.org_role_description,
            'org_role_responsibilities': json.loads(self.org_role_responsibilities) if self.org_role_responsibilities else [],
            'org_role_skills': json.loads(self.org_role_skills) if self.org_role_skills else [],
            'mapped_cluster': {
                'id': self.mapped_cluster_id,
                'name': self.role_cluster.role_cluster_name if self.role_cluster else None,
                'description': self.role_cluster.role_cluster_description if self.role_cluster else None
            } if self.role_cluster else None,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'mapping_reasoning': self.mapping_reasoning,
            'matched_responsibilities': json.loads(self.matched_responsibilities) if self.matched_responsibilities else [],
            'user_confirmed': self.user_confirmed,
            'upload_source': self.upload_source,
            'upload_batch_id': self.upload_batch_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        # Add Training Program Cluster for Phase 3 (if set)
        if self.training_program_cluster_id:
            result['training_program_cluster'] = {
                'id': self.training_program_cluster_id,
                'name': self.training_program_cluster.cluster_name if self.training_program_cluster else None,
                'training_program_name': self.training_program_cluster.training_program_name if self.training_program_cluster else None
            }
        else:
            result['training_program_cluster'] = None

        return result


class OrganizationRoles(db.Model):
    """
    Organization-Specific User-Defined Roles (PHASE 2 ALGORITHM USES THIS!)
    ========================================================================

    Created during Phase 1 Task 2 (Role Identification).

    IMPORTANT: This is the PRIMARY role table used by Phase 2 algorithm.

    How it works:
    1. Phase 1 Task 2: User defines roles for their organization by either:
       a) Selecting from 14 standard role clusters (role_cluster table) and customizing
       b) Creating completely custom roles with no standard mapping

    2. Phase 2 Algorithm: Uses THESE roles (not role_cluster) to:
       - Map roles → competency requirements (via role_competency_matrix)
       - Analyze user competency gaps
       - Generate learning recommendations

    Examples:
    - "Systems Engineer" (standard_role_cluster_id = 1, customized name)
    - "Embedded Software Developer" (standard_role_cluster_id = NULL, fully custom)
    - "QA Lead" (standard_role_cluster_id = 5, customized name)

    Relationship to role_cluster:
    - standard_role_cluster_id: OPTIONAL reference to role_cluster (for standard-based roles)
    - NULL if role is fully custom

    Created: 2025-10-29 (Migration 001_create_organization_roles_with_migration.sql)
    """
    __tablename__ = 'organization_roles'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id', ondelete='CASCADE'), nullable=False)
    role_name = db.Column(db.String(255), nullable=False)
    role_description = db.Column(db.Text)
    standard_role_cluster_id = db.Column(db.Integer, db.ForeignKey('role_cluster.id'))
    training_program_cluster_id = db.Column(db.Integer, db.ForeignKey('training_program_cluster.id'))  # Phase 3
    identification_method = db.Column(db.String(50), default='STANDARD')  # 'STANDARD' or 'CUSTOM' or 'TASK_BASED'
    participating_in_training = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = db.relationship('Organization', backref=db.backref('org_roles', cascade="all, delete-orphan", lazy=True))
    standard_cluster = db.relationship('RoleCluster', backref='organization_role_mappings')
    training_cluster = db.relationship('TrainingProgramCluster', backref='organization_roles')

    __table_args__ = (
        db.UniqueConstraint('organization_id', 'role_name', name='organization_roles_organization_id_role_name_key'),
    )

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'name': self.role_name,  # For DerikCompetencyBridge.vue (role.name)
            'description': self.role_description,  # For DerikCompetencyBridge.vue (role.description)
            'orgRoleName': self.role_name,  # For Phase 1 Task 2 components
            'role_name': self.role_name,
            'role_description': self.role_description,
            'standardRoleId': self.standard_role_cluster_id,  # Frontend expects this key
            'standard_role_cluster_id': self.standard_role_cluster_id,
            'standardRoleName': self.standard_cluster.role_cluster_name if self.standard_cluster else None,
            'standard_role_description': self.standard_cluster.role_cluster_description if self.standard_cluster else None,
            'training_program_cluster_id': self.training_program_cluster_id,  # Phase 3
            'trainingClusterId': self.training_program_cluster_id,  # Frontend key
            'trainingClusterName': self.training_cluster.cluster_name if self.training_cluster else None,
            'trainingProgramName': self.training_cluster.training_program_name if self.training_cluster else None,
            'identificationMethod': self.identification_method,  # Frontend expects this key
            'identification_method': self.identification_method,
            'participating_in_training': self.participating_in_training,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# =============================================================================
# SECTION 2: ISO/IEC 15288 PROCESS MODELS (Derik's Task-Based Role Mapping)
# =============================================================================

class IsoSystemLifeCycleProcesses(db.Model):
    """
    ISO/IEC 15288 System Life Cycle Process Groups
    Four main process groups: Agreement, Organizational, Technical, Project
    """
    __tablename__ = 'iso_system_life_cycle_processes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    # Relationships
    processes = db.relationship('IsoProcesses', backref='life_cycle_process', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class IsoProcesses(db.Model):
    """
    ISO/IEC 15288 System Engineering Processes
    Approximately 30 processes defined in the standard
    """
    __tablename__ = 'iso_processes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    life_cycle_process_id = db.Column(db.Integer, db.ForeignKey('iso_system_life_cycle_processes.id'))

    # Relationships removed: IsoActivities model was deleted in Phase 2A cleanup

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'life_cycle_process_id': self.life_cycle_process_id
        }


class RoleProcessMatrix(db.Model):
    """
    Maps organization-specific roles to ISO processes
    Defines which processes each role is involved in and at what level

    NOTE: Column 'role_cluster_id' is a legacy name - it actually references
    organization_roles.id (user-defined roles), not role_cluster.id.
    Name kept for backward compatibility.

    Updated: 2025-10-30 - FK changed from role_cluster to organization_roles
    """
    __tablename__ = 'role_process_matrix'

    id = db.Column(db.Integer, primary_key=True)
    role_cluster_id = db.Column(db.Integer, db.ForeignKey('organization_roles.id', ondelete='CASCADE'), nullable=False)
    iso_process_id = db.Column(db.Integer, db.ForeignKey('iso_processes.id'), nullable=False)
    role_process_value = db.Column(db.Integer, nullable=False, default=-100)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)

    # Relationships
    organization_role = db.relationship('OrganizationRoles', backref=db.backref('process_matrices', cascade="all, delete-orphan", lazy=True))
    iso_process = db.relationship('IsoProcesses', backref=db.backref('role_process_matrices', cascade="all, delete-orphan", lazy=True))
    organization = db.relationship('Organization', backref=db.backref('role_process_matrices', cascade="all, delete-orphan", lazy=True))

    __table_args__ = (
        db.UniqueConstraint('organization_id', 'role_cluster_id', 'iso_process_id', name='role_process_matrix_unique'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'role_cluster_id': self.role_cluster_id,
            'iso_process_id': self.iso_process_id,
            'role_process_value': self.role_process_value,
            'organization_id': self.organization_id
        }


class ProcessCompetencyMatrix(db.Model):
    """
    Maps ISO processes to competencies
    Defines which competencies are required for each process
    """
    __tablename__ = 'process_competency_matrix'

    id = db.Column(db.Integer, primary_key=True)
    iso_process_id = db.Column(db.Integer, db.ForeignKey('iso_processes.id'), nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey('competency.id'), nullable=False)
    process_competency_value = db.Column(db.Integer, nullable=False, default=-100)

    # Relationships
    iso_process = db.relationship('IsoProcesses', backref=db.backref('competency_matrices', cascade="all, delete-orphan", lazy=True))
    competency = db.relationship('Competency', backref=db.backref('process_matrices', cascade="all, delete-orphan", lazy=True))

    __table_args__ = (
        db.UniqueConstraint('iso_process_id', 'competency_id', name='process_competency_matrix_unique'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'iso_process_id': self.iso_process_id,
            'competency_id': self.competency_id,
            'process_competency_value': self.process_competency_value
        }


class RoleCompetencyMatrix(db.Model):
    """
    Role → Competency Requirements Matrix (PHASE 2 ALGORITHM USES THIS!)
    ====================================================================

    Maps organization-specific roles to required competency levels.
    Calculated from: RoleProcessMatrix × ProcessCompetencyMatrix

    CRITICAL NAMING CONFUSION (read carefully!):
    ┌──────────────────────────────────────────────────────────────┐
    │ Column Name: role_cluster_id (MISLEADING!)                   │
    │ Actually References: organization_roles.id                   │
    │ Why: Legacy naming kept for backward compatibility           │
    │                                                               │
    │ The FK was changed from role_cluster → organization_roles    │
    │ in migration 002_update_role_competency_matrix_fk.sql        │
    │ (2025-10-30) but column name was kept.                       │
    └──────────────────────────────────────────────────────────────┘

    Usage in Phase 2 Algorithm:
    - Defines required competency levels for each organization role
    - Example: "Systems Engineer" (org role) requires "Systems Thinking" level 4

    Fields:
    - role_cluster_id: FK to organization_roles.id (NOT role_cluster.id!)
    - competency_id: FK to competency.id
    - role_competency_value: Required level (0, 1, 2, 4, 6) - VALID VALUES ONLY
    - organization_id: FK to organization.id

    Updated: 2025-10-30 - FK changed from role_cluster to organization_roles
    """
    __tablename__ = 'role_competency_matrix'

    id = db.Column(db.Integer, primary_key=True)
    role_cluster_id = db.Column(db.Integer, db.ForeignKey('organization_roles.id', ondelete='CASCADE'), nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey('competency.id'), nullable=False)
    role_competency_value = db.Column(db.Integer, nullable=False, default=-100)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)

    # Relationships
    organization_role = db.relationship('OrganizationRoles', backref=db.backref('competency_matrices', cascade="all, delete-orphan", lazy=True))
    competency = db.relationship('Competency', backref=db.backref('role_competency_matrices', cascade="all, delete-orphan", lazy=True))
    organization = db.relationship('Organization', backref=db.backref('role_competency_matrices', cascade="all, delete-orphan", lazy=True))

    __table_args__ = (
        db.UniqueConstraint('organization_id', 'role_cluster_id', 'competency_id', name='role_competency_matrix_unique'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'role_cluster_id': self.role_cluster_id,
            'competency_id': self.competency_id,
            'role_competency_value': self.role_competency_value,
            'organization_id': self.organization_id
        }


class UnknownRoleProcessMatrix(db.Model):
    """
    Stores process involvement for users with unknown/custom roles
    Used for task-based role identification in Phase 1
    """
    __tablename__ = 'unknown_role_process_matrix'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(50), nullable=False)
    iso_process_id = db.Column(db.Integer, db.ForeignKey('iso_processes.id', ondelete='CASCADE'), nullable=False)
    role_process_value = db.Column(db.Integer, default=-100, nullable=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    iso_process = db.relationship('IsoProcesses', backref=db.backref('unknown_role_process_matrix', cascade="all, delete-orphan", lazy=True))
    organization = db.relationship('Organization', backref=db.backref('unknown_role_process_matrix', cascade="all, delete-orphan", lazy=True))

    __table_args__ = (
        db.UniqueConstraint('organization_id', 'iso_process_id', 'user_name', name='unknown_role_process_matrix_unique'),
        db.CheckConstraint("role_process_value IN (-100, 0, 1, 2, 4)", name="unknown_role_process_matrix_role_process_value_check"),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'iso_process_id': self.iso_process_id,
            'role_process_value': self.role_process_value,
            'organization_id': self.organization_id
        }


class UnknownRoleCompetencyMatrix(db.Model):
    """
    Stores competency requirements for users with unknown/custom roles
    Calculated from process involvement via stored procedure
    """
    __tablename__ = 'unknown_role_competency_matrix'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(50), nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey('competency.id'), nullable=False)
    role_competency_value = db.Column(db.Integer, default=-100, nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    competency = db.relationship('Competency', backref=db.backref('unknown_role_competency_matrix', cascade="all, delete-orphan", lazy=True))
    organization = db.relationship('Organization', backref=db.backref('unknown_role_competency_matrix', cascade="all, delete-orphan", lazy=True))

    __table_args__ = (
        db.UniqueConstraint('organization_id', 'user_name', 'competency_id', name='unknown_role_competency_matrix_unique'),
        db.CheckConstraint("role_competency_value IN (-100, 0, 1, 2, 4, 6)", name="unknown_role_competency_matrix_role_competency_value_check"),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'competency_id': self.competency_id,
            'role_competency_value': self.role_competency_value,
            'organization_id': self.organization_id
        }


# =============================================================================
# SECTION 2B: PHASE 2 LEARNING STRATEGY MODELS
# =============================================================================

class StrategyTemplate(db.Model):
    """
    Global Strategy Templates (Archetypes)
    ======================================

    Defines the 7 canonical qualification strategies from the template JSON.
    These are global templates that organizations instantiate via learning_strategy.

    The 7 strategies:
    1. Common basic understanding
    2. SE for managers
    3. Orientation in pilot project
    4. Needs-based, project-oriented training
    5. Continuous support
    6. Train the trainer
    7. Certification

    Each strategy has associated competency target levels defined in
    strategy_template_competency table.

    Created: 2025-11-05 (Global Strategy Templates Migration)
    """
    __tablename__ = 'strategy_template'

    id = db.Column(db.Integer, primary_key=True)
    strategy_name = db.Column(db.String(255), nullable=False, unique=True)
    strategy_description = db.Column(db.Text)
    requires_pmt_context = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template_competencies = db.relationship(
        'StrategyTemplateCompetency',
        back_populates='strategy_template',
        cascade="all, delete-orphan",
        lazy=True
    )
    learning_strategies = db.relationship(
        'LearningStrategy',
        back_populates='strategy_template',
        lazy=True
    )

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'strategy_name': self.strategy_name,
            'description': self.strategy_description,
            'requires_pmt_context': self.requires_pmt_context,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class StrategyTemplateCompetency(db.Model):
    """
    Strategy Template Competency Target Levels
    ==========================================

    Defines the target competency levels for each global strategy template.

    This is the source of truth that maps:
    - 7 strategies × 16 competencies = 112 total mappings

    Example:
    - Strategy: "SE for managers"
    - Competency: "Systems Modelling and Analysis" (ID=6)
    - Target Level: 1 (basic awareness)

    Validated: 2025-11-06 - 100% data integrity confirmed
    All 112 mappings match template JSON exactly.

    Created: 2025-11-05 (Global Strategy Templates Migration)
    """
    __tablename__ = 'strategy_template_competency'

    id = db.Column(db.Integer, primary_key=True)
    strategy_template_id = db.Column(
        db.Integer,
        db.ForeignKey('strategy_template.id', ondelete='CASCADE'),
        nullable=False
    )
    competency_id = db.Column(
        db.Integer,
        db.ForeignKey('competency.id', ondelete='CASCADE'),
        nullable=False
    )
    target_level = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    strategy_template = db.relationship(
        'StrategyTemplate',
        back_populates='template_competencies'
    )
    competency = db.relationship('Competency')

    # Table constraints
    __table_args__ = (
        db.UniqueConstraint(
            'strategy_template_id',
            'competency_id',
            name='strategy_template_competency_strategy_template_id_competenc_key'
        ),
        db.CheckConstraint(
            'target_level >= 1 AND target_level <= 6',
            name='strategy_template_competency_target_level_check'
        ),
        db.Index('idx_strategy_template_competency_template', 'strategy_template_id'),
        db.Index('idx_strategy_template_competency_competency', 'competency_id'),
    )

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'strategy_template_id': self.strategy_template_id,
            'competency_id': self.competency_id,
            'target_level': self.target_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class LearningStrategy(db.Model):
    """
    Phase 2 Learning Strategies (Specific Training Programs)
    =========================================================

    NOT REDUNDANT WITH PHASE 1 ARCHETYPES!

    Relationship between Phase 1 and Phase 2:
    ┌─────────────────────────────────────────────────────────────┐
    │ Phase 1: Archetype Selection (High-Level Approach)         │
    │   Table: Organization.selected_archetype                    │
    │   Examples: "SE_for_Managers", "Certification",             │
    │             "Common_Understanding"                           │
    │   Purpose: Determines overall qualification philosophy      │
    │                                                              │
    │                         ↓ (guides)                          │
    │                                                              │
    │ Phase 2: Learning Strategies (Specific Programs)            │
    │   Table: learning_strategy (THIS TABLE)                     │
    │   Examples: "Foundation Workshop", "CSEP Prep Course",      │
    │             "On-the-Job Mentoring"                           │
    │   Purpose: Specific training programs to close gaps         │
    └─────────────────────────────────────────────────────────────┘

    Analogy:
    - Phase 1 Archetype = "We need certification-based training" (strategy)
    - Phase 2 Learning Strategy = "INCOSE CSEP Prep Course" (tactics)

    Example Flow:
    1. Phase 1: Organization selects "Certification" archetype
    2. Phase 2: Creates 3 learning strategies:
       - "CSEP Foundation" (targets competency levels 1-2)
       - "CSEP Advanced" (targets competency levels 2-4)
       - "CSEP Expert" (targets competency levels 4-6)
    3. Algorithm: Matches users to appropriate strategies based on gaps

    Fields:
    - strategy_name: Specific training program name
    - selected: Whether organization has chosen this strategy
    - priority: Execution order (1 = first)

    Linked via strategy_competency table to define:
    "This strategy trains competency X to level Y"

    Created: 2025-11-04 (For Phase 2 Role-Based Pathway Algorithm)
    """
    __tablename__ = 'learning_strategy'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id', ondelete='CASCADE'), nullable=False)
    strategy_name = db.Column(db.String(255), nullable=False)
    strategy_description = db.Column(db.Text)
    selected = db.Column(db.Boolean, default=False)  # Whether this strategy is selected for the organization
    priority = db.Column(db.Integer)  # Priority order (1 = highest)
    strategy_template_id = db.Column(
        db.Integer,
        db.ForeignKey('strategy_template.id'),
        nullable=True  # Can be null for custom strategies
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = db.relationship('Organization', backref=db.backref('learning_strategies', cascade="all, delete-orphan", lazy=True))
    # DEPRECATED: strategy_competencies relationship removed (use strategy_template instead)
    # strategy_competencies = db.relationship('StrategyCompetency', back_populates='strategy', cascade="all, delete-orphan", lazy=True)
    strategy_template = db.relationship(
        'StrategyTemplate',
        back_populates='learning_strategies'
    )

    __table_args__ = (
        db.UniqueConstraint('organization_id', 'strategy_name', name='learning_strategy_org_name_unique'),
    )

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'name': self.strategy_name,
            'description': self.strategy_description,
            'selected': self.selected,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# =============================================================================
# DEPRECATED MODEL - DO NOT USE
# =============================================================================
# DEPRECATED: 2025-11-06 - Replaced by global template architecture
# Use StrategyTemplateCompetency instead - queries via strategy.strategy_template_id
#
# OLD Architecture (REDUNDANT):
#   - Each organization had duplicate strategy_competency rows
#   - 2 orgs × 7 strategies × 16 competencies = 224 rows of DUPLICATED data
#
# NEW Architecture (EFFICIENT):
#   - Global strategy_template + strategy_template_competency (112 shared rows)
#   - Organizations just link to templates via learning_strategy.strategy_template_id
#   - Result: 92% reduction in database size for 100 organizations!
#
# Migration completed: 2025-11-06
# Code updated to use StrategyTemplateCompetency
# Table will be dropped in migration 007_deprecate_strategy_competency.sql
# =============================================================================

# class StrategyCompetency(db.Model):
#     """
#     DEPRECATED: Use StrategyTemplateCompetency instead
#
#     OLD per-organization competency targets (REDUNDANT)
#     Replaced by global template architecture
#
#     Created: 2025-11-04
#     Deprecated: 2025-11-06
#     """
#     __tablename__ = 'strategy_competency'
#
#     id = db.Column(db.Integer, primary_key=True)
#     strategy_id = db.Column(db.Integer, db.ForeignKey('learning_strategy.id', ondelete='CASCADE'), nullable=False)
#     competency_id = db.Column(db.Integer, db.ForeignKey('competency.id', ondelete='CASCADE'), nullable=False)
#     target_level = db.Column(db.Integer, nullable=False)
#
#     strategy = db.relationship('LearningStrategy', back_populates='strategy_competencies')
#     competency = db.relationship('Competency', backref=db.backref('strategy_competencies', cascade="all, delete-orphan", lazy=True))
#
#     __table_args__ = (
#         db.UniqueConstraint('strategy_id', 'competency_id', name='strategy_competency_unique'),
#         db.CheckConstraint("target_level IN (0, 1, 2, 4, 6)", name="strategy_competency_target_level_check"),
#     )
#
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'strategy_id': self.strategy_id,
#             'competency_id': self.competency_id,
#             'target_level': self.target_level,
#             'competency_name': self.competency.competency_name if self.competency else None
#         }


class OrganizationPMTContext(db.Model):
    """
    Organization-specific PMT (Processes, Methods, Tools) Context

    Stores company-specific context for deep customization of learning objectives.
    Required only for strategies: "Needs-based project-oriented training" and "Continuous support"

    PMT Context is used to customize learning objectives with company-specific:
    - Processes: SE processes used (e.g., ISO 26262, V-model)
    - Methods: Methods employed (e.g., Agile, requirements traceability)
    - Tools: Tool landscape (e.g., DOORS, JIRA, SysML)
    - Industry: Industry context (e.g., Automotive, Medical devices)

    Phase 2 Usage: PMT-only customization (capability statements)
    Phase 3 Enhancement: Full SMART objectives (timeframe, demonstration, benefits)

    Created: 2025-11-04 (For Phase 2 Task 3 Learning Objectives Generation)
    """
    __tablename__ = 'organization_pmt_context'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id', ondelete='CASCADE'), nullable=False, unique=True)
    processes = db.Column(db.Text)
    methods = db.Column(db.Text)
    tools = db.Column(db.Text)
    industry = db.Column(db.Text)
    additional_context = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = db.relationship('Organization', backref=db.backref('pmt_context', uselist=False, cascade="all, delete-orphan"))

    def is_complete(self):
        """
        Check if PMT context has minimum required information
        At minimum, should have tools or processes
        """
        return bool(self.processes or self.tools)

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'processes': self.processes,
            'methods': self.methods,
            'tools': self.tools,
            'industry': self.industry,
            'additional_context': self.additional_context,
            'is_complete': self.is_complete(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class GeneratedLearningObjectives(db.Model):
    """
    Caches generated learning objectives to avoid expensive regeneration

    Table: generated_learning_objectives
    Purpose: Store full algorithm output with input hash for smart cache invalidation

    Performance Benefits:
    - Response time: 5-30 seconds -> 50ms (60-600x faster)
    - Cost savings: $0.01-0.05 per cached request (LLM calls avoided)
    - Token savings: 50,000+ per cached request

    Cache Invalidation Triggers:
    - New assessment completed (hash changes)
    - Strategy selection changed (hash changes)
    - PMT context updated (hash changes)
    - Admin clicks "Regenerate" (force=True parameter)

    Created: 2025-11-08 (Caching System Implementation)
    """
    __tablename__ = 'generated_learning_objectives'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, nullable=False, unique=True)

    # Pathway type
    pathway = db.Column(db.String(20), nullable=False)  # 'TASK_BASED' or 'ROLE_BASED'

    # Full JSON output from algorithm
    objectives_data = db.Column(db.JSON, nullable=False)

    # Metadata
    generated_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    generated_by_user_id = db.Column(db.Integer, nullable=True)

    # Input snapshot (for cache invalidation)
    input_hash = db.Column(db.String(64), nullable=False)

    # Quick-access validation results
    validation_status = db.Column(db.String(20), nullable=True)
    gap_percentage = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<GeneratedObjectives org={self.organization_id} pathway={self.pathway} hash={self.input_hash[:8]}...>'

    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'pathway': self.pathway,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'generated_by_user_id': self.generated_by_user_id,
            'input_hash': self.input_hash,
            'validation_status': self.validation_status,
            'gap_percentage': self.gap_percentage,
            'cached': True  # Flag to indicate this was from cache
        }


class OrganizationExistingTraining(db.Model):
    """
    Stores competencies for which organization has existing training programs.
    These competencies are excluded from LO generation/training requirements.

    Feature: "Check and Integrate Existing Offers" (Ulf's request - 11.12.2025)

    Purpose:
    - Allow users to mark competencies that already have training in their organization
    - Excluded competencies move from "Training Requirements Identified" to "No Training Required"
    - Shows "Training Exists" tag instead of generating new LOs for these
    - Affects all levels (1, 2, 4) of the selected competency

    Table: organization_existing_trainings
    """
    __tablename__ = 'organization_existing_trainings'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id', ondelete='CASCADE'),
                                nullable=False, index=True)
    competency_id = db.Column(db.Integer, db.ForeignKey('competency.id'), nullable=False)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(255))  # Username who marked this
    notes = db.Column(db.Text)  # Optional notes about existing training

    # Relationships
    organization = db.relationship('Organization', backref=db.backref(
        'existing_trainings', lazy='dynamic', cascade='all, delete-orphan'
    ))
    competency = db.relationship('Competency')

    # Unique constraint: one entry per org-competency pair
    __table_args__ = (
        db.UniqueConstraint('organization_id', 'competency_id',
                           name='unique_org_competency_training'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'competency_id': self.competency_id,
            'competency_name': self.competency.competency_name if self.competency else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'notes': self.notes
        }


# =============================================================================
# SECTION 3: USER AND AUTHENTICATION MODELS
# =============================================================================

# NOTE: AppUser model removed - consolidated into User model below
# The User model (table: 'users') is the single unified user model for SE-QPT
# It combines authentication, organization management, and role handling

class UserCompetencySurveyResult(db.Model):
    """
    Derik's survey results - EXTENDED for SE-QPT gap analysis
    Stores individual competency assessment scores with gap calculations
    """
    __tablename__ = 'user_se_competency_survey_results'

    # Derik's original fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    competency_id = db.Column(db.Integer, db.ForeignKey('competency.id'))
    score = db.Column(db.Integer, nullable=False)  # Current level (1-5)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    assessment_id = db.Column(db.Integer, db.ForeignKey('user_assessment.id', ondelete='CASCADE'))

    # SE-QPT gap analysis extensions (NEW COLUMNS - added via migration)
    target_level = db.Column(db.Integer)  # Target level from archetype matrix
    gap_size = db.Column(db.Integer)  # Calculated: target_level - score
    archetype_source = db.Column(db.String(100))  # Which archetype defined target

    # Relationships
    competency = db.relationship('Competency', backref='survey_results', foreign_keys=[competency_id])
    organization = db.relationship('Organization', backref='survey_results', foreign_keys=[organization_id])
    user = db.relationship('User', backref='survey_results', foreign_keys=[user_id])

    def calculate_gap(self, target_level):
        """Calculate and update gap size"""
        self.target_level = target_level
        self.gap_size = max(0, target_level - self.score) if target_level else 0
        return self.gap_size

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'organization_id': self.organization_id,
            'competency_id': self.competency_id,
            'competency_name': self.competency.competency_name if self.competency else None,
            'current_level': self.score,
            'target_level': self.target_level,
            'gap_size': self.gap_size,
            'archetype_source': self.archetype_source,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }


# =============================================================================
# DERIK'S COMPETENCY ASSESSMENT MODELS (for Phase 2 integration)
# =============================================================================

# REMOVED Phase 2B: AppUser model (legacy - replaced by unified User model)


# Note: UserCompetencySurveyResults uses the existing UserCompetencySurveyResult model
# Create an alias for backward compatibility with Derik's endpoints
UserCompetencySurveyResults = UserCompetencySurveyResult


class UserRoleCluster(db.Model):
    """
    User-role mapping table for assessments
    Links users to their selected organization roles (from Phase 1)

    Updated: 2025-10-30 - FK changed to reference organization_roles instead of role_cluster
    - Supports both standard-derived roles (e.g., "End User" -> org_id 286)
    - Supports custom roles (e.g., "Pepe Lolo" -> org_id 294)
    - Column 'role_cluster_id' is legacy name - now references organization_roles.id
    """
    __tablename__ = 'user_role_cluster'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    role_cluster_id = db.Column(db.Integer, db.ForeignKey('organization_roles.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('user_assessment.id', ondelete='CASCADE'))

    # Relationships
    user = db.relationship('User', backref=db.backref('role_clusters', cascade="all, delete-orphan", lazy=True), foreign_keys=[user_id])
    organization_role = db.relationship('OrganizationRoles', backref=db.backref('user_role_clusters', cascade="all, delete-orphan", lazy=True))

    def __repr__(self):
        return f"<UserRoleCluster user_id={self.user_id}, org_role_id={self.role_cluster_id}>"


# REMOVED Phase 2B: UserSurveyType model (legacy - merged into UserAssessment.survey_type)


# REMOVED Phase 2B: NewSurveyUser model (legacy - replaced by UserAssessment)


class UserCompetencySurveyFeedback(db.Model):
    """
    Stores LLM-generated feedback for competency assessment surveys
    """
    __tablename__ = 'user_competency_survey_feedback'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    feedback = db.Column(db.JSON, nullable=False)  # Store feedback as JSON array
    assessment_id = db.Column(db.Integer, db.ForeignKey('user_assessment.id', ondelete='CASCADE'))

    def __repr__(self):
        return f"<UserCompetencySurveyFeedback user_id={self.user_id} organization_id={self.organization_id}>"


# NOTE: LearningPlan model removed - not yet implemented
# Future learning plan features will be added when implemented


class UserAssessment(db.Model):
    """
    Tracks individual competency assessments for authenticated users
    Replaces the anonymous survey system (NewSurveyUser, AppUser)
    Links assessments to real User accounts for history and aggregation
    """
    __tablename__ = 'user_assessment'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)

    # Assessment type and survey mode
    assessment_type = db.Column(db.String(50), nullable=False)  # 'role_based', 'task_based', 'full_competency'
    survey_type = db.Column(db.String(50))  # 'known_roles', 'unknown_roles', 'all_roles'

    # Assessment data
    tasks_responsibilities = db.Column(db.JSON)  # Task descriptions for task-based assessments
    selected_roles = db.Column(db.JSON)  # Array of selected role IDs for role-based assessments

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', backref='assessments_history', foreign_keys=[user_id])
    organization = db.relationship('Organization', backref='user_assessments', foreign_keys=[organization_id])

    @property
    def selected_role_objects(self):
        """
        Get role objects from selected_roles JSON field
        Returns empty list if selected_roles is None or empty

        Added: 2025-11-04 for Phase 2 Algorithm compatibility
        Updated: 2025-11-06 - Handle JSON string deserialization bug
        """
        if not self.selected_roles:
            return []

        # Handle both JSON string and list (SQLAlchemy JSON deserialization issue)
        import json
        if isinstance(self.selected_roles, str):
            try:
                role_ids = json.loads(self.selected_roles)
            except (json.JSONDecodeError, TypeError):
                return []
        elif isinstance(self.selected_roles, list):
            role_ids = self.selected_roles
        else:
            return []

        if not role_ids:
            return []

        # OrganizationRoles is defined in this same file (line 154)
        # No import needed - reference directly to avoid circular dependency
        return OrganizationRoles.query.filter(
            OrganizationRoles.id.in_(role_ids)
        ).all()

    def to_dict(self):
        """Convert assessment to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'organization_id': self.organization_id,
            'assessment_type': self.assessment_type,
            'survey_type': self.survey_type,
            'tasks_responsibilities': self.tasks_responsibilities,
            'selected_roles': self.selected_roles,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': 'completed' if self.completed_at else 'in_progress'
        }

    def __repr__(self):
        return f"<UserAssessment id={self.id} user_id={self.user_id} type={self.assessment_type} status={'completed' if self.completed_at else 'in_progress'}>"


class PhaseQuestionnaireResponse(db.Model):
    """
    Store simplified questionnaire responses for SE-QPT phases
    Simpler than the full Questionnaire system - just stores JSON responses
    """
    __tablename__ = 'phase_questionnaire_responses'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)

    # Questionnaire metadata
    questionnaire_type = db.Column(db.String(50), nullable=False)  # 'maturity', 'archetype_selection'
    phase = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4

    # Response data (stored as JSON)
    responses = db.Column(db.Text, nullable=False)  # Raw responses
    computed_scores = db.Column(db.Text)  # Calculated scores/results

    # Timestamps
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='questionnaire_responses', foreign_keys=[user_id])
    organization = db.relationship('Organization', backref='questionnaire_responses', foreign_keys=[organization_id])

    def get_responses(self):
        """Get responses as Python dict"""
        if self.responses:
            return json.loads(self.responses)
        return {}

    def set_responses(self, responses_dict):
        """Set responses from Python dict"""
        self.responses = json.dumps(responses_dict, ensure_ascii=False)

    def get_computed_scores(self):
        """Get computed scores as Python dict"""
        if self.computed_scores:
            return json.loads(self.computed_scores)
        return {}

    def set_computed_scores(self, scores_dict):
        """Set computed scores from Python dict"""
        self.computed_scores = json.dumps(scores_dict, ensure_ascii=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'organization_id': self.organization_id,
            'questionnaire_type': self.questionnaire_type,
            'phase': self.phase,
            'responses': self.get_responses(),
            'computed_scores': self.get_computed_scores(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


# =============================================================================
# SECTION 2: UNIFIED USER MANAGEMENT
# Merges MVPUser + User into single comprehensive model
# =============================================================================

class User(db.Model):
    """
    Unified user model for all platform access
    Combines best features from MVPUser and original User model
    """
    __tablename__ = 'users'

    # Primary identification
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # User profile
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    # Organization relationship (supports both FK and string for flexibility)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))  # Proper FK relationship
    organization = db.Column(db.String(200))  # Fallback/legacy string field
    joined_via_code = db.Column(db.String(32))  # Organization code used to join (16-char hex codes)

    # Role and permissions (flexible system supporting both patterns)
    role = db.Column(db.String(100))  # Flexible role field (e.g., 'admin', 'employee', custom roles)
    user_type = db.Column(db.String(20), default='participant')  # participant, admin, assessor, employee

    # Status flags
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships removed: Assessment, LearningObjective, ModuleEnrollment models deleted in Phase 2A cleanup

    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        """Get user's full name or fallback to username"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def is_admin(self):
        """Check if user has admin privileges"""
        return self.role == 'admin' or self.user_type == 'admin'

    @property
    def is_employee(self):
        """Check if user is an employee"""
        return self.role == 'employee' or self.user_type == 'employee'

    @property
    def is_participant(self):
        """Check if user is a participant"""
        return self.user_type == 'participant'

    @property
    def is_assessor(self):
        """Check if user is an assessor"""
        return self.user_type == 'assessor'

    def to_dict(self):
        """Convert user to dictionary representation"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'organization_id': self.organization_id,
            'joined_via_code': self.joined_via_code,
            'role': self.role,
            'user_type': self.user_type,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


# =============================================================================
# SECTION 3: SE-QPT CORE MODELS
# =============================================================================

# =============================================================================
# SECTION 5: ASSESSMENT MODELS
# =============================================================================

# =============================================================================
# SECTION 6: RAG-LLM MODELS
# =============================================================================

# =============================================================================
# SECTION 7: QUESTIONNAIRE SYSTEM MODELS
# =============================================================================

# =============================================================================
# SECTION 8: LEARNING MODULE SYSTEM MODELS
# =============================================================================

# =============================================================================
# BACKWARD COMPATIBILITY ALIASES
# =============================================================================

# Alias for existing code that references SECompetency
SECompetency = Competency

# Alias for existing code that references SERole
SERole = RoleCluster

# Alias for existing code that references CompetencyAssessment
CompetencyAssessment = UserCompetencySurveyResult

# =============================================================================
# PHASE 2 ALGORITHM COMPATIBILITY ALIASES (added 2025-11-04)
# =============================================================================
#
# The Phase 2 algorithm was designed with cleaner naming than the actual database.
# These aliases map algorithm expectations → actual database tables.
#
# CRITICAL: These aliases determine which roles the algorithm uses!
#
# Role Mapping (IMPORTANT!):
# ┌────────────────────────────────────────────────────────────────────┐
# │ Algorithm expects: Role                                            │
# │ Actually uses: OrganizationRoles (organization-specific roles)     │
# │ Does NOT use: RoleCluster (standard reference roles)               │
# │                                                                     │
# │ Why: Phase 2 analyzes gaps for the organization's actual roles,    │
# │      not abstract standard roles.                                  │
# └────────────────────────────────────────────────────────────────────┘
#
# Field Mapping (due to legacy naming):
# ┌────────────────────────────────────────────────────────────────────┐
# │ Algorithm expects:     | Actual DB field:                          │
# ├────────────────────────┼───────────────────────────────────────────┤
# │ role_id                | role_cluster_id (confusing name!)         │
# │ required_level         | role_competency_value                     │
# │ assessment_complete    | completed_at IS NOT NULL                  │
# │ strategy.name          | strategy.strategy_name                    │
# │ user.selected_roles    | user.selected_role_objects (property)     │
# └────────────────────────────────────────────────────────────────────┘
#
Role = OrganizationRoles  # ✅ Correct: Uses org-specific roles from Phase 1
RoleCompetency = RoleCompetencyMatrix  # Maps org roles → competencies
CompetencyScore = UserCompetencySurveyResult  # User's current competency levels
PMTContext = OrganizationPMTContext  # Company-specific PMT context for deep customization


# =============================================================================
# HELPER FUNCTIONS (from unified_models.py)
# =============================================================================

def get_organization_by_code(org_code):
    """Get organization by public key (code)"""
    return Organization.query.filter_by(organization_public_key=org_code).first()


def get_user_competency_gaps(user_id, organization_id=None):
    """Get all competency gaps for a user"""
    query = UserCompetencySurveyResult.query.filter_by(user_id=user_id)
    if organization_id:
        query = query.filter_by(organization_id=organization_id)

    results = query.filter(UserCompetencySurveyResult.gap_size > 0).all()
    return [r.to_dict() for r in results]


def get_organization_completion_stats(organization_id):
    """Get Phase 1/2 completion statistics for organization"""
    org = Organization.query.get(organization_id)
    if not org:
        return None

    total_users = User.query.filter_by(organization_id=organization_id).count()

    # Count users with completed assessments
    # Must JOIN through user_assessment to get organization_id
    users_with_assessments = db.session.query(
        db.func.count(db.func.distinct(UserCompetencySurveyResult.user_id))
    ).join(
        UserAssessment,
        UserCompetencySurveyResult.assessment_id == UserAssessment.id
    ).filter(
        UserAssessment.organization_id == organization_id
    ).scalar()

    return {
        'organization_id': organization_id,
        'organization_name': org.organization_name,
        'phase1_completed': org.phase1_completed,
        'selected_archetype': org.selected_archetype,
        'total_users': total_users,
        'users_with_assessments': users_with_assessments or 0,
        'completion_rate': (users_with_assessments / total_users * 100) if total_users > 0 else 0
    }


# =============================================================================
# MVP BUSINESS LOGIC FUNCTIONS (from mvp_models.py)
# =============================================================================

def calculate_maturity_score(responses):
    """
    Calculate maturity score from 33-question assessment
    Based on MVP architecture specification
    """
    # Scope questions (1-15)
    scope_questions = responses[:15]
    # Process questions (16-33)
    process_questions = responses[15:33]

    # Calculate averages
    scope_score = sum(q.get('score', 0) for q in scope_questions) / len(scope_questions)
    process_score = sum(q.get('score', 0) for q in process_questions) / len(process_questions)

    # Calculate overall maturity (geometric mean)
    overall_maturity_score = math.sqrt((scope_score ** 2 + process_score ** 2) / 2)

    # Determine maturity level
    if overall_maturity_score <= 1.5:
        level = 'Initial'
    elif overall_maturity_score <= 2.5:
        level = 'Developing'
    elif overall_maturity_score <= 3.5:
        level = 'Defined'
    elif overall_maturity_score <= 4.0:
        level = 'Managed'
    else:
        level = 'Optimized'

    return {
        'scope_score': round(scope_score, 2),
        'process_score': round(process_score, 2),
        'overall_score': round(overall_maturity_score, 2),
        'overall_maturity': level
    }


def select_archetype(maturity_result, preferences=None):
    """
    Select qualification archetype based on maturity and preferences
    Based on MVP architecture specification
    """
    scope_score = maturity_result['scope_score']
    process_score = maturity_result['process_score']

    if process_score <= 1.5:
        # Low maturity - dual selection needed
        primary = 'SE_for_Managers'

        # Determine secondary based on preferences
        if preferences and preferences.get('goal'):
            goal = preferences['goal']
            if goal == 'apply_se':
                secondary = 'Orientation_Pilot_Project'
            elif goal == 'basic_understanding':
                secondary = 'Common_Understanding'
            elif goal == 'expert_training':
                secondary = 'Certification'
            else:
                secondary = 'Common_Understanding'
        else:
            secondary = 'Common_Understanding'

        return {
            'primary': primary,
            'secondary': secondary,
            'customization_level': 'low',
            'dual_selection': True
        }
    else:
        # Higher maturity - single selection
        if scope_score >= 3.0:
            archetype = 'Continuous_Support'
        else:
            archetype = 'Needs_Based_Training'

        return {
            'primary': archetype,
            'secondary': None,
            'customization_level': 'high',
            'dual_selection': False
        }


def generate_learning_plan_templates():
    """
    Template-based learning objectives for different archetypes
    Based on MVP architecture specification
    """
    return {
        'SE_for_Managers': [
            'Understand Systems Engineering fundamentals',
            'Learn SE process integration',
            'Develop SE leadership skills',
            'Master SE project management',
            'Build SE team coordination capabilities'
        ],
        'Common_Understanding': [
            'Gain SE awareness across organization',
            'Understand SE terminology and concepts',
            'Learn basic SE tools and methods',
            'Develop SE communication skills',
            'Understand SE lifecycle processes'
        ],
        'Orientation_Pilot_Project': [
            'Complete hands-on SE project',
            'Apply SE methods in practice',
            'Develop practical SE skills',
            'Build SE experience portfolio',
            'Demonstrate SE competency'
        ],
        'Certification': [
            'Prepare for SE certification',
            'Master advanced SE concepts',
            'Complete SE knowledge assessment',
            'Develop expert-level SE skills',
            'Achieve professional SE recognition'
        ],
        'Continuous_Support': [
            'Maintain SE competency levels',
            'Stay current with SE innovations',
            'Develop advanced SE specializations',
            'Mentor other SE professionals',
            'Lead SE improvement initiatives'
        ],
        'Needs_Based_Training': [
            'Address specific SE skill gaps',
            'Complete targeted SE training',
            'Develop project-specific SE capabilities',
            'Apply SE methods to current work',
            'Build contextual SE expertise'
        ]
    }


def generate_basic_modules(archetype):
    """
    Basic module recommendations based on archetype
    Based on MVP architecture specification
    """
    module_templates = {
        'SE_for_Managers': [
            'SE Management Fundamentals',
            'SE Leadership and Teams',
            'SE Process Integration',
            'SE Project Planning'
        ],
        'Common_Understanding': [
            'Introduction to Systems Engineering',
            'SE Terminology and Concepts',
            'Basic SE Tools',
            'SE Communication'
        ],
        'Orientation_Pilot_Project': [
            'SE Project Methods',
            'Hands-on SE Practice',
            'SE Tool Application',
            'Project Portfolio Development'
        ],
        'Certification': [
            'Advanced SE Concepts',
            'SE Certification Prep',
            'Expert SE Methods',
            'Professional SE Standards'
        ]
    }

    return module_templates.get(archetype, [])


def calculate_duration(objectives_count):
    """
    Estimate learning plan duration based on objective count
    """
    # Simple estimation: 2-3 weeks per objective
    base_weeks = objectives_count * 2.5
    return max(4, min(52, int(base_weeks)))  # Minimum 4 weeks, maximum 52 weeks


# Compatibility wrapper for role mapping (from mvp_models.py)
class RoleMapping:
    """
    Compatibility wrapper for role mapping functionality
    In unified system, this is handled by:
    - Derik's user_role_cluster table (not yet used)
    - PhaseQuestionnaireResponse for SE-QPT archetype selection

    This is a minimal placeholder to maintain API compatibility
    """
    @staticmethod
    def query_by_user(user_id):
        """Query role mapping for a user - returns None for now"""
        # TODO: Implement using PhaseQuestionnaireResponse or user_role_cluster
        return None

    @staticmethod
    def create(user_id, role_id, archetype):
        """Create role mapping - stores in PhaseQuestionnaireResponse"""
        # TODO: Implement using PhaseQuestionnaireResponse
        pass
