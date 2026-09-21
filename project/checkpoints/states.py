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
        self.save_text_mirrors(project_path, state)

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

    def save_text_mirrors(self, project_path, state):

        # Save the project objective.
        objective_path = project_path / "objective.txt"

        with open(objective_path, "w") as file:
            file.write(state.objective)


        # Save observations.
        observations_path = project_path / "observations.txt"

        with open(observations_path, "w") as file:

            for observation in state.observations:
                file.write(
                    f"[{observation.timestamp}] "
                    f"{observation.description}\n"
                )


        # Save hypotheses.
        hypotheses_path = project_path / "hypotheses.txt"

        with open(hypotheses_path, "w") as file:

            for hypothesis in state.hypotheses:
                file.write(
                    f"{hypothesis.description}\n"
                    f"Status: {hypothesis.status}\n"
                    f"Confidence: {hypothesis.confidence}\n\n"
                )


        # Save experiments.
        experiments_path = project_path / "experiments.txt"

        with open(experiments_path, "w") as file:

            for experiment in state.experiments:
                file.write(
                    f"Experiment: {experiment.id}\n"
                    f"Status: {experiment.status}\n"
                    f"Result: {experiment.result}\n\n"
                )


        # Save artifacts.
        artifacts_path = project_path / "artifacts.txt"

        with open(artifacts_path, "w") as file:

            for artifact in state.artifacts:
                file.write(
                    f"Artifact: {artifact.name}\n"
                    f"Type: {artifact.type}\n"
                    f"Path: {artifact.path}\n"
                    f"Status: {artifact.status}\n\n"
                )
    def create_checkpoint(self, project_path, state):

        # Find the checkpoint directory for this project.
        checkpoints_path = project_path / "checkpoints"

        # Find all existing checkpoint files.
        existing_checkpoints = list(
            checkpoints_path.glob("checkpoint_*.json")
        )

        # Create the number for the new checkpoint.
        checkpoint_number = len(existing_checkpoints) + 1

        # Build the filename for this checkpoint.
        checkpoint_filename = (
            f"checkpoint_{checkpoint_number:03d}.json"
        )

        # Build the complete path for the checkpoint.
        checkpoint_path = checkpoints_path / checkpoint_filename

        # Convert the current state into a dictionary.
        state_dict = asdict(state)

        # Save the state as a historical snapshot.
        with open(checkpoint_path, "w") as file:
            json.dump(state_dict, file, indent=4)

        # Return the checkpoint path.
        return checkpoint_path
    def add_observation(self, project_path, state, description, source):

        # Create a unique ID for the observation.
        observation_id = str(uuid.uuid4())

        # Record when the observation was created.
        timestamp = datetime.now().isoformat()

        # Create the observation object.
        observation = Observation(
            id=observation_id,
            description=description,
            source=source,
            timestamp=timestamp
        )

        # Add the observation to the current state.
        state.observations.append(observation)

        # Update the time the project state was changed.
        state.updated_at = timestamp

        # Save the updated state.
        self.save_state(project_path, state)

        # Update the human-readable state files.
        self.save_text_mirrors(project_path, state)

        # Return the new observation.
        return observation
    def add_hypothesis(
        self,
        project_path,
        state,
        description,
        status="ACTIVE",
        evidence=None,
        confidence=0.0
    ):

        # Create a unique ID for the hypothesis.
        hypothesis_id = str(uuid.uuid4())

        # Create an empty evidence list if none was provided.
        if evidence is None:
            evidence = []

        # Create the hypothesis object.
        hypothesis = Hypothesis(
            id=hypothesis_id,
            description=description,
            status=status,
            evidence=evidence,
            confidence=confidence
        )

        # Add the hypothesis to the current state.
        state.hypotheses.append(hypothesis)

        # Record when the state changed.
        state.updated_at = datetime.now().isoformat()

        # Save the updated state.
        self.save_state(project_path, state)

        # Update the human-readable state files.
        self.save_text_mirrors(project_path, state)

        # Return the new hypothesis.
        return hypothesis
    def add_experiment(
        self,
        project_path,
        state,
        observation_ids,
        hypothesis_id,
        code,
        result,
        status="COMPLETED"
    ):

        # Create a unique ID for the experiment.
        experiment_id = str(uuid.uuid4())

        # Create the experiment object.
        experiment = Experiment(
            id=experiment_id,
            observation_ids=observation_ids,
            hypothesis_id=hypothesis_id,
            code=code,
            result=result,
            status=status
        )

        # Add the experiment to the current state.
        state.experiments.append(experiment)

        # Record when the state changed.
        state.updated_at = datetime.now().isoformat()

        # Save the updated state.
        self.save_state(project_path, state)

        # Update the human-readable state files.
        self.save_text_mirrors(project_path, state)

        # Return the new experiment.
        return experiment 
    def add_artifact(
        self,
        project_path,
        state,
        artifact_type,
        name,
        path,
        created_by,
        status="CREATED",
        observation_ids=None,
        hypothesis_ids=None,
        experiment_ids=None
    ):

        # Create an empty list when no relationships were provided.
        if observation_ids is None:
            observation_ids = []

        if hypothesis_ids is None:
            hypothesis_ids = []

        if experiment_ids is None:
            experiment_ids = []

        # Create a unique ID for the artifact.
        artifact_id = str(uuid.uuid4())

        # Create the artifact object.
        artifact = Artifact(
            id=artifact_id,
            type=artifact_type,
            name=name,
            path=path,
            created_by=created_by,
            status=status,
            observation_ids=observation_ids,
            hypothesis_ids=hypothesis_ids,
            experiment_ids=experiment_ids
        )

        # Add the artifact to the current state.
        state.artifacts.append(artifact)

        # Record when the state changed.
        state.updated_at = datetime.now().isoformat()

        # Save the updated state.
        self.save_state(project_path, state)

        # Update the human-readable state files.
        self.save_text_mirrors(project_path, state)

        # Return the new artifact.
        return artifact
    def update_phase(self, project_path, state, new_phase):

        # Record the current phase before changing it.
        previous_phase = state.current_phase

        # Add the previous phase to the completed phases.
        if previous_phase not in state.completed_phases:
            state.completed_phases.append(previous_phase)

        # Move the project into the new phase.
        state.current_phase = new_phase

        # Record when the state changed.
        state.updated_at = datetime.now().isoformat()

        # Save the updated state.
        self.save_state(project_path, state)

        # Update the human-readable state files.
        self.save_text_mirrors(project_path, state)

        # Return the updated state.
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

checkpoint_path = manager.create_checkpoint(
    project_path,
    state
)

print("\nCheckpoint:")
print(checkpoint_path)