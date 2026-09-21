from dataclasses import dataclass
import uuid
from datetime import datetime


# Defining every single phase, observation,
# hypothesis, experiment, and artifact.


@dataclass
class Observation:
    id: str
    description: str
    source: str
    timestamp: str


@dataclass
class Hypothesis:
    id: str
    description: str
    status: str
    evidence: list[str]
    confidence: float


@dataclass
class Planning:
    id: str
    reasoning: list[str]
    steps: list[str]


@dataclass
class Experiment:
    id: str
    observation_ids: list[str]
    hypothesis_id: str
    code: str
    result: str
    status: str


@dataclass
class Artifact:
    id: str
    type: str
    name: str
    path: str
    created_by: str
    status: str
    observation_ids: list[str]
    hypothesis_ids: list[str]
    experiment_ids: list[str]


# Creating the overall state of an Exonaut project.
# This contains everything Exonaut currently knows
# about the project.


@dataclass
class ProjectState:
    project_id: str

    # The main objective Exonaut is currently working toward.
    objective: str

    # The phase Exonaut is currently in.
    current_phase: str

    # The overall state of the project.
    # Example: RUNNING, PAUSED, COMPLETE, FAILED
    status: str

    # Used to track when the project was created
    # and when its state was last changed.
    created_at: str
    updated_at: str

    # Structured information Exonaut has collected.
    observations: list[Observation]
    hypotheses: list[Hypothesis]
    experiments: list[Experiment]
    artifacts: list[Artifact]

    # Keeps track of phases that Exonaut has already completed.
    completed_phases: list[str]

    # Extra information that may become useful later.
    metadata: dict


# The StateManager will eventually be the ONLY component
# responsible for reading and writing project state.
#
# Other parts of Exonaut should interact with the
# StateManager instead of directly touching state files.


class StateManager:

    def __init__(self, workspace_path: str):
        # The location where all Exonaut projects will live.
        self.workspace_path = workspace_path


# Temporary test ID.
# Later, create_project() will generate project IDs automatically.
project_id = str(uuid.uuid4())