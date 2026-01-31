"""
SE-QPT Unified Web Platform - Flask Backend
Integrates all components: Marcel's methodology, Derik's assessor, RAG-LLM innovation
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Extensions will be initialized by the models module
migrate = Migrate()
jwt = JWTManager()

# Import db at module level to make it available for mvp_routes
from models import db

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://seqpt_user:seqpt_pass@localhost:5432/seqpt')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://ma0349:MA0349_2025@localhost:5432/competency_assessment')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # DEBUG: Log database connection
    print(f"[DATABASE] Using: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

    # OpenAI Configuration
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

    # File upload configuration
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

    # Initialize extensions with app (db is already imported at module level)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # CORS configuration for frontend
    CORS(app,
         origins=[
             'http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002',
             'http://localhost:3003', 'http://localhost:3004', 'http://localhost:5173',
             'http://127.0.0.1:3000', 'http://127.0.0.1:3001', 'http://127.0.0.1:3002',
             'http://127.0.0.1:3003', 'http://127.0.0.1:3004', 'http://127.0.0.1:5173'
         ],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         supports_credentials=True,
         expose_headers=['Content-Type', 'Authorization', 'Content-Disposition']
    )

    # Register blueprints - Refactored routes structure (Dec 2025)
    # All routes are now organized into domain-specific blueprints
    from app.routes.auth import auth_bp
    from app.routes.organization import org_bp
    from app.routes.phase1_maturity import phase1_maturity_bp
    from app.routes.phase1_roles import phase1_roles_bp
    from app.routes.phase1_strategies import phase1_strategies_bp
    from app.routes.phase2_assessment import phase2_assessment_bp
    from app.routes.phase2_learning import phase2_learning_bp
    from app.routes.phase3_planning import phase3_planning_bp
    from app.routes.phase4_aviva import phase4_aviva_bp
    from app.routes.main import main_bp
    from app.competency_service import competency_service_bp

    # Register all blueprints under /api prefix
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(org_bp, url_prefix='/api')
    app.register_blueprint(phase1_maturity_bp, url_prefix='/api')
    app.register_blueprint(phase1_roles_bp, url_prefix='/api')
    app.register_blueprint(phase1_strategies_bp, url_prefix='/api')
    app.register_blueprint(phase2_assessment_bp, url_prefix='/api')
    app.register_blueprint(phase2_learning_bp, url_prefix='/api')
    app.register_blueprint(phase3_planning_bp, url_prefix='/api')
    app.register_blueprint(phase4_aviva_bp, url_prefix='/api')
    app.register_blueprint(main_bp, url_prefix='/api')
    app.register_blueprint(competency_service_bp, url_prefix='/api/competency')

    print("[OK] All 10 route blueprints registered successfully:"
          "\n  - auth_bp: /api/mvp/auth/*, /api/auth/*"
          "\n  - org_bp: /api/organization/*"
          "\n  - phase1_maturity_bp: /api/phase1/maturity/*"
          "\n  - phase1_roles_bp: /api/phase1/roles/*, /api/findProcesses, /api/role-clusters"
          "\n  - phase1_strategies_bp: /api/phase1/target-group/*, /api/phase1/strategies/*"
          "\n  - phase2_assessment_bp: /api/phase2/*, /api/assessment/*"
          "\n  - phase2_learning_bp: /api/phase2/learning-objectives/*"
          "\n  - phase3_planning_bp: /api/phase3/*"
          "\n  - phase4_aviva_bp: /api/phase4/* (AVIVA Didactics)"
          "\n  - main_bp: /api/ (misc routes)")

    # Import Derik's routes - Enable competency assessor integration
    try:
        from app.derik_integration import derik_bp
        app.register_blueprint(derik_bp, url_prefix='/api/derik')
        print("Derik's competency assessor integration enabled (bridge routes only)")
    except Exception as e:
        print(f"Warning: Derik's competency assessor not available: {e}")
        pass

    # Import SE-QPT RAG routes - REMOVED Phase 3 - Broken (uses removed models)
    # Archived to archive/blueprints/seqpt_routes.py
    # try:
    #     from app.seqpt_routes import seqpt_bp
    #     app.register_blueprint(seqpt_bp, url_prefix='/api/seqpt')
    #     print("SE-QPT RAG routes registered successfully")
    # except Exception as e:
    #     print(f"Warning: SE-QPT RAG routes not available: {e}")
    #     pass

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'service': 'SE-QPT Unified Platform',
            'version': '1.0.0',
            'components': {
                'database': 'connected',
                'rag_llm': 'operational',
                'derik_assessor': 'integrated'
            }
        }

    return app