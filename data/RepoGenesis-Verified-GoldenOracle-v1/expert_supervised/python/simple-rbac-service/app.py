#!/usr/bin/env python3
"""
Simple RBAC Service - Role-Based Access Control API

A lightweight service for managing users, roles, and permissions.
"""

from flask import Flask, request, jsonify
from typing import Dict, List, Set, Optional
import uuid

# Initialize Flask app
app = Flask(__name__)

# In-memory data storage
roles_db: Dict[str, Dict] = {}  # role_id -> {role_name, permissions}
users_db: Dict[str, Dict] = {}  # user_id -> {role_ids}
role_names: Dict[str, str] = {}  # role_name -> role_id (for uniqueness check)

# Helper functions


def generate_role_id() -> str:
    """Generate a unique role ID"""
    return f"role_{str(uuid.uuid4())[:8]}"


def get_success_response(data: Dict) -> tuple:
    """Create a success response"""
    response = {"status": "success"}
    response.update(data)
    return jsonify(response), 200


def get_error_response(message: str) -> tuple:
    """Create an error response"""
    return jsonify({"status": "error", "message": message}), 400


# API Endpoints


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "Simple RBAC Service"}), 200


@app.route("/api/roles", methods=["POST"])
def create_role():
    """
    Create a new role
    
    Request body: {"role_name": "string"}
    """
    try:
        data = request.get_json()
        
        if not data:
            return get_error_response("Request body must be JSON")
        
        # Validate required fields
        role_name = data.get("role_name")
        if not role_name:
            return get_error_response("Missing required field: role_name")
        
        # Check for duplicates
        if role_name in role_names:
            return get_error_response(f"Role '{role_name}' already exists")
        
        # Create new role
        role_id = generate_role_id()
        roles_db[role_id] = {
            "role_name": role_name,
            "permissions": set()
        }
        role_names[role_name] = role_id
        
        return get_success_response({
            "role_id": role_id,
            "role_name": role_name
        })
    
    except Exception as e:
        return get_error_response(f"Internal server error: {str(e)}")


@app.route("/api/roles/<role_id>/permissions", methods=["POST"])
def assign_permissions_to_role(role_id: str):
    """
    Assign permissions to a role
    
    Request body: {"permissions": ["string"]}
    """
    try:
        # Check if role exists
        if role_id not in roles_db:
            return get_error_response(f"Role '{role_id}' not found")
        
        data = request.get_json()
        
        if not data:
            return get_error_response("Request body must be JSON")
        
        # Validate required fields
        permissions = data.get("permissions")
        if not permissions:
            return get_error_response("Missing required field: permissions")
        
        if not isinstance(permissions, list):
            return get_error_response("Field 'permissions' must be a list")
        
        # Add permissions to role
        for permission in permissions:
            roles_db[role_id]["permissions"].add(permission)
        
        # Return the role with all its permissions
        all_permissions = list(roles_db[role_id]["permissions"])
        
        return get_success_response({
            "role_id": role_id,
            "permissions": sorted(all_permissions)
        })
    
    except Exception as e:
        return get_error_response(f"Internal server error: {str(e)}")


@app.route("/api/users/<user_id>/roles", methods=["POST"])
def assign_roles_to_user(user_id: str):
    """
    Assign roles to a user
    
    Request body: {"role_ids": ["string"]}
    """
    try:
        data = request.get_json()
        
        if not data:
            return get_error_response("Request body must be JSON")
        
        # Validate required fields
        role_ids = data.get("role_ids")
        if role_ids is None:
            return get_error_response("Missing required field: role_ids")
        
        if not isinstance(role_ids, list):
            return get_error_response("Field 'role_ids' must be a list")
        
        # Validate that all role IDs exist
        for role_id in role_ids:
            if role_id not in roles_db:
                return get_error_response(f"Role '{role_id}' not found")
        
        # Create or update user's roles
        if user_id not in users_db:
            users_db[user_id] = {"role_ids": set()}
        
        # Add roles to user
        for role_id in role_ids:
            users_db[user_id]["role_ids"].add(role_id)
        
        # Return the user with all their roles
        all_role_ids = list(users_db[user_id]["role_ids"])
        
        return get_success_response({
            "user_id": user_id,
            "role_ids": sorted(all_role_ids)
        })
    
    except Exception as e:
        return get_error_response(f"Internal server error: {str(e)}")


@app.route("/api/users/<user_id>/permissions", methods=["GET"])
def get_user_permissions(user_id: str):
    """
    Get all permissions for a user
    
    Permissions are the union of all permissions from user's roles
    """
    try:
        # Get user's roles
        if user_id not in users_db:
            # User exists but has no roles
            return get_success_response({
                "user_id": user_id,
                "permissions": []
            })
        
        user_role_ids = users_db[user_id]["role_ids"]
        
        # Collect all permissions from user's roles
        all_permissions: Set[str] = set()
        for role_id in user_role_ids:
            if role_id in roles_db:
                all_permissions.update(roles_db[role_id]["permissions"])
        
        return get_success_response({
            "user_id": user_id,
            "permissions": sorted(list(all_permissions))
        })
    
    except Exception as e:
        return get_error_response(f"Internal server error: {str(e)}")


# Error handlers


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return get_error_response("Endpoint not found"), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return get_error_response("Method not allowed"), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return get_error_response("Internal server error"), 500


if __name__ == "__main__":
    # Run the Flask app on port 8080
    app.run(host="0.0.0.0", port=8080, debug=False)

