from dataclasses import dataclass 
from dataclasses import asdict
import uuid
from datetime import datetime 
from pathlib import Path
import json

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
        self.workspace_path = Path(workspace_path)

        # Create the workspace directory if it does not already exist.
        self.workspace_path.mkdir(parents=True, exist_ok=True)

    def create_project(self, objective: str):
        # We receive a unique ID per project.
        project_id = str(uuid.uuid4())

        # Build the path for this specific project.
        project_path = self.workspace_path / project_id

        # Create the project directory.
        project_path.mkdir(parents=True, exist_ok=True)

        # Create the directories that will store different types of project data.
        checkpoints_path = project_path / "checkpoints"
        artifacts_path = project_path / "artifacts"
        generated_path = project_path / "generated"
        data_path = project_path / "data"

        # Create each directory.
        checkpoints_path.mkdir(parents=True, exist_ok=True)
        artifacts_path.mkdir(parents=True, exist_ok=True)
        generated_path.mkdir(parents=True, exist_ok=True)
        data_path.mkdir(parents=True, exist_ok=True)

        # Track when the project was created.
        created_at = datetime.now().isoformat()

        # A newly created project was just updated,
        # so both timestamps start out the same.
        updated_at = created_at

        # The project begins in the initialization phase.
        current_phase = "initialization"

        # The project is active when it is first created.
        status = "RUNNING"

        # A new project has not collected anything yet.
        observations = []
        hypotheses = []
        experiments = []
        artifacts = []

        # No phases have been completed yet.
        completed_phases = []

        # Extra project information can be stored here later.
        metadata = {}

        # Create the initial state of the project.
        state = ProjectState(
            project_id,
            objective,
            current_phase,
            status,
            created_at,
            updated_at,
            observations,
            hypotheses,
            experiments,
            artifacts,
            completed_phases,
            metadata
        )

        # Save the initial state to disk.
        self.save_state(project_path, state)

        # Return the location of the new project
        # and its initial state.
        return project_path, state

    def save_state(self, project_path, state):

        # Convert the ProjectState dataclass into a dictionary.
        state_dict = asdict(state)

        # Build the path where the state will be stored.
        state_path = project_path / "state.json"

        # Open the state file for writing.
        with open(state_path, "w") as file:

            # Convert the dictionary into JSON and write it to the file.
            json.dump(state_dict, file, indent=4)

    def load_state(self, project_path):
        # Build the path to the saved state.
        state_path = project_path / "state.json"

        # Open the saved state for reading.
        with open(state_path, "r") as file:
            # Convert the JSON file back into a Python dictionary.
            state_dict = json.load(file)

        # Reconstruct the ProjectState object.
        state = ProjectState(**state_dict)

        # Return the loaded state.
        return state


manager = StateManager("workspace/projects")

project_path, state = manager.create_project(
    "Analyze airline disruption propagation"
)

loaded_state = manager.load_state(project_path)

print("Original state:")
print(state)

print("\nLoaded state:")
print(loaded_state)