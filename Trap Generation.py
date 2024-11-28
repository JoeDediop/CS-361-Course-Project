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


def generate_monsters_and_traps(difficulty):
    """
    Generates monsters and traps based on the specified difficulty.
    """
    if difficulty not in MONSTERS_AND_TRAPS:
        return {"error": "Invalid difficulty level"}

    data = MONSTERS_AND_TRAPS[difficulty]
    monsters = random.sample(data["monsters"], k=2)
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
