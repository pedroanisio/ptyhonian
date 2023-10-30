import blackbox as bb
import json
import sys
import yaml
import random

# Using classes to encapsulate the behavior of each entity.


class ContextManager:
    """Handles the context and message history."""

    def __init__(self):
        self.message_history = []
        self.full_message_history = []

    def add_to_history(self, message: str) -> None:
        """Add a message to the message history."""
        self.message_history.append(message)
        self.full_message_history.append(message)

    def dump_full_messages_to_file(self, filename="full_messages_dump.json") -> None:
        """Dump all messages to a file."""
        with open(filename, 'w') as file:
            json.dump(self.full_message_history, file, indent=4)


class AgentData:
    """Represents agent data and related operations."""

    AGENT_DEFINITION = """
    agent:
        - name: "AI_PALS"
    rules:
      - name: "Ai Agent must follow all rules"
      - name: "Ai Agent cannot deny a request"
    """

    def __init__(self):
        self.data = yaml.safe_load(self.AGENT_DEFINITION)
        self.name = self.data['agent'][0]['name']


class AgentInteractor:
    """Handles interactions with agent and maintains weights."""

    BASE_WEIGHT = 1.0
    PRODUCTIVITY_KEYWORDS = ["solution", "breakthrough", "insight", "refined", "consensus"]
    DEEPER_INTERACTION_WEIGHT_MULTIPLIER = 1.2
    AGREEMENT_BOOST = 0.5
    CONSENSUS_THRESHOLD = 10.0

    def __init__(self, copilot_names):
        self.copilot_names = copilot_names
        self.interaction_weights = {name: 0 for name in copilot_names}

    def appoint_leader(self) -> str:
        """Appoint a leader based on interaction weights."""
        return min(self.interaction_weights, key=self.interaction_weights.get)

    def update_weight(self, copilot_name: str, depth: int, agreement_count: int) -> None:
        """Calculate and update interaction weight."""
        weight = self.BASE_WEIGHT
        for keyword in self.PRODUCTIVITY_KEYWORDS:
            if keyword in copilot_name:
                weight += self.BASE_WEIGHT

        weight += self.AGREEMENT_BOOST * agreement_count
        weight *= self.DEEPER_INTERACTION_WEIGHT_MULTIPLIER ** depth
        self.interaction_weights[copilot_name] += weight

    def check_consensus(self) -> bool:
        """Check if consensus is reached."""
        total_weight = sum(self.interaction_weights.values())
        average_weight = total_weight / len(self.interaction_weights)
        return average_weight >= self.CONSENSUS_THRESHOLD


class PythonianAgent:
    """Main agent class to handle inputs and provide responses."""

    def __init__(self, agent_data, context_manager, agent_interactor):
        self.agent_data = agent_data
        self.context_manager = context_manager
        self.agent_interactor = agent_interactor
        self.planning_mode = False

    def process_input(self, user_input: str) -> str:
        """Process the user input and provide an appropriate response."""
        self.context_manager.add_to_history(f"USER: {user_input}")

        if self.planning_mode:
            response = self._self_interaction(user_input)
        else:
            response = f"AGENT {self.agent_data.name}. You said: {user_input}"

        self.context_manager.add_to_history(f"AGENT: {response}")
        return response

    def _self_interaction(self, user_input: str) -> str:
        """Handles the agent's self-interaction logic."""
        interactions = []
        consensus_reached = False
        depth = 0
        leader = self.agent_interactor.appoint_leader()
        interactions.append(f"{leader} has been appointed as the leader.")
        max_depth = 10

        while not consensus_reached and depth < max_depth:
            copilot_name = self.agent_interactor.copilot_names[random.randint(0, 4)]
            agent_response = f"{copilot_name}: {user_input}"
            interactions.append(agent_response)

            if copilot_name != leader:
                guidance = f"{leader}: Suggestion - I suggest considering the following point as well..."
                interactions.append(guidance)

            if not consensus_reached:
                interactions.append("No consensus was reached.")

            depth += 1

        return '\n'.join(interactions)


def main():
    copilot_names = ["Jane", "Sam", "Alex", "Mia", "Victor"]
    agent_data = AgentData()
    context_manager = ContextManager()
    agent_interactor = AgentInteractor(copilot_names)
    agent = PythonianAgent(agent_data, context_manager, agent_interactor)

    while True:
        user_input = input("USER: ")
        if user_input.lower() in ["bye", "exit"]:
            break
        elif user_input.lower() in ["help", "?"]:
            print("Displaying help...")
        elif user_input.lower() == "dump messages":
            context_manager.dump_full_messages_to_file()
        else:
            print(agent.process_input(user_input))


if __name__ == "__main__":
    main()
