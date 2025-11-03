"""
Test fixtures for contract management tests
"""

# Sample OpenAPI specification for testing
SAMPLE_OPENAPI = {
    "openapi": "3.0.0",
    "info": {
        "title": "User Management API",
        "version": "1.0.0",
        "description": "API for user management"
    },
    "servers": [
        {
            "url": "http://localhost:8080",
            "description": "Development server"
        }
    ],
    "paths": {
        "/api/user/login": {
            "post": {
                "summary": "User login",
                "operationId": "userLogin",
                "tags": ["Authentication"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string"}
                                },
                                "required": ["username", "password"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Login successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "token": {"type": "string"},
                                        "userId": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/user/{userId}": {
            "get": {
                "summary": "Get user info",
                "operationId": "getUserInfo",
                "tags": ["User"],
                "parameters": [
                    {
                        "name": "userId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "User information",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "userId": {"type": "integer"},
                                        "username": {"type": "string"},
                                        "email": {"type": "string"},
                                        "phone": {"type": "string"},
                                        "createDate": {"type": "string"},
                                        "uuid": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/reports/export": {
            "post": {
                "summary": "Export report",
                "operationId": "exportReport",
                "tags": ["Reports"],
                "responses": {
                    "200": {
                        "description": "Export successful"
                    }
                }
            }
        },
        "/api/reports/list": {
            "get": {
                "summary": "List reports",
                "operationId": "listReports",
                "tags": ["Reports"],
                "responses": {
                    "200": {
                        "description": "Report list"
                    }
                }
            }
        },
        "/api/admin/settings": {
            "get": {
                "summary": "Get admin settings",
                "operationId": "getAdminSettings",
                "tags": ["Admin"],
                "responses": {
                    "200": {
                        "description": "Settings"
                    }
                }
            }
        }
    }
}

# Sample configuration
SAMPLE_CONFIG = {
    "aceflow": {
        "project": {
            "name": "Test Project",
            "openapi_url": "http://localhost:8080/v3/api-docs"
        },
        "features": {
            "user-management": {
                "description": "User management feature",
                "api_filter": {
                    "type": "prefix",
                    "pattern": "/api/user/"
                },
                "dev_team": ["alice@example.com", "bob@example.com"],
                "enabled": True
            },
            "reports": {
                "description": "Report feature",
                "api_filter": {
                    "type": "prefix",
                    "pattern": "/api/reports/"
                },
                "dev_team": ["charlie@example.com"],
                "enabled": True
            }
        },
        "contract_repo": {
            "url": "git@github.com:test/contracts.git",
            "branch": "main",
            "base_path": "contracts/active"
        },
        "notification": {
            "smtp": {
                "host": "smtp.example.com",
                "port": 587,
                "user": "test@example.com",
                "password": "${SMTP_PASSWORD}",
                "from_email": "aceflow@example.com"
            }
        },
        "smart_completion": {
            "enabled": True,
            "rules": [
                {"pattern": ".*[Ii]d$", "example": 12345},
                {"pattern": ".*[Dd]ate$", "example": "2025-01-01"},
                {"pattern": ".*[Uu]uid$", "example": "550e8400-e29b-41d4-a716-446655440000"},
                {"pattern": ".*[Ee]mail$", "example": "user@example.com"},
                {"pattern": ".*[Pp]hone$", "example": "13800138000"}
            ]
        }
    }
}
