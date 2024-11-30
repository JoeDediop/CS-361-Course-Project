import random
import zmq
import json

# ZeroMQ context
context = zmq.Context()


def main_menu():
    """
    Display the main menu and prompt the user for a choice.
    Returns the user's choice as a string.
    """
    print("\nWelcome to Joseph's Dungeon Map Generator!")
    print("Type '1' below to generate a dungeon or review the options:")
    print("1. Generate a Dungeon")
    print("2. Review Dungeon")
    print("3. Export Dungeon")
    print("4. Custom Elements Menu")
    print("Or type 'Exit' to quit the program!")

    while True:
        choice = input("Please enter your choice: ").strip().lower()
        if choice in ["1", "2", "3", "4", "Exit", "exit"]:
            return choice
        else:
            print("Invalid choice, please enter 1, 2, 3, 4, or 'Exit'.")


def generate_dungeon():
    """
    Prompts user for dungeon preferences, generates dungeon rooms and corridors,
    and displays the generated dungeon details if confirmed.
    Returns a dictionary representing the dungeon.
    """
    dungeon = None

    # Prompt user for dungeon size
    print(
        "\nTime to generate your dungeon! Input your choice from the options listed, once complete you will be prompted to confirm your choices.")
    print(" - Choose a Dungeon Size (small, medium, large):")
    print(" - Dungeon size will determine the scale of the generated map.")
    print("Tip: A larger dungeon may take longer to generate.")

    size = input("Size: ").lower()
    while size not in ["small", "medium", "large"]:
        print("Invalid input. Please enter 'small', 'medium', or 'large'.")
        size = input("Size: ").lower()

    # Prompt user for corridor complexity
    print("\nChoose Corridor Complexity (simple, realistic, complex):")
    print("Corridor complexity will determine how complex the corridors connecting rooms should be.")
    print(" - Simple corridors will connect each room once in a chain.")
    print(" - Realistic corridors will connect each room once and will connect a couple other rooms together.")
    print(" - Complex corridors will connect each room once and most rooms to each other")
    print("Tip: More complex corridors may make the dungeon more difficult to visualize")

    complexity = input("Complexity: ").lower()
    while complexity not in ["simple", "realistic", "complex"]:
        print("Invalid input. Please enter 'simple', 'realistic', or 'complex'.")
        complexity = input("Complexity: ").lower()

    # Request treasure details
    treasure = request_treasure(size)

    # NEW: Request monsters
    hazards = request_monsters_and_traps()

    # Extract monsters and traps
    monsters = hazards.get("monsters", []) if hazards else []
    traps = hazards.get("traps", []) if hazards else []

    print(f"\nCurrently, you have chosen a '{size}' sized dungeon and '{complexity}' complexity corridors.")
    if treasure:
        print(f"You chose to include {treasure['quality']} treasure.")
    else:
        print("You chose not to include treasure in your dungeon.")

    if hazards:
        difficulty = hazards['difficulty']
        monsters = hazards['hazards'].get('monsters', [])
        traps = hazards['hazards'].get('traps',[])
        print(f"You chose to include hazards of {difficulty} difficulty")
    else:
        print("You chose not to include monsters and traps in your dungeon.")

    print(
        "If this is what you want, please type 'yes' to generate the dungeon and view the contents, otherwise type "
        "'no' to enter new choices.")
    confirmation = input("Confirm? (yes or no): ").lower()
    while confirmation not in ["yes", "no"]:
        print("Invalid input. Please enter 'yes' or 'no'.")
        confirmation = input("Confirm? (yes or no): ").lower()

    # Generate dungeon based on user input
    # Generate rooms based on size
    if confirmation == 'yes':
        rooms = generate_rooms(size)  # Store the rooms in a variable
        # Generate corridors based on the rooms
        corridors = generate_corridors(rooms, complexity)
        dungeon = {
            "size": size,
            "complexity": complexity,
            "rooms": rooms,
            "corridors": corridors,
            "treasure": treasure,
            "monsters": monsters,
            "traps": traps,
        }
        print("\nDungeon generated successfully!")
        review_dungeon(dungeon)
    elif confirmation == 'no':
        generate_dungeon()

    return dungeon


def generate_rooms(size):
    room_counts = {"small": (2, 5), "medium": (4, 8), "large": (7, 12)}
    room_sizes = {
        "small": ["10x10", "15x15", "10x15", "15x20", "20x20"],
        "medium": ["15x15", "15x20", "20x20", "25x25", "25x40", "25x30"],
        "large": ["15x15", "15x20", "20x20", "25x25", "25x40", "25x30", "30x40", "40x40", "50x50", "50x60"]
    }
    num_rooms = random.randint(*room_counts[size])
    rooms = []

    grid_size = int(num_rooms**0.5) + 1
    for i in range(num_rooms):
        x = i % grid_size
        y = i // grid_size
        room = {
            "id": i + 1,
            "description": "An empty room",
            "dimensions": random.choice(room_sizes[size]),
            "position": (x, y)
        }
        rooms.append(room)

    return rooms

unique_corridors = set()

def generate_corridors(rooms, complexity):
    corridors = []
    room_count = len(rooms)

    # Connect rooms sequentially
    for i in range(room_count - 1):
        corridor = add_corridor(rooms[i]['id'], rooms[i+1]['id'])
        if corridor:
            corridors.append(corridor)

    # Add extra corridors based on complexity
    if complexity in ["realistic", "complex"]:
        extra_corridors = random.randint(1, room_count) if complexity == "realistic" or room_count == 2 else random.randint(room_count, room_count * 2)
        attempts = 0
        while len(corridors) < room_count - 1 + extra_corridors and attempts < 100:
            room_a, room_b = random.sample(rooms, 2)
            corridor = add_corridor(room_a['id'], room_b['id'], is_extra=True)
            if corridor:
                corridors.append(corridor)
            attempts += 1

    return corridors

def add_corridor(room_a, room_b, is_extra=False):
    if room_a != room_b:
        connection = tuple(sorted([room_a, room_b]))
        if connection not in unique_corridors:
            unique_corridors.add(connection)
            prefix = "Extra corridor" if is_extra else "Corridor"
            return {"description": f"{prefix} connecting Room {room_a} to Room {room_b}"}
    return None


def request_treasure(size):
    """
    Prompts the user to decide whether to generate treasure and its quality.
    Returns a dictionary with treasure details or None if skipped.
    """
    print(
        "\nWould you like to generate treasure for your dungeon? You will choose between low, medium, or high-quality "
        "treasure.")
    print(" - The amount of treasure will be determined based on the size dungeon you chose.")
    choice = input("Enter 'yes' to include treasure or 'no' to skip: ").strip().lower()

    if choice == 'yes':
        print("\nGreat! You chose to include treasure.")
        print("Please select the quality of the treasure:")
        print("1. Low quality")
        print("2. Medium quality")
        print("3. High quality")

        treasure_quality = input("Enter 1, 2, or 3: ").strip()
        while treasure_quality not in ['1', '2', '3']:
            print("Invalid choice. Please enter '1', '2', or '3'.")
            treasure_quality = input("Enter 1, 2, or 3: ").strip()

        # Map user's selection to treasure quality
        quality_map = {
            '1': 'Low quality',
            '2': 'Medium quality',
            '3': 'High quality'
        }

        # Send request to Microservice A for the selected treasure quality
        request_data = {
            "dungeon_size": size,
            "treasure_quality": quality_map[treasure_quality]
        }

        socket_server = context.socket(zmq.DEALER)
        socket_client = context.socket(zmq.DEALER)

        socket_server.bind("tcp://*:5555")
        socket_client.connect("tcp://localhost:5556")

        poller = zmq.Poller()
        poller.register(socket_server, zmq.POLLIN)

        socket_client.send_json(request_data)

        request = socket_server.recv()
        treasureRequest = json.loads(request)

        # Return the received treasure data as a dictionary
        return treasureRequest
    else:
        print("\nYou chose not to include treasure in your dungeon.")
        return None


def request_monsters_and_traps():
    """
    Requests both monsters and traps from the microservice based on the user-specified difficulty level.
    Returns a dictionary with monsters and traps or an error message.
    """

    print("\nWould you like to generate monsters and traps for your dungeon? You will choose between "
          "an easy, medium or hard difficulty for the randomly generated monsters and traps.")
    print(" - TIP: Custom traps and monsters will be included")
    choice = input("Enter 'yes' to include hazards or 'no' to skip: ").strip().lower()

    if choice == 'yes':
        # Ask the user for the difficulty level
        print("\nChoose a difficulty level for monsters and traps:")
        print("Options: easy, medium, hard")
        difficulty = input("Enter difficulty: ").strip().lower()

        if difficulty not in ["easy", "medium", "hard"]:
            print("Invalid difficulty level. Please try again.")
            return None

        # Set up ZeroMQ context and socket
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        try:
            print("\nConnecting to the Monsters and Traps microservice...")
            socket.connect("tcp://localhost:5559")  # Microservice endpoint

            # Send the request
            request_data = {"difficulty": difficulty}
            socket.send_json(request_data)

            # Wait for and process the response
            print("Waiting for monsters and traps data...")
            response = socket.recv_json()

            if "error" in response:
                print(f"Error from the microservice: {response['error']}")
                return None

            print("\nMonsters and traps received successfully!")
            return {'difficulty': difficulty, 'hazards':response}

        except zmq.ZMQError as e:
            print(f"An error occurred while communicating with the microservice: {e}")
            return None
        finally:
            socket.close()
            context.term()

    else:
        print("\nYou chose not to include hazards in your dungeon.")
        return None

def request_ascii_map(dungeon):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5558")

    layout_data = {
        "rooms": [{"id": f"room{room['id']}", "dimensions": room["dimensions"]} for room in dungeon["rooms"]],
        "corridors": [{"description": c["description"]} for c in dungeon["corridors"]]
    }

    socket.send_json(layout_data)
    ascii_map = socket.recv_string()

    socket.close()
    context.term()

    return ascii_map

def custom_element_menu():
    """Access the memnu for using the custom elements microservice"""
    print("\nHere you can add custom treasure or monsters, which can then be used during random dungeon generation!")
    print("Please choose one of the options below:")
    print("1. Add custom element")
    print("2. View custom elements")
    print("3. Return to Main Menu")

    choice = input("Enter your choice: ")

    if choice == "1":
        # Option 1: Add a custom element (monster or treasure)
        add_custom_element_to_service()
    elif choice == "2":
        # Option 2: View custom elements (monsters and treasures)
        view_custom_elements()
    elif choice == "3":
        # Option 3: Return to the main menu
        return
    else:
        print("Invalid choice. Please choose a valid option.")

def add_custom_element_to_service():
    """Add a custom element using the custom elements service."""
    # Input validation for element type
    while True:
        element_type = input("\nEnter element type ('monsters' or 'treasures'): ").strip().lower()
        if element_type not in ["monsters", "treasures"]:
            print("Invalid input. Please enter 'monsters' or 'treasures' only.")
        else:
            break

    # Input validation for name
    while True:
        name = input("Enter the name of the element (max 100 characters): ").strip()
        if len(name) > 100:
            print("Name is too long! Please enter a name with 100 characters or fewer.")
        else:
            break

    # Input validation for description
    while True:
        description = input("Enter a description of the element (max 500 characters): ").strip()
        if len(description) > 500:
            print("Description is too long! Please enter a description with 500 characters or fewer.")
        else:
            break

    request_data = {"action": "add", "type": element_type, "name": name, "description": description}
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5560")

    socket.send_json(request_data)
    response = socket.recv_json()
    print(response.get("message", response.get("error")))

def view_custom_elements():
    """Retrieve and display custom elements from the custom elements service."""
    request_data = {"action": "get"}
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5560")

    socket.send_json(request_data)
    response = socket.recv_json()

    monsters = response.get("monsters", [])
    treasures = response.get("treasures", [])

    print("\nCustom Monsters:")
    for monster in monsters:
        print(f"- {monster['name']}: {monster['description']}")

    print("\nCustom Treasures:")
    for treasure in treasures:
        print(f"- {treasure['name']}: {treasure['description']}")

def review_dungeon(dungeon):
    if not dungeon:
        print("")
        print("No dungeon has been generated yet. Select '1' below to generate a dungeon or review the other options.")
        choice = display_review_menu()
        print("")

        if choice == '1':
            generate_dungeon()
        elif choice == '2':
            export_dungeon(dungeon)
        elif choice == '3':
            return

    print("\nHere is your generated dungeon!:")
    print("Size:", dungeon["size"])
    print("Complexity:", dungeon["complexity"])
    # print(f'dungeon:', dungeon)             # TEST LINE
    # Display rooms with numbering
    print("\nRooms:")
    for index, room in enumerate(dungeon["rooms"], start=1):
        print(f" - Room {index} - {room['description']} with dimensions {room['dimensions']}")

    # Display corridors
    print("Corridors:")
    for corridor in dungeon["corridors"]:
        print(f" - {corridor['description']}")

    # Generate and display ASCII map
    ascii_map = request_ascii_map(dungeon)
    print("\nASCII Map of the Dungeon:")
    print(ascii_map)

    # Display treasure
    if dungeon.get("treasure"):
        print("\nTreasure:")
        print(f"Quality: {dungeon['treasure']['quality']}")
        if "items" in dungeon["treasure"]:
            print("Items:")
            for item in dungeon["treasure"]["items"]:
                print(f" - {item}")
        if "value" in dungeon["treasure"]:
            print(f"Total Value: {dungeon['treasure']['value']}")
    else:
        print("\nNo treasure was included in this dungeon.")

    # Display monsters and traps
    if dungeon.get("monsters") or dungeon.get("traps"):
        print("\nHazards:")
        if "monsters" in dungeon:
            print("Monsters:")
            for monster in dungeon["monsters"]:
                print(f" - {monster}")

        if "traps" in dungeon:
            print("Traps:")
            for trap in dungeon["traps"]:
                print(f" - {trap}")
    else:
        print("\nNo hazards (monsters or traps) were included in this dungeon.")

    choice = display_review_menu()

    if choice == '1':
        generate_dungeon()
    elif choice == '2':
        export_dungeon(dungeon)
    elif choice == '3':
        return


def export_dungeon(dungeon):
    if not dungeon:
        print("\nNo dungeon to export.")
        print("\nPlease select one of the options below to continue:")
        print("1. Generate a Dungeon")
        print("2. Return to Main Menu")

        while True:
            choice = input("Please enter your choice: ").lower()
            if choice in ['1', '2']:
                if choice == '1':
                    generate_dungeon()
                elif choice == '2':
                    return
                break
            else:
                print("Invalid choice, please enter 1 or 2.")

    print(
        "\nYou are about to export your dungeon, please type 'confirm' to download the dungeon or type 'back' to return to the main menu:")
    export_choice = input("Please type 'confirm' or 'back': ")

    ascii_map = request_ascii_map(dungeon)

    # Export to dungeon.txt file in local folder
    if export_choice == 'confirm':
        with open("dungeon.txt", "w") as file:
            file.write("Dungeon Layout\n")
            file.write(f"Size: {dungeon['size']}\n")
            file.write(f"Complexity: {dungeon['complexity']}\n")
            file.write("Rooms:\n")
            for room in dungeon["rooms"]:
                file.write(f" - {room['description']} with dimensions {room['dimensions']}\n")
            file.write("Corridors:\n")
            for corridor in dungeon["corridors"]:
                file.write(f" - {corridor['description']}\n")
            file.write("Map:\n")
            file.write(ascii_map)

        print("Congratulations, your dungeon has been saved to your computer as 'dungeon.txt'")

    # Return to the main menu
    elif export_choice == 'back':
        print("")
        return


def display_review_menu():
    print("\nSelect one of the options below to continue:")
    print("1. Regenerate Dungeon")
    print("2. Export Dungeon (you will be able to return to the main menu before exporting your dungeon)")
    print("3. Return to Main Menu")

    while True:
        choice = input("Please enter your choice: ").lower()
        if choice in ['1', '2', '3']:
            return choice
        else:
            print("Invalid choice, please enter 1, 2, or 3.")


# Main Program Flow
def main():
    dungeon = None
    while True:
        choice = main_menu()
        if choice == "1":
            dungeon = generate_dungeon()
        elif choice == "2":
            review_dungeon(dungeon)
        elif choice == "3":
            export_dungeon(dungeon)
        elif choice == "4":
            custom_element_menu()
        elif choice.lower() == "exit":
            print("\nAre you sure you want to exit? Your dungeon will not be saved, please export it before exiting.")
            confirm_choice = input("Type yes to confirm or no to return to select another option: ")

            if confirm_choice == 'yes':
                print("Exiting the program. Goodbye!")
                break
            elif confirm_choice == 'no':
                continue
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
