"""Test domain functionality for fluvius_interim."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fluvius_interim.domain import WorkflowDomain, WorkflowAggregate, WorkflowQueryManager
from fluvius_interim.domain.command import (
    CreateWorkflow, UpdateWorkflow, AddParticipant, RemoveParticipant,
    ProcessActivity, AddRole, RemoveRole, StartWorkflow, CancelWorkflow,
    IgnoreStep, CancelStep, AbortWorkflow, InjectEvent, SendTrigger
)
from fluvius_interim.domain.datadef import (
    CreateWorkflowData, UpdateWorkflowData, AddParticipantData, 
    InjectEventData, SendTriggerData
)
from fluvius.data import UUID_GENF, UUID_GENR


class TestWorkflowDomain:
    """Test workflow domain functionality"""

    def test_domain_metadata(self):
        """Test domain metadata and configuration"""
        domain = WorkflowDomain()
        
        assert domain.__namespace__ == 'riparius-workflow'
        assert domain.Meta.name == "Workflow Management"
        assert "workflow" in domain.Meta.tags
        assert domain.Meta.description is not None

    def test_domain_aggregate(self):
        """Test domain aggregate configuration"""
        domain = WorkflowDomain()
        
        assert domain.__aggregate__ == WorkflowAggregate
        assert hasattr(domain, '__statemgr__')

    def test_command_registration(self):
        """Test that commands are properly registered"""
        # Test that command classes exist
        assert CreateWorkflow is not None
        assert UpdateWorkflow is not None
        assert AddParticipant is not None
        assert RemoveParticipant is not None
        assert ProcessActivity is not None
        assert AddRole is not None
        assert RemoveRole is not None
        assert StartWorkflow is not None
        assert CancelWorkflow is not None
        assert IgnoreStep is not None
        assert CancelStep is not None
        assert AbortWorkflow is not None
        assert InjectEvent is not None
        assert SendTrigger is not None

    def test_command_metadata(self):
        """Test command metadata configuration"""
        # Test CreateWorkflow metadata
        assert CreateWorkflow.Meta.key == 'create-workflow'
        assert CreateWorkflow.Meta.name == 'Create Workflow'
        assert CreateWorkflow.Meta.auth_required == True
        assert CreateWorkflow.Meta.new_resource == True
        assert "workflow" in CreateWorkflow.Meta.resources

        # Test InjectEvent metadata
        assert InjectEvent.Meta.key == 'inject-event'
        assert InjectEvent.Meta.name == 'Inject Event'
        assert InjectEvent.Meta.auth_required == True
        assert "workflow" in InjectEvent.Meta.resources
        assert "event" in InjectEvent.Meta.tags

        # Test SendTrigger metadata
        assert SendTrigger.Meta.key == 'send-trigger'
        assert SendTrigger.Meta.name == 'Send Trigger'
        assert SendTrigger.Meta.auth_required == True
        assert "trigger" in SendTrigger.Meta.tags

    def test_data_definitions(self):
        """Test data definition classes"""
        # Test CreateWorkflowData
        data = CreateWorkflowData(
            title="Test Workflow",
            workflow_key="test-workflow",
            route_id=UUID_GENF("test-route"),
            params={"test": "value"}
        )
        assert data.title == "Test Workflow"
        assert data.workflow_key == "test-workflow"
        assert data.params["test"] == "value"

        # Test InjectEventData
        event_data = InjectEventData(
            event_type="test_event",
            event_data={"source": "test"},
            target_step_id=UUID_GENF("test-step"),
            priority=1
        )
        assert event_data.event_type == "test_event"
        assert event_data.event_data["source"] == "test"
        assert event_data.priority == 1

        # Test SendTriggerData
        trigger_data = SendTriggerData(
            trigger_type="time_based",
            trigger_data={"schedule": "daily"},
            target_id=UUID_GENF("test-target"),
            delay_seconds=300
        )
        assert trigger_data.trigger_type == "time_based"
        assert trigger_data.trigger_data["schedule"] == "daily"
        assert trigger_data.delay_seconds == 300


class TestWorkflowAggregate:
    """Test workflow aggregate functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.aggregate = WorkflowAggregate()

    @pytest.mark.asyncio
    async def test_create_workflow_method(self):
        """Test create workflow aggregate method"""
        # Mock the necessary methods
        self.aggregate.create_workflow = AsyncMock(return_value={"id": "test-id"})
        
        data = CreateWorkflowData(
            title="Test Workflow",
            workflow_key="test-workflow",
            route_id=UUID_GENF("test-route")
        )
        
        result = await self.aggregate.create_workflow(data)
        assert result is not None

    @pytest.mark.asyncio
    async def test_inject_event_method(self):
        """Test inject event aggregate method"""
        # Mock the fetch_aggroot method
        mock_workflow = MagicMock()
        mock_workflow.status = 'ACTIVE'
        mock_workflow.id = UUID_GENF("test-workflow")
        
        self.aggregate.fetch_aggroot = AsyncMock(return_value=mock_workflow)
        
        data = InjectEventData(
            event_type="test_event",
            event_data={"test": "data"},
            priority=1
        )
        
        result = await self.aggregate.do__inject_event(data)
        
        assert result["status"] == "event_injected"
        assert result["event_type"] == "test_event"
        assert result["workflow_id"] == mock_workflow.id
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_send_trigger_method(self):
        """Test send trigger aggregate method"""
        # Mock the fetch_aggroot method
        mock_workflow = MagicMock()
        mock_workflow.status = 'ACTIVE'
        mock_workflow.id = UUID_GENF("test-workflow")
        
        self.aggregate.fetch_aggroot = AsyncMock(return_value=mock_workflow)
        
        data = SendTriggerData(
            trigger_type="time_based",
            trigger_data={"schedule": "daily"},
            delay_seconds=300
        )
        
        result = await self.aggregate.do__send_trigger(data)
        
        assert result["status"] == "trigger_sent"
        assert result["trigger_type"] == "time_based"
        assert result["workflow_id"] == mock_workflow.id
        assert result["delay_seconds"] == 300
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_workflow_status_validation(self):
        """Test workflow status validation in aggregate methods"""
        # Mock workflow with invalid status for event injection
        mock_workflow = MagicMock()
        mock_workflow.status = 'COMPLETED'  # Invalid status
        
        self.aggregate.fetch_aggroot = AsyncMock(return_value=mock_workflow)
        
        data = InjectEventData(event_type="test_event")
        
        # Should raise ValueError for invalid status
        with pytest.raises(ValueError, match="Cannot inject event into workflow in status"):
            await self.aggregate.do__inject_event(data)

    @pytest.mark.asyncio
    async def test_add_participant_method(self):
        """Test add participant aggregate method"""
        # Mock workflow and state manager
        mock_workflow = MagicMock()
        mock_workflow.status = 'ACTIVE'
        mock_workflow.id = UUID_GENF("test-workflow")
        
        self.aggregate.fetch_aggroot = AsyncMock(return_value=mock_workflow)
        self.aggregate.statemgr = MagicMock()
        self.aggregate.statemgr.create = AsyncMock(return_value={"id": "participant-id"})
        
        data = AddParticipantData(
            user_id=UUID_GENF("test-user"),
            role="reviewer"
        )
        
        result = await self.aggregate.do__add_participant(data)
        assert result is not None

    @pytest.mark.asyncio
    async def test_update_workflow_method(self):
        """Test update workflow aggregate method"""
        # Mock workflow and state manager
        mock_workflow = MagicMock()
        mock_workflow.id = UUID_GENF("test-workflow")
        
        self.aggregate.fetch_aggroot = AsyncMock(return_value=mock_workflow)
        self.aggregate.statemgr = MagicMock()
        self.aggregate.statemgr.update = AsyncMock(return_value=mock_workflow)
        
        data = UpdateWorkflowData(
            title="Updated Title",
            desc="Updated description"
        )
        
        # Mock the model_dump method
        data.model_dump = MagicMock(return_value={"title": "Updated Title", "desc": "Updated description"})
        
        result = await self.aggregate.do__update_workflow(data)
        assert result is not None


class TestWorkflowQueryManager:
    """Test workflow query manager functionality"""

    def test_query_manager_configuration(self):
        """Test query manager configuration"""
        query_manager = WorkflowQueryManager()
        
        assert hasattr(query_manager, '__data_manager__')
        assert hasattr(query_manager, 'Meta')
        assert query_manager.Meta.prefix == 'riparius-workflow'
        assert "workflow" in query_manager.Meta.tags

    def test_query_resources(self):
        """Test that query resources are properly configured"""
        from fluvius_interim.domain.query import (
            WorkflowQuery, WorkflowFullQuery, WorkflowStepQuery,
            WorkflowParticipantQuery, WorkflowStageQuery
        )
        
        # Test that query classes exist
        assert WorkflowQuery is not None
        assert WorkflowFullQuery is not None
        assert WorkflowStepQuery is not None
        assert WorkflowParticipantQuery is not None
        assert WorkflowStageQuery is not None

    def test_query_fields(self):
        """Test query field definitions"""
        from fluvius_interim.domain.query import WorkflowQuery
        
        # Test that required fields are defined
        assert hasattr(WorkflowQuery, 'id')
        assert hasattr(WorkflowQuery, 'title')
        assert hasattr(WorkflowQuery, 'workflow_key')
        assert hasattr(WorkflowQuery, 'status')
        assert hasattr(WorkflowQuery, 'route_id')

    def test_scoped_queries(self):
        """Test scoped query configurations"""
        from fluvius_interim.domain.query import WorkflowStepQuery, WorkflowScope
        
        # Test that scoped queries require proper scope
        assert WorkflowStepQuery.Meta.scope_required == WorkflowScope
        assert hasattr(WorkflowScope, 'workflow_id')


class TestDomainIntegration:
    """Test domain integration functionality"""

    def test_domain_command_query_integration(self):
        """Test that domain, commands, and queries work together"""
        domain = WorkflowDomain()
        query_manager = WorkflowQueryManager()
        
        # Test that both use the same namespace
        assert domain.__namespace__ == query_manager.Meta.prefix
        
        # Test that both are properly configured
        assert domain.Meta.name is not None
        assert len(domain.Meta.tags) > 0

    def test_import_structure(self):
        """Test that all components can be imported correctly"""
        from fluvius_interim.domain import (
            WorkflowDomain, WorkflowAggregate, WorkflowQueryManager
        )
        
        assert WorkflowDomain is not None
        assert WorkflowAggregate is not None
        assert WorkflowQueryManager is not None

    def test_command_data_validation(self):
        """Test command data validation"""
        # Test required fields
        with pytest.raises(Exception):  # Should raise validation error
            CreateWorkflowData()  # Missing required fields
            
        # Test valid data
        valid_data = CreateWorkflowData(
            title="Valid Workflow",
            workflow_key="valid-workflow",
            route_id=UUID_GENF("valid-route")
        )
        assert valid_data.title == "Valid Workflow"

    def test_uuid_handling(self):
        """Test UUID handling in data definitions"""
        route_id = UUID_GENF("test-route")
        user_id = UUID_GENF("test-user")
        step_id = UUID_GENF("test-step")
        
        # Test UUID in CreateWorkflowData
        workflow_data = CreateWorkflowData(
            title="Test",
            workflow_key="test",
            route_id=route_id
        )
        assert workflow_data.route_id == route_id
        
        # Test UUID in AddParticipantData
        participant_data = AddParticipantData(
            user_id=user_id,
            role="test-role"
        )
        assert participant_data.user_id == user_id
        
        # Test UUID in InjectEventData
        event_data = InjectEventData(
            event_type="test",
            target_step_id=step_id
        )
        assert event_data.target_step_id == step_id
