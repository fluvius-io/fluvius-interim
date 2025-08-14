"""Test basic imports for fluvius_interim package."""

import pytest


def test_main_package_import():
    """Test that the main package can be imported."""
    import fluvius_interim
    assert fluvius_interim is not None


def test_domain_imports():
    """Test that domain components can be imported."""
    from fluvius_interim.domain import WorkflowDomain, WorkflowQueryManager
    assert WorkflowDomain is not None
    assert WorkflowQueryManager is not None


def test_engine_imports():
    """Test that engine components can be imported."""
    from fluvius_interim import WorkflowManager, ActivityRouter
    assert WorkflowManager is not None
    assert ActivityRouter is not None


def test_workflow_imports():
    """Test that workflow components can be imported."""
    from fluvius_interim import Workflow, Stage, Step, Role
    assert Workflow is not None
    assert Stage is not None
    assert Step is not None
    assert Role is not None


def test_model_imports():
    """Test that model components can be imported."""
    from fluvius_interim import WorkflowDataManager
    assert WorkflowDataManager is not None


def test_config_imports():
    """Test that configuration can be imported."""
    from fluvius_interim import config, logger
    assert config is not None
    assert logger is not None


def test_all_exports():
    """Test that all exported components are available."""
    import fluvius_interim
    
    # Check that __all__ is defined and contains expected exports
    assert hasattr(fluvius_interim, '__all__')
    assert isinstance(fluvius_interim.__all__, list)
    assert len(fluvius_interim.__all__) > 0
    
    # Test that all exported items are actually available
    for item_name in fluvius_interim.__all__:
        assert hasattr(fluvius_interim, item_name), f"{item_name} not found in package"


def test_package_metadata():
    """Test that package metadata is accessible."""
    import fluvius_interim
    
    # Basic package structure check
    assert hasattr(fluvius_interim, 'config')
    assert hasattr(fluvius_interim, 'logger')


def test_domain_command_imports():
    """Test that domain commands can be imported."""
    from fluvius_interim.domain.command import (
        CreateWorkflow, UpdateWorkflow, AddParticipant, RemoveParticipant,
        InjectEvent, SendTrigger
    )
    
    assert CreateWorkflow is not None
    assert UpdateWorkflow is not None
    assert AddParticipant is not None
    assert RemoveParticipant is not None
    assert InjectEvent is not None
    assert SendTrigger is not None


def test_domain_datadef_imports():
    """Test that domain data definitions can be imported."""
    from fluvius_interim.domain.datadef import (
        CreateWorkflowData, UpdateWorkflowData, AddParticipantData,
        InjectEventData, SendTriggerData
    )
    
    assert CreateWorkflowData is not None
    assert UpdateWorkflowData is not None
    assert AddParticipantData is not None
    assert InjectEventData is not None
    assert SendTriggerData is not None


def test_domain_query_imports():
    """Test that domain queries can be imported."""
    from fluvius_interim.domain.query import (
        WorkflowQuery, WorkflowStepQuery, WorkflowParticipantQuery
    )
    
    assert WorkflowQuery is not None
    assert WorkflowStepQuery is not None
    assert WorkflowParticipantQuery is not None


def test_engine_component_imports():
    """Test that engine components can be imported individually."""
    from fluvius_interim.engine.workflow import Workflow
    from fluvius_interim.engine.manager import WorkflowManager
    from fluvius_interim.engine.router import ActivityRouter
    from fluvius_interim.engine.datadef import WorkflowData
    
    assert Workflow is not None
    assert WorkflowManager is not None
    assert ActivityRouter is not None
    assert WorkflowData is not None


def test_status_imports():
    """Test that status enums can be imported."""
    from fluvius_interim.status import WorkflowStatus, StepStatus
    
    assert WorkflowStatus is not None
    assert StepStatus is not None
    
    # Test some status values
    assert hasattr(WorkflowStatus, 'NEW')
    assert hasattr(WorkflowStatus, 'ACTIVE')
    assert hasattr(WorkflowStatus, 'COMPLETED')
    
    assert hasattr(StepStatus, 'PENDING')
    assert hasattr(StepStatus, 'ACTIVE')
    assert hasattr(StepStatus, 'COMPLETED')


def test_model_components():
    """Test that model components are accessible."""
    from fluvius_interim.model import WorkflowDataManager, WorkflowConnector
    
    assert WorkflowDataManager is not None
    assert WorkflowConnector is not None


def test_schema_imports():
    """Test that schema components can be imported."""
    from fluvius_interim import schema
    assert schema is not None


def test_configuration_values():
    """Test that configuration values are properly set."""
    from fluvius_interim import config
    
    # Test that config has expected attributes
    assert hasattr(config, 'CQRS_DOMAIN_NAMESPACE')
    assert hasattr(config, 'DB_DSN')
    assert hasattr(config, 'MAX_MUTATIONS')
    
    # Test default values
    assert config.CQRS_DOMAIN_NAMESPACE == 'riparius-workflow'
    assert config.MAX_MUTATIONS == 50


def test_logger_functionality():
    """Test that logger is properly configured."""
    from fluvius_interim import logger
    
    # Test that logger has expected methods
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'error')
    assert hasattr(logger, 'warning')
    assert hasattr(logger, 'debug')
    
    # Test that logger name is correct
    assert logger.name == 'fluvius_interim'


def test_circular_imports():
    """Test that there are no circular import issues."""
    # Import in different orders to test for circular dependencies
    
    # Test 1: Domain first
    from fluvius_interim.domain import WorkflowDomain
    from fluvius_interim import WorkflowManager
    assert WorkflowDomain is not None
    assert WorkflowManager is not None
    
    # Test 2: Engine first
    from fluvius_interim.engine.manager import WorkflowManager as EngineManager
    from fluvius_interim.domain.aggregate import WorkflowAggregate
    assert EngineManager is not None
    assert WorkflowAggregate is not None


def test_relative_imports():
    """Test that relative imports work correctly within the package."""
    # Test that internal imports work
    from fluvius_interim.domain import command, datadef
    assert command is not None
    assert datadef is not None
    
    # Test meta imports
    from fluvius_interim._meta import config as meta_config, logger as meta_logger
    assert meta_config is not None
    assert meta_logger is not None


if __name__ == "__main__":
    pytest.main([__file__])