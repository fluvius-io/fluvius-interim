"""Test basic workflow functionality for fluvius_interim."""

import pytest
from pprint import pformat
from types import SimpleNamespace
from fluvius_interim import logger, config
from fluvius_interim import (
    Workflow, Stage, Step, Role, st_connect, wf_connect, transition, 
    FINISH_STATE, ActivityRouter, WorkflowManager
)
from fluvius.data import UUID_GENF, UUID_GENR

selector01 = UUID_GENF('S101')
resource01 = UUID_GENR()


@pytest.fixture(scope="session")
async def workflows():
    """Fixture for workflow instances"""
    workflows = SimpleNamespace()
    return workflows


@pytest.mark.asyncio(loop_scope="session")
async def test_workflow_01(workflows):
    """Test basic workflow creation and execution"""
    manager = WorkflowManager()
    async with manager._datamgr.transaction():
        wf = manager.create_workflow('sample-process', 'test-resource', resource01, {
            'test-param': 'test-value',
            'step-selector': str(selector01)
        })
        with wf.transaction():
            wf.start()
        await manager.commit()

        evt_data = SimpleNamespace(
            resource_name='test-resource',
            resource_id=resource01,
            step_selector=selector01
        )

        workflows.id01 = wf.id
        async for wf in manager.process_event('test-event', evt_data):
            assert len(wf.step_id_map) == 3  # 3 steps created
            await manager.commit_workflow(wf)


@pytest.mark.asyncio(loop_scope="session")
async def test_workflow_02(workflows):
    """Test workflow event processing"""
    manager = WorkflowManager()
    async with manager._datamgr.transaction():
        wf = await manager.load_workflow_by_id('sample-process', workflows.id01)

        evt_data = SimpleNamespace(
            resource_name='test-resource',
            resource_id=resource01,
            step_selector=selector01
        )

        async for wf in manager.process_event('test-event', evt_data):
            assert len(wf.step_id_map) == 5  # 2 more steps created
            await manager.commit_workflow(wf)


@pytest.mark.asyncio
async def test_workflow_manager_basic():
    """Test WorkflowManager basic functionality"""
    manager = WorkflowManager()
    assert hasattr(manager, 'process_event')
    assert hasattr(manager, 'create_workflow')
    assert hasattr(manager, 'load_workflow_by_id')


@pytest.mark.asyncio
async def test_workflow_creation_parameters():
    """Test workflow creation with various parameters"""
    manager = WorkflowManager()
    
    # Test with minimal parameters
    wf = manager.create_workflow(
        'test-workflow', 
        'test-resource', 
        UUID_GENR(), 
        {'basic': 'param'}
    )
    
    assert wf is not None
    assert hasattr(wf, 'id')
    assert hasattr(wf, 'start')


@pytest.mark.asyncio
async def test_event_data_structure():
    """Test event data structure creation"""
    resource_id = UUID_GENR()
    step_selector = UUID_GENF('test-selector')
    
    evt_data = SimpleNamespace(
        resource_name='test-resource',
        resource_id=resource_id,
        step_selector=step_selector,
        additional_data={'key': 'value'}
    )
    
    assert evt_data.resource_name == 'test-resource'
    assert evt_data.resource_id == resource_id
    assert evt_data.step_selector == step_selector
    assert evt_data.additional_data['key'] == 'value'


@pytest.mark.asyncio
async def test_workflow_transaction_context():
    """Test workflow transaction context management"""
    manager = WorkflowManager()
    
    async with manager._datamgr.transaction():
        wf = manager.create_workflow(
            'transaction-test', 
            'test-resource', 
            UUID_GENR(), 
            {'test': 'data'}
        )
        
        # Test transaction context
        with wf.transaction():
            wf.start()
            # Workflow should be in started state within transaction
            
        # Transaction should be committed at this point


@pytest.mark.asyncio 
async def test_workflow_memory_operations():
    """Test workflow memory operations"""
    # This test would need a more complete workflow implementation
    # For now, just test the basic structure
    manager = WorkflowManager()
    
    wf = manager.create_workflow(
        'memory-test',
        'test-resource',
        UUID_GENR(),
        {'memory_test': True}
    )
    
    assert wf is not None
    # Additional memory tests would go here when implementation is complete


@pytest.mark.asyncio
async def test_multiple_workflow_instances():
    """Test managing multiple workflow instances"""
    manager = WorkflowManager()
    resource1 = UUID_GENR()
    resource2 = UUID_GENR()
    
    wf1 = manager.create_workflow('multi-test-1', 'resource-1', resource1, {})
    wf2 = manager.create_workflow('multi-test-2', 'resource-2', resource2, {})
    
    assert wf1.id != wf2.id
    assert wf1 is not wf2


@pytest.mark.asyncio
async def test_workflow_configuration():
    """Test workflow configuration and metadata"""
    # Test that our configuration is accessible
    assert hasattr(config, 'CQRS_DOMAIN_NAMESPACE')
    assert hasattr(config, 'DB_DSN')
    
    # Test logger is available
    assert logger is not None
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'error')


def test_uuid_generation():
    """Test UUID generation utilities"""
    # Test fixed UUID generation
    fixed_uuid = UUID_GENF('test-fixed')
    same_uuid = UUID_GENF('test-fixed')
    assert fixed_uuid == same_uuid
    
    # Test random UUID generation
    random_uuid1 = UUID_GENR()
    random_uuid2 = UUID_GENR()
    assert random_uuid1 != random_uuid2
    assert len(str(random_uuid1)) > 0
    assert len(str(random_uuid2)) > 0
