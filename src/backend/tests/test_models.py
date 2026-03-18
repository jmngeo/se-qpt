"""
Backend Model Tests for SE-QPT System
Tests all database models, relationships, and data integrity
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'backend'))

from models import db, User, SECompetency, SERole, QualificationArchetype, Assessment, CompetencyAssessmentResult
from models import LearningObjective, QualificationPlan, CompanyContext, RAGTemplate
from app import create_app

class TestSEQPTModels:
    """Test suite for SE-QPT database models"""

    @pytest.fixture(scope="class")
    def app(self):
        """Create test Flask application"""
        app = create_app('testing')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True

        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()

    @pytest.fixture(scope="function")
    def db_session(self, app):
        """Create database session for each test"""
        with app.app_context():
            db.session.begin()
            yield db.session
            db.session.rollback()

    def test_user_model_creation(self, db_session):
        """Test User model creation and validation"""
        user = User(
            username='test_user',
            email='test@example.com',
            password_hash='hashed_password',
            first_name='Test',
            last_name='User',
            role='user'
        )

        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.username == 'test_user'
        assert user.email == 'test@example.com'
        assert user.full_name == 'Test User'
        assert user.is_active == True
        assert user.created_at is not None

    def test_user_password_methods(self, db_session):
        """Test User password hashing and verification"""
        user = User(username='test_user', email='test@example.com')
        user.set_password('test_password')

        assert user.password_hash is not None
        assert user.password_hash != 'test_password'
        assert user.check_password('test_password') == True
        assert user.check_password('wrong_password') == False

    def test_se_competency_model(self, db_session):
        """Test SECompetency model creation"""
        competency = SECompetency(
            name='Systems Thinking',
            code='ST',
            description='Ability to understand complex systems',
            category='Technical',
            incose_reference='INCOSE-ST-001'
        )

        db_session.add(competency)
        db_session.commit()

        assert competency.id is not None
        assert competency.name == 'Systems Thinking'
        assert competency.code == 'ST'
        assert competency.is_active == True

    def test_se_role_model(self, db_session):
        """Test SERole model creation"""
        role = SERole(
            name='System Engineer',
            description='Core systems engineering role',
            level='Senior',
            typical_experience_years=5
        )

        db_session.add(role)
        db_session.commit()

        assert role.id is not None
        assert role.name == 'System Engineer'
        assert role.typical_experience_years == 5

    def test_qualification_archetype_model(self, db_session):
        """Test QualificationArchetype model creation"""
        archetype = QualificationArchetype(
            name='Project-Oriented Training',
            description='Focus on project-based learning',
            strategy='hands_on',
            target_audience='junior_engineers',
            duration_weeks=12,
            delivery_format='hybrid'
        )

        db_session.add(archetype)
        db_session.commit()

        assert archetype.id is not None
        assert archetype.name == 'Project-Oriented Training'
        assert archetype.duration_weeks == 12

    def test_assessment_model_with_relationships(self, db_session):
        """Test Assessment model with user and archetype relationships"""
        # Create user
        user = User(username='test_user', email='test@example.com')
        db_session.add(user)
        db_session.flush()

        # Create archetype
        archetype = QualificationArchetype(
            name='Test Archetype',
            description='Test archetype',
            strategy='test'
        )
        db_session.add(archetype)
        db_session.flush()

        # Create assessment
        assessment = Assessment(
            user_id=user.id,
            phase=1,
            assessment_type='maturity',
            title='Phase 1 Maturity Assessment',
            description='Initial maturity assessment',
            status='completed',
            score=85.5,
            max_score=100.0,
            completion_time_minutes=45,
            selected_archetype_id=archetype.id
        )

        db_session.add(assessment)
        db_session.commit()

        assert assessment.id is not None
        assert assessment.user_id == user.id
        assert assessment.phase == 1
        assert assessment.score == 85.5
        assert assessment.selected_archetype_id == archetype.id

        # Test relationships
        assert assessment.user == user
        assert assessment.selected_archetype == archetype

    def test_competency_assessment_result_model(self, db_session):
        """Test CompetencyAssessmentResult model"""
        # Create dependencies
        user = User(username='test_user', email='test@example.com')
        competency = SECompetency(name='Test Competency', code='TC')
        assessment = Assessment(
            user_id=user.id,
            phase=2,
            assessment_type='competency',
            title='Competency Assessment'
        )

        db_session.add_all([user, competency, assessment])
        db_session.flush()

        # Create competency result
        result = CompetencyAssessmentResult(
            assessment_id=assessment.id,
            competency_id=competency.id,
            current_level=2,
            target_level=4,
            score=75.0,
            confidence_score=0.85,
            gap_analysis={'areas': ['requirements', 'modeling']},
            recommendations=['Complete advanced training', 'Practice with real projects']
        )

        db_session.add(result)
        db_session.commit()

        assert result.id is not None
        assert result.current_level == 2
        assert result.target_level == 4
        assert result.gap_size == 2
        assert result.confidence_score == 0.85
        assert isinstance(result.gap_analysis, dict)
        assert isinstance(result.recommendations, list)

    def test_learning_objective_model(self, db_session):
        """Test LearningObjective model with RAG integration"""
        user = User(username='test_user', email='test@example.com')
        competency = SECompetency(name='Test Competency', code='TC')

        db_session.add_all([user, competency])
        db_session.flush()

        objective = LearningObjective(
            user_id=user.id,
            competency_id=competency.id,
            text='Demonstrate proficiency in requirements analysis within 3 months',
            type='rag_generated',
            priority='high',
            smart_score=88.5,
            smart_analysis={
                'specific': {'score': 90, 'feedback': 'Clear and specific'},
                'measurable': {'score': 85, 'feedback': 'Measurable criteria present'},
                'achievable': {'score': 90, 'feedback': 'Realistic timeline'},
                'relevant': {'score': 95, 'feedback': 'Highly relevant to role'},
                'timebound': {'score': 85, 'feedback': 'Clear 3-month timeline'}
            },
            context_relevance=0.92,
            validation_status='validated',
            rag_sources=['ISO15288', 'INCOSE_Handbook'],
            generation_metadata={
                'model': 'gpt-4',
                'temperature': 0.7,
                'company_context': 'automotive',
                'prompt_version': '2.1'
            }
        )

        db_session.add(objective)
        db_session.commit()

        assert objective.id is not None
        assert objective.smart_score == 88.5
        assert objective.type == 'rag_generated'
        assert objective.validation_status == 'validated'
        assert isinstance(objective.smart_analysis, dict)
        assert len(objective.rag_sources) == 2

    def test_qualification_plan_model(self, db_session):
        """Test QualificationPlan model with relationships"""
        user = User(username='test_user', email='test@example.com')
        archetype = QualificationArchetype(name='Test Archetype', strategy='test')

        db_session.add_all([user, archetype])
        db_session.flush()

        plan = QualificationPlan(
            user_id=user.id,
            name='My SE Qualification Plan',
            description='Comprehensive qualification plan',
            target_role='System Engineer',
            archetype_id=archetype.id,
            status='active',
            estimated_duration_weeks=16,
            modules=['Requirements Engineering', 'System Architecture', 'V&V'],
            learning_path={
                'phase1': 'completed',
                'phase2': 'in_progress',
                'phase3': 'pending',
                'phase4': 'pending'
            },
            progress_tracking={
                'overall_progress': 35,
                'completed_modules': 1,
                'current_phase': 2
            }
        )

        db_session.add(plan)
        db_session.commit()

        assert plan.id is not None
        assert plan.name == 'My SE Qualification Plan'
        assert plan.estimated_duration_weeks == 16
        assert isinstance(plan.modules, list)
        assert len(plan.modules) == 3
        assert plan.learning_path['phase1'] == 'completed'
        assert plan.progress_tracking['overall_progress'] == 35

    def test_company_context_model(self, db_session):
        """Test CompanyContext model for RAG integration"""
        context = CompanyContext(
            name='AutoTech Motors GmbH',
            industry='Automotive',
            size='large',
            domain='Electric Vehicles',
            processes=['ISO26262', 'ASPICE', 'Agile'],
            methods=['FMEA', 'HAZOP', 'Monte Carlo'],
            tools=['DOORS', 'Enterprise Architect', 'MATLAB'],
            standards=['ISO26262', 'ISO21434', 'UN-R155'],
            project_types=['Vehicle Development', 'ADAS', 'Autonomous Driving'],
            organizational_structure={
                'departments': ['R&D', 'Quality', 'Production'],
                'hierarchy_levels': 4,
                'team_sizes': {'average': 8, 'range': [3, 15]}
            },
            quality_score=0.87,
            extraction_metadata={
                'last_updated': datetime.utcnow().isoformat(),
                'source': 'manual_input',
                'validated': True
            }
        )

        db_session.add(context)
        db_session.commit()

        assert context.id is not None
        assert context.name == 'AutoTech Motors GmbH'
        assert len(context.processes) == 3
        assert len(context.methods) == 3
        assert len(context.tools) == 3
        assert context.quality_score == 0.87
        assert context.extraction_metadata['validated'] == True

    def test_rag_template_model(self, db_session):
        """Test RAGTemplate model for AI objective generation"""
        template = RAGTemplate(
            name='Automotive Systems Engineering',
            category='competency_specific',
            competency_focus='Systems Architecture',
            industry_context='Automotive',
            template_text="""
            Generate a SMART learning objective for {competency} in {industry} context.
            Consider {company_processes} and {project_types}.
            Target level: {target_level}
            Current level: {current_level}
            """,
            variables=['competency', 'industry', 'company_processes', 'project_types', 'target_level', 'current_level'],
            success_criteria={
                'smart_score_min': 85,
                'relevance_min': 0.8,
                'specificity_required': True
            },
            usage_count=0,
            average_quality_score=0.0,
            metadata={
                'created_by': 'system',
                'version': '1.0',
                'validated': True
            }
        )

        db_session.add(template)
        db_session.commit()

        assert template.id is not None
        assert template.competency_focus == 'Systems Architecture'
        assert len(template.variables) == 6
        assert template.success_criteria['smart_score_min'] == 85

    def test_model_relationships_integrity(self, db_session):
        """Test relationships between models"""
        # Create complete data hierarchy
        user = User(username='test_user', email='test@example.com')
        competency = SECompetency(name='Systems Thinking', code='ST')
        role = SERole(name='System Engineer')
        archetype = QualificationArchetype(name='Project Training', strategy='hands_on')

        db_session.add_all([user, competency, role, archetype])
        db_session.flush()

        # Create assessment with results
        assessment = Assessment(
            user_id=user.id,
            phase=2,
            assessment_type='competency',
            title='Competency Assessment',
            selected_archetype_id=archetype.id
        )
        db_session.add(assessment)
        db_session.flush()

        # Add competency result
        result = CompetencyAssessmentResult(
            assessment_id=assessment.id,
            competency_id=competency.id,
            current_level=2,
            target_level=4,
            score=80.0
        )
        db_session.add(result)

        # Add learning objective
        objective = LearningObjective(
            user_id=user.id,
            competency_id=competency.id,
            text='Test objective',
            type='rag_generated'
        )
        db_session.add(objective)

        # Create qualification plan
        plan = QualificationPlan(
            user_id=user.id,
            name='Test Plan',
            target_role='System Engineer',
            archetype_id=archetype.id
        )
        db_session.add(plan)
        db_session.commit()

        # Test relationships
        assert assessment.user == user
        assert assessment.selected_archetype == archetype
        assert result.assessment == assessment
        assert result.competency == competency
        assert objective.user == user
        assert objective.competency == competency
        assert plan.user == user
        assert plan.archetype == archetype

        # Test cascade relationships
        assert len(user.assessments) == 1
        assert len(user.learning_objectives) == 1
        assert len(user.qualification_plans) == 1
        assert len(assessment.competency_results) == 1

    def test_model_validation_constraints(self, db_session):
        """Test model validation and constraints"""
        # Test required fields
        with pytest.raises(Exception):
            user = User()  # Missing required username and email
            db_session.add(user)
            db_session.commit()

        # Test unique constraints
        user1 = User(username='test_user', email='test1@example.com')
        user2 = User(username='test_user', email='test2@example.com')  # Duplicate username

        db_session.add(user1)
        db_session.commit()

        with pytest.raises(Exception):
            db_session.add(user2)
            db_session.commit()

    def test_json_field_serialization(self, db_session):
        """Test JSON field serialization and deserialization"""
        user = User(username='test_user', email='test@example.com')
        competency = SECompetency(name='Test Competency', code='TC')

        db_session.add_all([user, competency])
        db_session.flush()

        # Test complex JSON data
        complex_data = {
            'analysis': {
                'specific': {'score': 90, 'feedback': 'Very specific'},
                'measurable': {'score': 85, 'feedback': 'Clearly measurable'}
            },
            'sources': ['source1', 'source2'],
            'metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0'
            }
        }

        objective = LearningObjective(
            user_id=user.id,
            competency_id=competency.id,
            text='Test objective',
            smart_analysis=complex_data,
            rag_sources=['source1', 'source2']
        )

        db_session.add(objective)
        db_session.commit()

        # Retrieve and verify JSON serialization
        retrieved = db_session.query(LearningObjective).filter_by(id=objective.id).first()
        assert retrieved.smart_analysis['analysis']['specific']['score'] == 90
        assert len(retrieved.rag_sources) == 2

def run_model_tests():
    """Run all model tests and return results"""
    print("🧪 Running SE-QPT Backend Model Tests...")

    # Configure pytest to run with coverage
    import coverage
    cov = coverage.Coverage(source=['models'])
    cov.start()

    # Run tests
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--disable-warnings'
    ])

    cov.stop()
    cov.save()

    # Generate coverage report
    print("\n📊 Test Coverage Report:")
    cov.report(show_missing=True)

    return {
        'status': 'passed' if exit_code == 0 else 'failed',
        'exit_code': exit_code,
        'coverage': cov.report()
    }

if __name__ == '__main__':
    results = run_model_tests()
    print(f"\n✅ Model Tests: {results['status']}")