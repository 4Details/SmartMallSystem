class AppError(Exception):
    """Base exception for all application errors"""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class UserNotFoundError(AppError):
    """Raised when a user is not found"""
    def __init__(self, message="User not found"):
        super().__init__(message, 404)

class DuplicateUserError(AppError):
    """Raised when attempting to create a user with existing username or email"""
    def __init__(self, message="Username or email already exists"):
        super().__init__(message, 409)

class ProductNotFoundError(AppError):
    """Raised when a product is not found"""
    def __init__(self, message="Product not found"):
        super().__init__(message, 404)

class InsufficientStockError(AppError):
    """Raised when product stock is insufficient"""
    def __init__(self, message="Insufficient stock"):
        super().__init__(message, 400)

class InsufficientPointsError(AppError):
    """Raised when user doesn't have enough points"""
    def __init__(self, message="Insufficient points"):
        super().__init__(message, 400)

class OrderNotFoundError(AppError):
    """Raised when an order is not found"""
    def __init__(self, message="Order not found"):
        super().__init__(message, 404)

class InvalidOrderStatusError(AppError):
    """Raised when attempting an invalid order status transition"""
    def __init__(self, message="Invalid order status transition"):
        super().__init__(message, 400)

class AuthenticationError(AppError):
    """Raised for authentication failures"""
    def __init__(self, message="Authentication failed"):
        super().__init__(message, 401)

class AuthorizationError(AppError):
    """Raised for authorization failures"""
    def __init__(self, message="You don't have permission to perform this action"):
        super().__init__(message, 403)