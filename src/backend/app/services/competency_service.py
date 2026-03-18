"""
Simplified Competency Assessment Service for SE-QPT Integration
Provides competency assessment functionality without requiring full Derik LLM setup
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import json

from models import (
    db, User, SECompetency, SERole
)

competency_service_bp = Blueprint('competency_service', __name__)

# 16 SE Competencies based on INCOSE framework
SE_COMPETENCIES = [
    {
        "id": 1,
        "name": "Systems Thinking",
        "code": "ST",
        "category": "Core",
        "description": "Ability to view systems holistically, understanding interactions and interdependencies.",
        "indicators": [
            "Identifies system boundaries and environment",
            "Understands system hierarchy and emergent properties",
            "Recognizes system feedback loops and behavior patterns",
            "Applies systems thinking to problem solving"
        ]
    },
    {
        "id": 2,
        "name": "Requirements Engineering",
        "code": "RE",
        "category": "Technical",
        "description": "Skills in eliciting, analyzing, specifying and managing requirements.",
        "indicators": [
            "Elicits stakeholder requirements effectively",
            "Translates needs into technical specifications",
            "Manages requirements traceability and changes",
            "Validates requirements against stakeholder needs"
        ]
    },
    {
        "id": 3,
        "name": "System Architecture",
        "code": "SA",
        "category": "Technical",
        "description": "Designing system architectures that meet functional and non-functional requirements.",
        "indicators": [
            "Develops logical and physical architectures",
            "Balances architectural trade-offs and constraints",
            "Applies architectural patterns and principles",
            "Evaluates architectural alternatives"
        ]
    },
    {
        "id": 4,
        "name": "System Integration",
        "code": "SI",
        "category": "Technical",
        "description": "Integrating system components and interfaces to create coherent systems.",
        "indicators": [
            "Plans and executes integration strategies",
            "Manages interface definitions and compatibility",
            "Resolves integration issues and conflicts",
            "Validates integrated system performance"
        ]
    },
    {
        "id": 5,
        "name": "Verification & Validation",
        "code": "VV",
        "category": "Technical",
        "description": "Ensuring systems meet requirements and stakeholder needs through testing and validation.",
        "indicators": [
            "Develops V&V plans and procedures",
            "Conducts system and acceptance testing",
            "Validates system against user needs",
            "Manages V&V processes and results"
        ]
    },
    {
        "id": 6,
        "name": "Life Cycle Management",
        "code": "LCM",
        "category": "Management",
        "description": "Managing systems throughout their entire lifecycle from concept to disposal.",
        "indicators": [
            "Applies lifecycle models and processes",
            "Manages phase transitions and gates",
            "Coordinates lifecycle stakeholders",
            "Plans for system evolution and retirement"
        ]
    },
    {
        "id": 7,
        "name": "Project Management",
        "code": "PM",
        "category": "Management",
        "description": "Managing systems engineering projects including planning, execution, and control.",
        "indicators": [
            "Develops SE project plans and schedules",
            "Manages SE resources and budgets",
            "Monitors and controls SE activities",
            "Communicates project status and issues"
        ]
    },
    {
        "id": 8,
        "name": "Risk Management",
        "code": "RM",
        "category": "Management",
        "description": "Identifying, analyzing, and mitigating risks in systems engineering projects.",
        "indicators": [
            "Identifies technical and programmatic risks",
            "Analyzes risk probability and impact",
            "Develops risk mitigation strategies",
            "Monitors and controls risk exposure"
        ]
    },
    {
        "id": 9,
        "name": "Configuration Management",
        "code": "CM",
        "category": "Management",
        "description": "Managing system configurations, baselines, and changes throughout the lifecycle.",
        "indicators": [
            "Establishes configuration baselines",
            "Controls configuration changes",
            "Maintains configuration records",
            "Audits configuration compliance"
        ]
    },
    {
        "id": 10,
        "name": "Quality Management",
        "code": "QM",
        "category": "Management",
        "description": "Ensuring quality in systems engineering processes and products.",
        "indicators": [
            "Develops quality management plans",
            "Implements quality assurance processes",
            "Conducts quality reviews and audits",
            "Drives continuous improvement"
        ]
    },
    {
        "id": 11,
        "name": "Communication & Leadership",
        "code": "CL",
        "category": "Professional",
        "description": "Leading teams and communicating effectively with stakeholders.",
        "indicators": [
            "Leads cross-functional SE teams",
            "Communicates technical concepts clearly",
            "Facilitates stakeholder collaboration",
            "Influences and negotiates effectively"
        ]
    },
    {
        "id": 12,
        "name": "Decision Analysis",
        "code": "DA",
        "category": "Professional",
        "description": "Making informed technical and programmatic decisions using systematic approaches.",
        "indicators": [
            "Applies decision analysis methods",
            "Evaluates alternatives objectively",
            "Considers stakeholder perspectives",
            "Documents decision rationale"
        ]
    },
    {
        "id": 13,
        "name": "Stakeholder Management",
        "code": "SM",
        "category": "Professional",
        "description": "Managing relationships and expectations with diverse system stakeholders.",
        "indicators": [
            "Identifies key stakeholders and needs",
            "Engages stakeholders throughout lifecycle",
            "Manages conflicting stakeholder interests",
            "Maintains stakeholder satisfaction"
        ]
    },
    {
        "id": 14,
        "name": "Technical Leadership",
        "code": "TL",
        "category": "Professional",
        "description": "Providing technical direction and guidance for systems engineering efforts.",
        "indicators": [
            "Sets technical vision and direction",
            "Mentors junior systems engineers",
            "Resolves technical disputes",
            "Champions SE best practices"
        ]
    },
    {
        "id": 15,
        "name": "Innovation & Creativity",
        "code": "IC",
        "category": "Professional",
        "description": "Applying creative thinking and innovation to systems engineering challenges.",
        "indicators": [
            "Identifies innovative solution approaches",
            "Challenges conventional thinking",
            "Promotes creative problem solving",
            "Adapts to emerging technologies"
        ]
    },
    {
        "id": 16,
        "name": "Continuous Learning",
        "code": "CLE",
        "category": "Professional",
        "description": "Continuously developing systems engineering knowledge and skills.",
        "indicators": [
            "Stays current with SE practices",
            "Seeks feedback and learning opportunities",
            "Applies lessons learned effectively",
            "Shares knowledge with others"
        ]
    }
]

# 14 SE Role Clusters
SE_ROLES = [
    {
        "id": 1,
        "name": "Systems Engineer",
        "description": "Core systems engineering role focusing on technical systems development",
        "career_level": "Senior",
        "primary_focus": "Technical system design and integration",
        "typical_experience_years": 8,
        "typical_responsibilities": [
            "Lead technical system architecture design",
            "Coordinate system integration activities",
            "Interface with stakeholders on technical requirements",
            "Manage technical risk and trade-offs"
        ]
    },
    {
        "id": 2,
        "name": "Requirements Engineer",
        "description": "Specializes in requirements engineering and management processes",
        "career_level": "Mid-Level",
        "primary_focus": "Requirements analysis and management",
        "typical_experience_years": 5,
        "typical_responsibilities": [
            "Elicit and analyze stakeholder requirements",
            "Maintain requirements traceability",
            "Manage requirements changes and baselines",
            "Facilitate requirements validation"
        ]
    },
    {
        "id": 3,
        "name": "System Architect",
        "description": "Focuses on system architecture design and technical leadership",
        "career_level": "Senior",
        "primary_focus": "System architecture and design",
        "typical_experience_years": 10,
        "typical_responsibilities": [
            "Design system architecture and interfaces",
            "Evaluate architectural alternatives",
            "Lead architecture reviews and decisions",
            "Mentor other engineers on architecture"
        ]
    },
    {
        "id": 4,
        "name": "Integration Engineer",
        "description": "Specializes in system integration, testing and validation",
        "career_level": "Mid-Level",
        "primary_focus": "System integration and testing",
        "typical_experience_years": 6,
        "typical_responsibilities": [
            "Plan and execute integration activities",
            "Develop integration test procedures",
            "Resolve integration issues",
            "Coordinate with development teams"
        ]
    },
    {
        "id": 5,
        "name": "Test Engineer",
        "description": "Focuses on verification and validation activities",
        "career_level": "Mid-Level",
        "primary_focus": "System testing and validation",
        "typical_experience_years": 5,
        "typical_responsibilities": [
            "Develop test plans and procedures",
            "Execute system and acceptance tests",
            "Analyze test results and issues",
            "Support V&V process improvement"
        ]
    },
    {
        "id": 6,
        "name": "SE Project Manager",
        "description": "Manages systems engineering projects and processes",
        "career_level": "Senior",
        "primary_focus": "SE project management",
        "typical_experience_years": 12,
        "typical_responsibilities": [
            "Manage SE project planning and execution",
            "Coordinate SE resources and activities",
            "Monitor SE project performance",
            "Interface with program management"
        ]
    },
    {
        "id": 7,
        "name": "Product Manager",
        "description": "Manages product development from systems perspective",
        "career_level": "Senior",
        "primary_focus": "Product strategy and development",
        "typical_experience_years": 8,
        "typical_responsibilities": [
            "Define product requirements and roadmap",
            "Coordinate cross-functional development",
            "Manage product lifecycle",
            "Interface with customers and markets"
        ]
    },
    {
        "id": 8,
        "name": "SE Team Lead",
        "description": "Leads systems engineering teams and technical activities",
        "career_level": "Senior",
        "primary_focus": "Technical team leadership",
        "typical_experience_years": 10,
        "typical_responsibilities": [
            "Lead SE team technical activities",
            "Mentor junior systems engineers",
            "Coordinate with other engineering disciplines",
            "Represent team in technical discussions"
        ]
    },
    {
        "id": 9,
        "name": "Junior Systems Engineer",
        "description": "Entry-level systems engineering role with basic responsibilities",
        "career_level": "Junior",
        "primary_focus": "Learning SE fundamentals",
        "typical_experience_years": 2,
        "typical_responsibilities": [
            "Support senior engineers in SE activities",
            "Learn SE processes and tools",
            "Perform assigned technical tasks",
            "Participate in SE training programs"
        ]
    },
    {
        "id": 10,
        "name": "SE Consultant",
        "description": "External consultant providing specialized SE expertise",
        "career_level": "Expert",
        "primary_focus": "SE consulting and advisory",
        "typical_experience_years": 15,
        "typical_responsibilities": [
            "Assess SE process maturity",
            "Recommend SE improvements",
            "Mentor client SE teams",
            "Transfer SE best practices"
        ]
    },
    {
        "id": 11,
        "name": "SE Process Engineer",
        "description": "Focuses on SE process definition and improvement",
        "career_level": "Mid-Level",
        "primary_focus": "SE process development",
        "typical_experience_years": 7,
        "typical_responsibilities": [
            "Define SE processes and procedures",
            "Support SE process implementation",
            "Conduct SE process assessments",
            "Drive SE process improvements"
        ]
    },
    {
        "id": 12,
        "name": "SE Analyst",
        "description": "Performs systems analysis and modeling activities",
        "career_level": "Mid-Level",
        "primary_focus": "System analysis and modeling",
        "typical_experience_years": 4,
        "typical_responsibilities": [
            "Perform system trade studies",
            "Develop system models and simulations",
            "Analyze system performance",
            "Support decision analysis"
        ]
    },
    {
        "id": 13,
        "name": "SE Quality Engineer",
        "description": "Focuses on SE quality assurance and improvement",
        "career_level": "Mid-Level",
        "primary_focus": "SE quality management",
        "typical_experience_years": 6,
        "typical_responsibilities": [
            "Develop SE quality processes",
            "Conduct SE quality reviews",
            "Monitor SE quality metrics",
            "Support SE process audits"
        ]
    },
    {
        "id": 14,
        "name": "SE Manager",
        "description": "Manages SE organization and strategic initiatives",
        "career_level": "Expert",
        "primary_focus": "SE organizational leadership",
        "typical_experience_years": 18,
        "typical_responsibilities": [
            "Lead SE organizational strategy",
            "Manage SE department operations",
            "Develop SE capabilities and talent",
            "Interface with executive leadership"
        ]
    }
]

@competency_service_bp.route('/competencies', methods=['GET'])
@jwt_required()
def get_competencies():
    """Get all 16 SE competencies"""
    return jsonify({
        'competencies': SE_COMPETENCIES,
        'total': len(SE_COMPETENCIES)
    })

@competency_service_bp.route('/public/roles', methods=['GET'])
def get_roles_public():
    """Get all 14 SE roles - public endpoint"""
    return jsonify({
        'roles': SE_ROLES,
        'total': len(SE_ROLES)
    })

@competency_service_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    """Get all 14 SE roles"""
    return jsonify({
        'roles': SE_ROLES,
        'total': len(SE_ROLES)
    })

@competency_service_bp.route('/roles/<int:role_id>/competencies', methods=['GET'])
@jwt_required()
def get_role_competency_requirements(role_id):
    """Get competency requirements for a specific role"""
    # Simplified competency matrix - in reality this would come from database
    # This is a basic mapping of importance levels (1-5) for each competency per role
    role_competency_matrix = {
        1: {1: 5, 2: 4, 3: 5, 4: 4, 5: 3, 6: 4, 7: 3, 8: 4, 9: 3, 10: 3, 11: 4, 12: 4, 13: 4, 14: 5, 15: 3, 16: 4},  # Systems Engineer
        2: {1: 3, 2: 5, 3: 3, 4: 2, 5: 3, 6: 3, 7: 2, 8: 3, 9: 4, 10: 4, 11: 4, 12: 3, 13: 5, 14: 3, 15: 2, 16: 3},  # Requirements Engineer
        3: {1: 5, 2: 4, 3: 5, 4: 4, 5: 3, 6: 4, 7: 3, 8: 4, 9: 3, 10: 4, 11: 5, 12: 5, 13: 3, 14: 5, 15: 4, 16: 4},  # System Architect
        4: {1: 4, 2: 3, 3: 4, 4: 5, 5: 5, 6: 3, 7: 3, 8: 4, 9: 4, 10: 4, 11: 4, 12: 3, 13: 3, 14: 4, 15: 3, 16: 3},  # Integration Engineer
        5: {1: 3, 2: 4, 3: 3, 4: 4, 5: 5, 6: 3, 7: 2, 8: 3, 9: 3, 10: 5, 11: 3, 12: 4, 13: 3, 14: 3, 15: 2, 16: 3},  # Test Engineer
        6: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 5, 7: 5, 8: 5, 9: 4, 10: 4, 11: 5, 12: 4, 13: 4, 14: 4, 15: 3, 16: 4},  # SE Project Manager
        7: {1: 4, 2: 4, 3: 3, 4: 3, 5: 3, 6: 5, 7: 4, 8: 4, 9: 3, 10: 4, 11: 5, 12: 4, 13: 5, 14: 4, 15: 4, 16: 3},  # Product Manager
        8: {1: 5, 2: 4, 3: 4, 4: 4, 5: 3, 6: 4, 7: 4, 8: 4, 9: 3, 10: 4, 11: 5, 12: 4, 13: 4, 14: 5, 15: 4, 16: 5},  # SE Team Lead
        9: {1: 3, 2: 3, 3: 2, 4: 3, 5: 3, 6: 2, 7: 2, 8: 2, 9: 2, 10: 2, 11: 3, 12: 2, 13: 2, 14: 2, 15: 2, 16: 4},  # Junior Systems Engineer
        10: {1: 5, 2: 4, 3: 4, 4: 4, 5: 4, 6: 5, 7: 4, 8: 5, 9: 4, 10: 5, 11: 5, 12: 5, 13: 4, 14: 5, 15: 5, 16: 5},  # SE Consultant
        11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 5, 7: 3, 8: 3, 9: 4, 10: 5, 11: 4, 12: 3, 13: 3, 14: 4, 15: 3, 16: 4},  # SE Process Engineer
        12: {1: 5, 2: 4, 3: 4, 4: 3, 5: 3, 6: 3, 7: 2, 8: 4, 9: 3, 10: 3, 11: 3, 12: 5, 13: 3, 14: 3, 15: 4, 16: 3},  # SE Analyst
        13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 4, 6: 4, 7: 3, 8: 3, 9: 4, 10: 5, 11: 4, 12: 3, 13: 3, 14: 4, 15: 3, 16: 4},  # SE Quality Engineer
        14: {1: 5, 2: 4, 3: 4, 4: 3, 5: 3, 6: 5, 7: 5, 8: 5, 9: 4, 10: 4, 11: 5, 12: 4, 13: 4, 14: 5, 15: 4, 16: 5}   # SE Manager
    }

    role = next((r for r in SE_ROLES if r['id'] == role_id), None)
    if not role:
        return jsonify({'error': 'Role not found'}), 404

    requirements = role_competency_matrix.get(role_id, {})

    competency_requirements = []
    for comp in SE_COMPETENCIES:
        importance = requirements.get(comp['id'], 3)  # Default to 3 if not specified
        competency_requirements.append({
            'competency_id': comp['id'],
            'competency_name': comp['name'],
            'competency_code': comp['code'],
            'category': comp['category'],
            'importance_level': importance,
            'indicators': comp['indicators']
        })

    return jsonify({
        'role': role,
        'competency_requirements': competency_requirements
    })

# REMOVED Phase 3 - These routes use the removed Assessment model
# Use main_bp routes in routes.py instead (/assessment/start, /assessment/submit, /assessment/results)

# @competency_service_bp.route('/assessment/<int:assessment_id>/competency-questionnaire', methods=['GET'])
# @jwt_required()
# def get_competency_questionnaire(assessment_id):
#     """Generate competency questionnaire based on selected role"""
#     try:
#         user_id = int(get_jwt_identity())
#
#         # Get assessment
#         assessment = Assessment.query.filter_by(id=assessment_id, user_id=user_id).first()
#         if not assessment:
#             return jsonify({'error': 'Assessment not found'}), 404
#
#         # For now, assume role selection is stored in assessment results
#         selected_role_id = assessment.results.get('selected_role_id', 1) if assessment.results else 1
#
#         # Get competency requirements for the role
#         role = next((r for r in SE_ROLES if r['id'] == selected_role_id), SE_ROLES[0])
#
#         # Generate questionnaire for high importance competencies (4-5)
#         role_competency_matrix = {
#             1: {1: 5, 2: 4, 3: 5, 4: 4, 5: 3, 6: 4, 7: 3, 8: 4, 9: 3, 10: 3, 11: 4, 12: 4, 13: 4, 14: 5, 15: 3, 16: 4},
#             # ... (same matrix as above, simplified for brevity)
#         }
#
#         requirements = role_competency_matrix.get(selected_role_id, {})
#         high_importance_competencies = [
#             comp for comp in SE_COMPETENCIES
#             if requirements.get(comp['id'], 3) >= 4
#         ]
#
#         questionnaire = {
#             'assessment_id': assessment_id,
#             'role': role,
#             'competencies': high_importance_competencies,
#             'instructions': 'Rate your current competency level for each indicator on a scale of 1-5',
#             'scale': {
#                 '1': 'Beginner - Limited knowledge or experience',
#                 '2': 'Basic - Some knowledge, can perform with guidance',
#                 '3': 'Intermediate - Good knowledge, can perform independently',
#                 '4': 'Advanced - Strong knowledge, can guide others',
#                 '5': 'Expert - Extensive knowledge, recognized authority'
#             }
#         }
#
#         return jsonify(questionnaire)
#
#     except Exception as e:
#         current_app.logger.error(f"Questionnaire generation error: {str(e)}")
#         return jsonify({'error': 'Failed to generate questionnaire'}), 500
#
# @competency_service_bp.route('/assessment/<int:assessment_id>/submit-responses', methods=['POST'])
# @jwt_required()
# def submit_competency_responses(assessment_id):
#     """Submit competency assessment responses"""
#     try:
#         user_id = int(get_jwt_identity())
#         data = request.get_json()
#         responses = data.get('responses', {})
#
#         # Get assessment
#         assessment = Assessment.query.filter_by(id=assessment_id, user_id=user_id).first()
#         if not assessment:
#             return jsonify({'error': 'Assessment not found'}), 404
#
#         # Calculate competency scores
#         competency_scores = {}
#         total_score = 0
#         count = 0
#
#         for competency_code, indicators in responses.items():
#             # Find competency
#             competency = next((c for c in SE_COMPETENCIES if c['code'] == competency_code), None)
#             if competency:
#                 # Calculate average score for this competency
#                 indicator_scores = list(indicators.values())
#                 competency_avg = sum(indicator_scores) / len(indicator_scores) if indicator_scores else 0
#                 competency_scores[competency['name']] = competency_avg
#                 total_score += competency_avg
#                 count += 1
#
#         overall_avg = total_score / count if count > 0 else 0
#
#         # Update assessment
#         assessment.status = 'completed'
#         assessment.score = overall_avg
#         assessment.competency_scores = competency_scores
#         assessment.completion_time_minutes = data.get('completion_time', 0)
#         assessment.completed_at = datetime.utcnow()
#         assessment.results = {
#             'competency_responses': responses,
#             'competency_scores': competency_scores,
#             'overall_score': overall_avg,
#             'competencies_assessed': count
#         }
#
#         db.session.commit()
#
#         return jsonify({
#             'message': 'Assessment completed successfully',
#             'results': {
#                 'overall_score': overall_avg,
#                 'competency_scores': competency_scores,
#                 'competencies_assessed': count
#             }
#         })
#
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Response submission error: {str(e)}")
#         return jsonify({'error': 'Failed to submit responses'}), 500