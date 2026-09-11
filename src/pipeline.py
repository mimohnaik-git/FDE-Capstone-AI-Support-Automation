"""Public entry point. Compatibility names share one production implementation."""

from src.orchestrator import SupportAutomationOrchestrator, SupportPipelineOrchestrator

__all__ = ["SupportAutomationOrchestrator", "SupportPipelineOrchestrator"]
