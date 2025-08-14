"""Comprehensive test suite for the fluvius_interim workflow management system."""

import pytest
from types import SimpleNamespace

from fluvius_interim.engine.workflow import Workflow, Step, Stage, Role, transition, ALL_STATES
from fluvius_interim.status import WorkflowStatus, StepStatus
from fluvius_interim.engine.exceptions import WorkflowExecutionError, WorkflowConfigurationError
from fluvius_interim.engine.datadef import WorkflowState, WorkflowStep, validate_labels
from fluvius_interim.engine.router import st_connect, wf_connect, ActivityRouter
from fluvius_interim.engine.manager import WorkflowManager
from fluvius.data import UUID_GENF


class TestFluviusInterimWorkflowSystem:
    """Comprehensive test suite for the fluvius_interim workflow management system"""

    def setup_method(self):
        """Set up test fixtures"""
        # Clear registries before each test
        WorkflowManager.__registry__ = {}
        ActivityRouter.ROUTING_TABLE = {}

    def test_workflow_registration_and_key_generation(self):
        """Test workflow registration with automatic key generation"""
        class TestWorkflow(Workflow, title='Test Workflow', revision=1):
            stage = Stage('Test Stage')
            
            class TestStep(Step, title='Test Step', stage=stage):
                pass
                
        # Verify workflow is registered with kebab-case key
        assert 'test-workflow' in WorkflowManager.__registry__
        
        # Verify workflow metadata
        assert TestWorkflow.__title__ == 'Test Workflow'
        assert TestWorkflow.__revision__ == 1
        # The actual key is kebab-case
        assert TestWorkflow.__key__ == 'test-workflow'

    def test_custom_workflow_key(self):
        """Test workflow with custom key"""
        class CustomWorkflow(Workflow, title='Custom Workflow', revision=1):
            __key__ = 'my_custom_key'
            stage = Stage('Custom Stage')
            
            class CustomStep(Step, title='Custom Step', stage=stage):
                pass
                
        # Custom key should be preserved
        assert CustomWorkflow.__key__ == 'my_custom_key'
        assert 'my_custom_key' in WorkflowManager.__registry__

    def test_step_state_machine(self):
        """Test step state machine with transitions"""
        stage = Stage('State Stage')
        
        class StateStep(Step, title='State Step', stage=stage):
            __states__ = ('CREATED', 'PROCESSING', 'COMPLETED', 'FAILED')
            __start__ = 'CREATED'
            
            @transition('PROCESSING', allowed_states=('CREATED',))
            def start_processing(self):
                return {'message': 'Started'}
                
            @transition('COMPLETED', allowed_states=('PROCESSING',))
            def complete_processing(self):
                return {'message': 'Completed'}
                
        assert StateStep.__states__ == ('CREATED', 'PROCESSING', 'COMPLETED', 'FAILED')
        assert StateStep.__start__ == 'CREATED'
        assert len(StateStep.__transitions__) == 2

    def test_event_routing(self):
        """Test event routing registration"""
        class EventWorkflow(Workflow, title='Event Workflow', revision=1):
            stage = Stage('Event Stage')
            
            @wf_connect('workflow-event')
            def handle_workflow_event(wf_state, event):
                yield f"Workflow handled: {event.data}"
                
            class EventStep(Step, title='Event Step', stage=stage):
                @st_connect('step-event')
                def handle_step_event(step_state, event):
                    yield f"Step handled: {event.data}"
                    
        assert 'workflow-event' in ActivityRouter.ROUTING_TABLE
        assert 'step-event' in ActivityRouter.ROUTING_TABLE

    def test_data_structures(self):
        """Test data structure creation and immutability"""
        wf_state = WorkflowState(
            state='test_state',
            label='TEST_LABEL',
            status=WorkflowStatus.ACTIVE
        )
        
        assert wf_state.state == 'test_state'
        assert wf_state.status == WorkflowStatus.ACTIVE
        
        # Test immutability
        updated = wf_state.set(status=WorkflowStatus.COMPLETED)
        assert wf_state.status == WorkflowStatus.ACTIVE
        assert updated.status == WorkflowStatus.COMPLETED

    def test_label_validation(self):
        """Test label validation"""
        result = validate_labels('CREATED', 'PROCESSING', 'COMPLETED')
        assert result == ('CREATED', 'PROCESSING', 'COMPLETED')
        
        with pytest.raises(ValueError):
            validate_labels('invalid_label')

    def test_status_categories(self):
        """Test status categorization"""
        assert WorkflowStatus.ACTIVE in WorkflowStatus._ACTIVE
        assert WorkflowStatus.BLANK in WorkflowStatus._INACTIVE
        assert WorkflowStatus.COMPLETED in WorkflowStatus._FINISHED
        
        assert StepStatus.COMPLETED in StepStatus._FINISHED
        assert StepStatus.ACTIVE not in StepStatus._FINISHED

    def test_workflow_validation_errors(self):
        """Test workflow configuration validation"""
        stage = Stage('Validation Stage')
        
        # Test transition to non-existent state
        with pytest.raises(WorkflowConfigurationError):
            class InvalidStep(Step, title='Invalid Step', stage=stage):
                @transition('NONEXISTENT')
                def invalid_transition(self):
                    pass

    def test_manager_functionality(self):
        """Test WorkflowManager basic functionality"""
        class ManagerWorkflow(Workflow, title='Manager Workflow', revision=1):
            stage = Stage('Manager Stage')
            
            class ManagerStep(Step, title='Manager Step', stage=stage):
                pass
                
        manager = WorkflowManager()
        assert 'manager-workflow' in WorkflowManager.__registry__
        assert hasattr(manager, 'process_event')

    def test_role_and_stage_definitions(self):
        """Test role and stage components"""
        stage = Stage('Test Stage', order=1)
        role = Role('Test Role')
        
        assert stage.__title__ == 'Test Stage'
        assert stage.__order__ == 1
        assert role.__title__ == 'Test Role'

    def test_multi_instance_steps(self):
        """Test multi-instance step configuration"""
        stage = Stage('Multi Stage')
        
        class SingleStep(Step, title='Single Step', stage=stage):
            pass
            
        class MultiStep(Step, title='Multi Step', stage=stage, multi=True):
            pass
            
        assert SingleStep.__multi__ == False
        assert MultiStep.__multi__ == True

    def test_all_states_transition(self):
        """Test transitions allowed from all states"""
        stage = Stage('Emergency Stage')
        
        class EmergencyStep(Step, title='Emergency Step', stage=stage):
            __states__ = ('CREATED', 'PROCESSING', 'EMERGENCY')
            
            @transition('EMERGENCY', allowed_states=(ALL_STATES,))
            def emergency_stop(self):
                return {'message': 'Emergency'}
                
        allowed_states, _ = EmergencyStep.__transitions__['EMERGENCY']
        assert allowed_states == (ALL_STATES,)

    def test_workflow_metadata_attributes(self):
        """Test workflow metadata and attributes"""
        class MetadataWorkflow(Workflow, title='Metadata Test', revision=2):
            __description__ = 'Test workflow with metadata'
            stage = Stage('Meta Stage')
            
            class MetaStep(Step, title='Meta Step', stage=stage):
                __description__ = 'Test step with metadata'
                pass
                
        assert MetadataWorkflow.__title__ == 'Metadata Test'
        assert MetadataWorkflow.__revision__ == 2
        assert MetadataWorkflow.__description__ == 'Test workflow with metadata'
        assert MetadataWorkflow.MetaStep.__description__ == 'Test step with metadata'

    def test_stage_ordering(self):
        """Test stage ordering functionality"""
        stage1 = Stage('First Stage', order=1)
        stage2 = Stage('Second Stage', order=2)
        stage3 = Stage('Third Stage', order=3)
        
        stages = [stage2, stage1, stage3]
        sorted_stages = sorted(stages, key=lambda s: s.__order__)
        
        assert sorted_stages[0] == stage1
        assert sorted_stages[1] == stage2
        assert sorted_stages[2] == stage3

    def test_complex_state_transitions(self):
        """Test complex state transition scenarios"""
        stage = Stage('Complex Stage')
        
        class ComplexStep(Step, title='Complex Step', stage=stage):
            __states__ = ('CREATED', 'PROCESSING', 'REVIEW', 'APPROVED', 'REJECTED', 'COMPLETED')
            __start__ = 'CREATED'
            
            @transition('PROCESSING', allowed_states=('CREATED', 'REVIEW'))
            def start_processing(self):
                return {'action': 'processing_started'}
                
            @transition('REVIEW', allowed_states=('PROCESSING',))
            def submit_for_review(self):
                return {'action': 'submitted_for_review'}
                
            @transition('APPROVED', allowed_states=('REVIEW',))
            def approve(self):
                return {'action': 'approved'}
                
            @transition('REJECTED', allowed_states=('REVIEW',))
            def reject(self):
                return {'action': 'rejected'}
                
            @transition('COMPLETED', allowed_states=('APPROVED',))
            def complete(self):
                return {'action': 'completed'}
                
        assert len(ComplexStep.__transitions__) == 5
        assert ComplexStep.__start__ == 'CREATED'

    def test_comprehensive_workflow_scenario(self):
        """Test a complete workflow scenario with multiple components"""
        class CompleteWorkflow(Workflow, title='Complete Workflow', revision=1):
            init_stage = Stage('Initialization', order=1)
            proc_stage = Stage('Processing', order=2)
            final_stage = Stage('Finalization', order=3)
            
            admin_role = Role('Administrator')
            user_role = Role('User')
            
            @wf_connect('workflow-start')
            def handle_start(wf_state, event):
                yield f"Started: {event.data}"
                
            @wf_connect('workflow-complete')
            def handle_complete(wf_state, event):
                yield f"Completed: {event.data}"
                
            class InitStep(Step, title='Init Step', stage=init_stage):
                __states__ = ('CREATED', 'INITIALIZING', 'COMPLETED')
                
                @st_connect('init-event')
                def handle_init(step_state, event):
                    yield f"Init: {event.data}"
                    
                @transition('INITIALIZING')
                def start_init(self):
                    return {'message': 'Started initialization'}
                    
                @transition('COMPLETED', allowed_states=('INITIALIZING',))
                def complete_init(self):
                    return {'message': 'Completed initialization'}
                    
            class ProcessStep(Step, title='Process Step', stage=proc_stage, multi=True):
                __states__ = ('CREATED', 'PROCESSING', 'COMPLETED')
                
                @transition('PROCESSING')
                def start_processing(self):
                    return {'message': 'Started processing'}
                    
                @transition('COMPLETED', allowed_states=('PROCESSING',))
                def complete_processing(self):
                    return {'message': 'Completed processing'}
                    
            class FinalStep(Step, title='Final Step', stage=final_stage):
                pass
                
        # Verify registration and configuration
        assert 'complete-workflow' in WorkflowManager.__registry__
        assert CompleteWorkflow.__title__ == 'Complete Workflow'
        assert CompleteWorkflow.InitStep.__states__ == ('CREATED', 'INITIALIZING', 'COMPLETED')
        assert CompleteWorkflow.ProcessStep.__multi__ == True
        
        # Verify event registration
        assert 'workflow-start' in ActivityRouter.ROUTING_TABLE
        assert 'workflow-complete' in ActivityRouter.ROUTING_TABLE
        assert 'init-event' in ActivityRouter.ROUTING_TABLE
        
        # Verify transitions
        assert len(CompleteWorkflow.InitStep.__transitions__) == 2
        assert len(CompleteWorkflow.ProcessStep.__transitions__) == 2
        
        # Verify stages
        stages = [CompleteWorkflow.init_stage, CompleteWorkflow.proc_stage, CompleteWorkflow.final_stage]
        assert len(stages) == 3
        
        # Verify roles
        assert CompleteWorkflow.admin_role.__title__ == 'Administrator'
        assert CompleteWorkflow.user_role.__title__ == 'User'

    def test_workflow_inheritance(self):
        """Test workflow inheritance patterns"""
        class BaseWorkflow(Workflow, title='Base Workflow', revision=1):
            base_stage = Stage('Base Stage')
            
            class BaseStep(Step, title='Base Step', stage=base_stage):
                pass
                
        class ExtendedWorkflow(BaseWorkflow, title='Extended Workflow', revision=1):
            extended_stage = Stage('Extended Stage')
            
            class ExtendedStep(Step, title='Extended Step', stage=extended_stage):
                pass
                
        # Both workflows should be registered
        assert 'base-workflow' in WorkflowManager.__registry__
        assert 'extended-workflow' in WorkflowManager.__registry__
        
        # Extended workflow should have access to base components
        assert hasattr(ExtendedWorkflow, 'base_stage')
        assert hasattr(ExtendedWorkflow, 'BaseStep')
        assert hasattr(ExtendedWorkflow, 'extended_stage')
        assert hasattr(ExtendedWorkflow, 'ExtendedStep')

    def test_error_handling_scenarios(self):
        """Test various error handling scenarios"""
        stage = Stage('Error Stage')
        
        # Test invalid state definition
        with pytest.raises((WorkflowConfigurationError, ValueError)):
            class InvalidStateStep(Step, title='Invalid State Step', stage=stage):
                __states__ = ('CREATED', 'created')  # Duplicate states (case-insensitive)
                
        # Test invalid transition
        with pytest.raises(WorkflowConfigurationError):
            class InvalidTransitionStep(Step, title='Invalid Transition Step', stage=stage):
                __states__ = ('CREATED', 'PROCESSING')
                
                @transition('NONEXISTENT')  # State doesn't exist
                def invalid_transition(self):
                    pass

    def test_step_naming_conventions(self):
        """Test step naming and title conventions"""
        stage = Stage('Naming Stage')
        
        class AutoNameStep(Step, stage=stage):
            """Step with automatic naming"""
            pass
            
        class CustomNameStep(Step, title='Custom Named Step', stage=stage):
            """Step with custom title"""
            pass
            
        class ExplicitNameStep(Step, name='explicit-name', stage=stage):
            """Step with explicit name"""
            pass
            
        # Verify naming conventions are applied
        assert hasattr(AutoNameStep, '__title__')
        assert CustomNameStep.__title__ == 'Custom Named Step'
        # Additional naming tests would depend on implementation details
