import logging
import os
from types import SimpleNamespace


def setup_config():
    """Setup configuration for fluvius_interim package."""
    config = SimpleNamespace()
    
    # Import defaults
    from .defaults import (
        MAX_MUTATIONS,
        DB_DSN,
        CQRS_DOMAIN_NAMESPACE,
        CQRS_RESOURCE_SCHEMA
    )
    
    # Set configuration values
    config.MAX_MUTATIONS = int(os.getenv('FLUVIUS_INTERIM_MAX_MUTATIONS', MAX_MUTATIONS))
    config.DB_DSN = os.getenv('FLUVIUS_INTERIM_DB_DSN', DB_DSN)
    config.CQRS_DOMAIN_NAMESPACE = os.getenv('FLUVIUS_INTERIM_DOMAIN_NAMESPACE', CQRS_DOMAIN_NAMESPACE)
    config.CQRS_RESOURCE_SCHEMA = os.getenv('FLUVIUS_INTERIM_RESOURCE_SCHEMA', CQRS_RESOURCE_SCHEMA)
    
    return config


def setup_logger():
    """Setup logger for fluvius_interim package."""
    logger = logging.getLogger('fluvius_interim')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


# Initialize config and logger
config = setup_config()
logger = setup_logger()
