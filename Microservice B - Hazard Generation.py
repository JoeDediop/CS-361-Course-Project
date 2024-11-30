import random
import zmq
import json

# Predefined data for monsters and traps
MONSTERS_AND_TRAPS = {
    "easy": {
        "monsters": ["Goblin", "Kobold", "Rat Swarm"],
        "traps": ["Tripwire", "Poison Dart", "Collapsing Ceiling"]
    },
    "medium": {
        "monsters": ["Orc", "Spider", "Werewolf"],
        "traps": ["Pitfall", "Swinging Blade", "Fire Trap"]
    },
    "hard": {
        "monsters": ["Dragon", "Lich", "Beholder"],
        "traps": ["Spike Wall", "Magic Glyph", "Teleporting Maze"]
    }
}

# Function to retrieve custom monsters from the custom elements service
def get_custom_monsters():
    """Retrieve custom monsters from the custom elements service."""
    try:
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5560")  # Custom elements service address

        # Request to get custom monsters
        request = {"action": "get"}
        socket.send_json(request)

        # Receive the response
        response = socket.recv_json()
        if "monsters" in response:
            return [monster["name"] for monster in response["monsters"]]
        else:
            return []  # Return empty if no custom monsters are found
    except Exception as e:
        print(f"Error retrieving custom monsters: {e}")
        return []

def generate_monsters_and_traps(difficulty):
    """
    Generates monsters and traps based on the specified difficulty.
    """
    if difficulty not in MONSTERS_AND_TRAPS:
        return {"error": "Invalid difficulty level"}

    data = MONSTERS_AND_TRAPS[difficulty]

    # Get custom monsters
    custom_monsters = get_custom_monsters()

    # Combine predefined monsters with custom monsters
    all_monsters = data["monsters"] + custom_monsters

    monsters = random.sample(all_monsters, k=2)
    traps = random.sample(data["traps"], k=2)

    return {"monsters": monsters, "traps": traps}


def main():
    # Set up ZeroMQ communication
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5559")

    print("Monster and Trap Generation Microservice is running...")

    while True:
        # Receive request
        message = socket.recv_json()
        difficulty = message.get("difficulty")
        print(f"Received request for difficulty: {difficulty}")

        # Generate monsters and traps
        response = generate_monsters_and_traps(difficulty)

        # Send response
        socket.send_json(response)


if __name__ == "__main__":
    main()
