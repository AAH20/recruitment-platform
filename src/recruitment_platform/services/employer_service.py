"""Employer service for recruitment platform."""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from recruitment_platform.models.employer import Employer

logger = logging.getLogger(__name__)


class EmployerNotFoundError(Exception):
    """Raised when an employer is not found."""

    def __init__(self, employer_id: str) -> None:
        self.employer_id = employer_id
        super().__init__(f"Employer with id {employer_id} not found")


class EmployerValidationError(Exception):
    """Raised when employer data fails validation."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class EmployerServiceError(Exception):
    """Raised when an employer service operation fails."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def _get_db() -> Session:
    """Get a database session.

    Returns:
        A SQLAlchemy Session instance.

    Raises:
        EmployerServiceError: If session creation fails.
    """
    try:
        from recruitment_platform.database import SessionLocal

        return SessionLocal()
    except Exception as e:
        logger.error(f"Failed to create database session: {e}")
        raise EmployerServiceError(f"Database session error: {e}") from e


def _employer_to_dict(employer: Employer) -> dict:
    """Convert an Employer model instance to a dictionary.

    Args:
        employer: The Employer model instance.

    Returns:
        A dictionary representation of the employer.
    """
    return {
        "id": employer.id,
        "name": employer.name,
        "email": employer.email,
        "phone": employer.phone,
        "website": employer.website,
        "industry": employer.industry,
        "size": employer.size,
        "location": employer.location,
        "description": employer.description,
        "is_active": employer.is_active,
        "created_at": employer.created_at.isoformat()
        if hasattr(employer, "created_at") and employer.created_at
        else None,
        "updated_at": employer.updated_at.isoformat()
        if hasattr(employer, "updated_at") and employer.updated_at
        else None,
    }


def get_employer(employer_id: str) -> dict:
    """Get employer by ID.

    Args:
        employer_id: The unique identifier of the employer.

    Returns:
        A dictionary containing the employer data.

    Raises:
        EmployerNotFoundError: If the employer does not exist.
        EmployerServiceError: If the operation fails.
    """
    db = _get_db()
    try:
        employer = db.query(Employer).filter(Employer.id == employer_id).first()
        if not employer:
            raise EmployerNotFoundError(employer_id)
        return _employer_to_dict(employer)
    except EmployerNotFoundError:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching employer {employer_id}: {e}")
        raise EmployerServiceError(f"Failed to fetch employer: {e}") from e
    finally:
        db.close()


def list_employers(filters: dict, page: int, page_size: int) -> list[dict]:
    """List employers with optional filters and pagination.

    Args:
        filters: A dictionary of filter criteria.
        page: The page number (1-indexed).
        page_size: The number of results per page.

    Returns:
        A list of employer dictionaries.

    Raises:
        EmployerServiceError: If the operation fails.
    """
    db = _get_db()
    try:
        query = db.query(Employer)

        # Apply filters
        if filters:
            if filters.get("name"):
                query = query.filter(Employer.name.ilike(f"%{filters['name']}%"))
            if filters.get("industry"):
                query = query.filter(Employer.industry == filters["industry"])
            if filters.get("location"):
                query = query.filter(
                    Employer.location.ilike(f"%{filters['location']}%")
                )
            if "is_active" in filters and filters["is_active"] is not None:
                query = query.filter(Employer.is_active == filters["is_active"])
            if filters.get("size"):
                query = query.filter(Employer.size == filters["size"])

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        employers = query.all()
        return [_employer_to_dict(emp) for emp in employers]

    except SQLAlchemyError as e:
        logger.error(f"Database error listing employers: {e}")
        raise EmployerServiceError(f"Failed to list employers: {e}") from e
    finally:
        db.close()


def create_employer(data: dict) -> dict:
    """Create a new employer.

    Args:
        data: A dictionary containing the employer data.

    Returns:
        A dictionary containing the created employer data.

    Raises:
        EmployerValidationError: If data validation fails.
        EmployerServiceError: If the operation fails.
    """
    db = _get_db()
    try:
        # Validate required fields
        if not data.get("name") or not str(data["name"]).strip():
            raise EmployerValidationError("Employer name is required")
        if not data.get("email") or not str(data["email"]).strip():
            raise EmployerValidationError("Employer email is required")

        # Check for duplicate email
        existing = (
            db.query(Employer)
            .filter(Employer.email == str(data["email"]).strip())
            .first()
        )
        if existing:
            raise EmployerValidationError(
                f"Employer with email {data['email']} already exists"
            )

        employer = Employer(
            name=str(data["name"]).strip(),
            email=str(data["email"]).strip(),
            phone=data.get("phone"),
            website=data.get("website"),
            industry=data.get("industry"),
            size=data.get("size"),
            location=data.get("location"),
            description=data.get("description"),
            is_active=data.get("is_active", True),
        )

        db.add(employer)
        db.commit()
        db.refresh(employer)

        logger.info(f"Created employer {employer.id}: {employer.name}")
        return _employer_to_dict(employer)

    except EmployerValidationError:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating employer: {e}")
        raise EmployerValidationError("Employer with this data already exists") from e
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating employer: {e}")
        raise EmployerServiceError(f"Failed to create employer: {e}") from e
    finally:
        db.close()


def update_employer(employer_id: str, data: dict) -> dict:
    """Update an existing employer.

    Args:
        employer_id: The unique identifier of the employer.
        data: A dictionary containing the fields to update.

    Returns:
        A dictionary containing the updated employer data.

    Raises:
        EmployerNotFoundError: If the employer does not exist.
        EmployerValidationError: If data validation fails.
        EmployerServiceError: If the operation fails.
    """
    db = _get_db()
    try:
        employer = db.query(Employer).filter(Employer.id == employer_id).first()
        if not employer:
            raise EmployerNotFoundError(employer_id)

        # Validate name if provided
        if "name" in data:
            if not str(data["name"]).strip():
                raise EmployerValidationError("Employer name cannot be empty")
            employer.name = str(data["name"]).strip()

        # Validate email if provided
        if "email" in data:
            if not str(data["email"]).strip():
                raise EmployerValidationError("Employer email cannot be empty")
            # Check for duplicate email
            existing = (
                db.query(Employer)
                .filter(
                    Employer.email == str(data["email"]).strip(),
                    Employer.id != employer_id,
                )
                .first()
            )
            if existing:
                raise EmployerValidationError(
                    f"Employer with email {data['email']} already exists"
                )
            employer.email = str(data["email"]).strip()

        # Update optional fields
        if "phone" in data:
            employer.phone = data["phone"]
        if "website" in data:
            employer.website = data["website"]
        if "industry" in data:
            employer.industry = data["industry"]
        if "size" in data:
            employer.size = data["size"]
        if "location" in data:
            employer.location = data["location"]
        if "description" in data:
            employer.description = data["description"]
        if "is_active" in data:
            employer.is_active = data["is_active"]

        db.commit()
        db.refresh(employer)

        logger.info(f"Updated employer {employer.id}: {employer.name}")
        return _employer_to_dict(employer)

    except (EmployerNotFoundError, EmployerValidationError):
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error updating employer {employer_id}: {e}")
        raise EmployerValidationError("Employer with this data already exists") from e
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating employer {employer_id}: {e}")
        raise EmployerServiceError(f"Failed to update employer: {e}") from e
    finally:
        db.close()


def delete_employer(employer_id: str) -> bool:
    """Delete an employer.

    Args:
        employer_id: The unique identifier of the employer.

    Returns:
        True if the employer was deleted successfully.

    Raises:
        EmployerNotFoundError: If the employer does not exist.
        EmployerServiceError: If the operation fails.
    """
    db = _get_db()
    try:
        employer = db.query(Employer).filter(Employer.id == employer_id).first()
        if not employer:
            raise EmployerNotFoundError(employer_id)

        db.delete(employer)
        db.commit()

        logger.info(f"Deleted employer {employer_id}")
        return True

    except EmployerNotFoundError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting employer {employer_id}: {e}")
        raise EmployerServiceError(f"Failed to delete employer: {e}") from e
    finally:
        db.close()
