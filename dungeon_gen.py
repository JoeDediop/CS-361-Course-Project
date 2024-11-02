import random

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
    print("Or type 'Exit' to quit the program!")

    while True:
        choice = input("Please enter your choice: ").strip().lower()
        if choice in ["1", "2", "3", "Exit", "exit"]:
            return choice
        else:
            print("Invalid choice, please enter 1, 2, 3, or 'Exit'.")

def generate_dungeon():
    """
    Prompts user for dungeon preferences, generates dungeon rooms and corridors,
    and displays the generated dungeon details if confirmed.
    Returns a dictionary representing the dungeon.
    """
    dungeon = None
    # Prompt user for dungeon size
    print("")
    print("Time to generate your dungeon! Input your choice from the options listed, once complete you will be prompted to confirm your choices.")
    print(" - Choose a Dungeon Size (small, medium, large):")
    print(" - Dungeon size will determine the scale of the generated map.")
    print("Tip: A larger dungeon may take longer to generate.")

    size = input("Size: ").lower()
    while size not in ["small", "medium", "large"]:
        print("Invalid input. Please enter 'small', 'medium', or 'large'.")
        size = input("Size: ").lower()

    # Prompt user for corridor complexity
    print("")
    print("Choose Corridor Complexity (simple, realistic, complex):")
    print("Corridor complexity will determine how complex the corridors connecting rooms should be.")
    print(" - Simple corridors will connect each room once in a chain.")
    print(" - Realistic corridors will connect each room once and will connect a couple other rooms together.")
    print(" - Complex corridors will connect each room once and most rooms to each other")
    print("Tip: More complex corridors may make the dungeon more difficult to visualize")

    complexity = input("Complexity: ").lower()
    while complexity not in ["simple", "realistic", "complex"]:
        print("Invalid input. Please enter 'simple', 'realistic', or 'complex'.")
        complexity = input("Complexity: ").lower()

    print(f"\nCurrently, you have chosen a '{size}' sized dungeon and '{complexity}' complexity corridors.")
    print("If this is what you want, please type 'yes' to generate the dungeon and view the contents, otherwise type 'no' to enter new choices.")
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
            "corridors": corridors
        }
        print("\nDungeon generated successfully!")
        review_dungeon(dungeon)
    elif confirmation == 'no':
        generate_dungeon()

    return dungeon

def generate_rooms(size):
    """
    Generates a list of rooms based on the specified dungeon size.
    Returns a list of room dictionaries, each with a description and dimensions.
    """
    room_counts = {"small": (2, 5), "medium": (4, 8), "large": (7, 12)}
    room_sizes = {
        "small": ["10x10", "15x15", "10x15", "15x20", "20x20"],
        "medium": ["15x15", "15x20", "20x20", "25x25", "25x40", "25x30"],
        "large": ["15x15", "15x20", "20x20", "25x25", "25x40", "25x30", "30x40", "40x40", "50x50", "50x60"]
    }

    num_rooms = random.randint(*room_counts[size])
    room_sizes_available = room_sizes[size]

    rooms = [{"description": "An empty room", "dimensions": random.choice(room_sizes_available)} for _ in range(num_rooms)]
    return rooms

def generate_corridors(rooms, complexity):
    """
    Generates corridors connecting rooms based on the specified complexity level.
    Returns a list of corridor dictionaries.
    """
    corridors = []
    room_count = len(rooms)

    # Add base connections
    for i in range(room_count - 1):
        corridors.append({"description": f"Corridor connecting Room {i+1} to Room {i+2}"})

    if complexity == "realistic" or complexity == "complex":
        additional_corridors = random.randint(1, room_count // 2) if complexity == "realistic" else random.randint(room_count // 2, room_count)
        for _ in range(additional_corridors):
            room_a, room_b = random.sample(range(room_count), 2)
            corridors.append({"description": f"Extra corridor connecting Room {room_a+1} to Room {room_b+1}"})

    return corridors

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

    # Display rooms with numbering
    print("\nRooms:")
    for index, room in enumerate(dungeon["rooms"], start=1):
        print(f" - Room {index} - {room['description']} with dimensions {room['dimensions']}")

    # Display corridors
    print("Corridors:")
    for corridor in dungeon["corridors"]:
        print(f" - {corridor['description']}")
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

    print("\nYou are about to export your dungeon, please type 'confirm' to download the dungeon or type 'back' to return to the main menu:")
    export_choice = input("Please type 'confirm' or 'back': ")

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
        print("Congratulations, your dungeon has been saved to your computer as 'dungeon.txt'")

    # Return to the main menu
    elif export_choice == 'back':
        print("")
        return

def display_review_menu():
    print("\nSelect one of the options below to continue:")
    print("1. Regenerate Dungeon")
    print("2. Export Dungeon")
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
