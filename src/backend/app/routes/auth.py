"""
Authentication Routes Blueprint
===============================
Handles user authentication: login, registration, token verification, logout.

Routes:
- POST /mvp/auth/login - Login for admin and employee users
- POST /mvp/auth/register-admin - Admin creates organization and first user
- POST /mvp/auth/register-employee - Employee joins organization with code
- GET /auth/me - Get current user information
- GET /auth/verify - Verify JWT token
- POST /mvp/auth/logout - Logout (client-side cleanup)
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from datetime import datetime

from models import db, User, Organization

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/mvp/auth/login', methods=['POST'])
def login():
    """Login for both admin and employee users"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        # Find user in MVP users table
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()

            # Create access token
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={
                    'organization_id': user.organization_id,
                    'role': user.role
                }
            )

            # Fetch organization details
            response_data = {
                'access_token': access_token,
                'user': user.to_dict()
            }

            # Include organization details if user belongs to one
            if user.organization_id:
                org = Organization.query.get(user.organization_id)
                if org:
                    response_data['organization'] = org.to_dict()

            return jsonify(response_data), 200

        return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500


@auth_bp.route('/mvp/auth/register-admin', methods=['POST'])
def register_admin():
    """Admin creates organization and becomes first user"""
    try:
        data = request.get_json()
        current_app.logger.info(f"[ADMIN REGISTRATION] Received data: {data}")

        # Required fields
        required_fields = ['username', 'password', 'organization_name', 'organization_size']
        for field in required_fields:
            if not data.get(field):
                error_msg = f'{field} is required'
                current_app.logger.error(f"[ADMIN REGISTRATION] Validation failed: {error_msg}")
                return jsonify({'error': error_msg}), 400

        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            error_msg = 'Username already registered'
            current_app.logger.error(f"[ADMIN REGISTRATION] Username conflict: {data['username']}")
            return jsonify({'error': error_msg}), 400

        # Check if organization name already exists
        if Organization.query.filter_by(organization_name=data['organization_name']).first():
            error_msg = 'Organization name already registered'
            current_app.logger.error(f"[ADMIN REGISTRATION] Organization name conflict: {data['organization_name']}")
            return jsonify({'error': error_msg}), 400

        # Create organization (using Derik's unified model)
        org_code = Organization.generate_public_key(data['organization_name'])
        organization = Organization(
            organization_name=data['organization_name'],
            organization_public_key=org_code,
            size=data['organization_size']
        )
        db.session.add(organization)
        db.session.flush()  # Get organization ID

        # MATRICES NO LONGER AUTO-INITIALIZED AT REGISTRATION
        # Matrix initialization now happens in Phase 1 Task 2 (Role Selection)
        current_app.logger.info(f"[ADMIN REGISTRATION] Organization {organization.id} created - matrices will be initialized in Phase 1 Task 2")

        # Create admin user
        admin_user = User(
            username=data['username'],
            first_name=data.get('first_name'),  # Optional
            last_name=data.get('last_name'),    # Optional
            role='admin',
            organization_id=organization.id,
            joined_via_code=org_code
        )
        admin_user.set_password(data['password'])
        db.session.add(admin_user)
        db.session.commit()

        # Create access token
        access_token = create_access_token(
            identity=str(admin_user.id),
            additional_claims={
                'organization_id': organization.id,
                'role': 'admin'
            }
        )

        return jsonify({
            'access_token': access_token,
            'user': admin_user.to_dict(),
            'organization': organization.to_dict(),
            'organization_code': org_code
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Admin registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/mvp/auth/register-employee', methods=['POST'])
def register_employee():
    """Employee joins organization with organization code"""
    try:
        data = request.get_json()

        # Required fields
        required_fields = ['username', 'password', 'organization_code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already registered'}), 400

        # Validate organization code (using Derik's organization_public_key field)
        organization = Organization.query.filter_by(
            organization_public_key=data['organization_code'].upper()
        ).first()

        if not organization:
            return jsonify({'error': 'Invalid organization code'}), 400

        # Create employee user
        employee_user = User(
            username=data['username'],
            first_name=data.get('first_name'),  # Optional
            last_name=data.get('last_name'),    # Optional
            role='employee',
            organization_id=organization.id,
            joined_via_code=data['organization_code'].upper()
        )
        employee_user.set_password(data['password'])
        db.session.add(employee_user)
        db.session.commit()

        # Create access token
        access_token = create_access_token(
            identity=str(employee_user.id),
            additional_claims={
                'organization_id': organization.id,
                'role': 'employee'
            }
        )

        return jsonify({
            'access_token': access_token,
            'user': employee_user.to_dict(),
            'organization': organization.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Employee registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'user': user.to_dict()}), 200

    except Exception as e:
        current_app.logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'Failed to get user info'}), 500


@auth_bp.route('/auth/verify', methods=['GET'])
@jwt_required()
def verify_auth():
    """Verify JWT token and return user info (compatibility endpoint)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'user': user.to_dict()}), 200

    except Exception as e:
        current_app.logger.error(f"Auth verification error: {str(e)}")
        return jsonify({'error': 'Token verification failed'}), 401


@auth_bp.route('/mvp/auth/logout', methods=['POST'])
def logout():
    """Logout endpoint (for MVP - since JWT tokens are stateless, this is mainly for client-side cleanup)"""
    try:
        # For JWT tokens, logout is mainly handled client-side
        # Server-side logout would require token blacklisting which is not implemented in MVP
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500
