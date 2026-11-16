import asyncio
from pathlib import Path

import pygame


class Ghost:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Artifact:
    def __init__(self, name, value, description):
        self.name = name
        self.value = value
        self.description = description

class Room:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.neighbors = {}
        self.ghost = None
        self.artifact = None

    def add_neighbor(self, direction, room):
        self.neighbors[direction] = room

    def get_neighbor(self, direction):
        return self.neighbors.get(direction)

    def list_exits(self):
        return ", ".join(self.neighbors.keys())

class Game:
    def __init__(self):
        bedroom = Room(
            "bedroom",
            "You awaken in a small cozy bedroom at the Sewanee Inn. You see a small desk, drawers, a locked wall safe, and a door to the bathroom."
        )
        bathroom = Room(
            "bathroom",
            "You enter a small bathroom with a countertop, sink, toilet, and shower."
        )

        bedroom.add_neighbor("bathroom", bathroom)
        bathroom.add_neighbor("bedroom", bedroom)

        bedroom.artifact = Artifact(
            "Old diary",
            100,
            "An old leather diary filled with yellowed pages and mad ramblings."
        )

        self.current_room = bedroom
        self.moves_left = 15
        self.ghost_active = False
        self.has_key = False

        self.found_bible_digit = False
        self.found_pad_digit = False
        self.found_soap_digit = False

        self.state = "command"
        self.messages = []
        self.say(self.current_room.description)
        self.say("You should look around and get ready.")

    def say(self, message):
        self.messages.append(message.strip())

    def spend_turn(self):
        if self.ghost_active:
            self.moves_left -= 1
            if self.moves_left <= 0:
                self.say("The room turns freezing cold! The ghost catches you. Game Over!")
                self.state = "lost"

    def submit(self, text):
        """Handle one submitted line and return control to Pygame."""
        choice = text.strip().lower()
        if self.state == "walk":
            self.say("YOU ESCAPED THE GHOST! YOU WIN!")
            self.state = "won"
            return
        if self.state in ("won", "lost", "quit"):
            return
        if choice == "quit":
            self.say("Goodbye!")
            self.state = "quit"
            return
        if not choice:
            return
        self.say(f"> {text.strip()}")
        if self.state == "safe":
            if choice == "cancel":
                self.say("You step away from the safe.")
            elif len(choice) != 3 or any(digit not in "0123456789" for digit in choice):
                self.say("Enter exactly three digits, or type cancel.")
                return
            elif choice == "482":
                self.say("The safe clicks open! You get the EXIT KEY!")
                self.has_key = True
            else:
                self.say("Wrong code! The safe remains locked.")
            self.state = "command"
            self.spend_turn()
            return

        if choice == "look":
            self.say(self.current_room.description)

        elif choice.startswith("go "):
            destination = choice.removeprefix("go ").strip()

            if destination in ("out", "door", "hallway", "exit"):
                if self.current_room.name != "bedroom":
                    self.say("The exit door is in the bedroom.")
                    self.spend_turn()
                    return

                self.say("You try the door handle, but it is locked shut tight!")
                self.say("Voice: 'You cannot leave this room yet...'")
                if not self.ghost_active:
                    self.ghost_active = True
                    g = Ghost("Sewanee Ghost", "A cold floating spirit.")
                    self.current_room.ghost = g
                    self.say("\nA spectral ghost suddenly appears!")
                    self.say("Ghost: 'YOU ARE TRAPPED! Find the key in the safe before time runs out!'")

            else:
                next_room = self.current_room.get_neighbor(destination)
                if next_room:
                    self.current_room = next_room
                    self.say(f"You walked into the {self.current_room.name}.")
                    self.say(self.current_room.description)
                else:
                    self.say("You can't go that way.")

        elif choice.startswith("examine "):
            item = choice.removeprefix("examine ").strip()

            if self.current_room.name == "bedroom":
                if item in ["safe", "wall safe", "locked safe"]:
                    self.say("\nYou examine the heavy metal wall safe.")
                    self.say("Dialogue: 'It requires a 3-digit key code. There must be numbers hidden somewhere in these rooms.'")

                elif item == "drawers":
                    self.say("\nYou open the drawers:")
                    self.say(f"- {self.current_room.artifact.name}: {self.current_room.artifact.description}")
                    self.say("- Newspaper: Cut off headline about mysterious disappearances.")
                    self.say("- Bible: Inside, you find a paper slip with the number '4'.")
                    self.found_bible_digit = True

                elif item == "desk":
                    self.say("\nYou check the desk:")
                    self.say("- Pen: Just an ordinary pen.")
                    self.say("- Pad of paper: Written at the top is the number '8'.")
                    self.found_pad_digit = True
                else:
                    self.say("Nothing special about that.")

            elif self.current_room.name == "bathroom":
                if item in ["counter", "countertop"]:
                    self.say("\nYou look at the counter:")
                    self.say("- Towels and tissue box.")
                    self.say("- Packaged soap: Turned over, there is a number '2' written on the back.")
                    self.found_soap_digit = True

                elif item == "shower":
                    self.say("\nInside the shower, there are just shampoo and conditioner bottles.")
                else:
                    self.say("Nothing special about that.")

        elif choice in ("open safe", "unlock safe"):
            if self.current_room.name != "bedroom":
                self.say("The wall safe is in the bedroom.")
            elif self.has_key:
                self.say("The safe is already open. You have the exit key.")
            else:
                self.say("You step up to the locked wall safe.")
                self.state = "safe"
                return

        elif choice in ("use key", "unlock door"):
            if not self.has_key:
                self.say("You don't have the key.")
            elif self.current_room.name != "bedroom":
                self.say("The exit door is in the bedroom.")
            else:
                self.say("\nYou unlock the exit door and run out into the hallway!")
                self.say("You quickly step out of the room and the door slams behind you.")
                self.say("What the heck was that? You think to yourself.")
                self.say("Your heart is still beating heavily in your chest as you take in deep gasping breaths of air.")
                self.say("You stand right outside the door waiting for your body to calm down.\n")
                self.state = "walk"
                return

        else:
            self.say("Unknown command. Try look, go bathroom, examine desk, or open safe.")

        self.spend_turn()


WIDTH, HEIGHT = 900, 590
BACKGROUND = (19, 20, 29)
PANEL = (31, 33, 46)
INK = (239, 234, 242)
MUTED = (189, 186, 204)
ACCENT = (221, 190, 249)
PROMPTS = {
    "command": "Type a command and press Enter",
    "safe": "Enter the three-digit code or type cancel",
    "walk": "Press Enter to walk down the hallway",
    "won": "You escaped! Press Enter to play again.",
    "lost": "Game over. Press Enter to try again.",
    "quit": "Game ended. Press Enter to play again.",
}
END_STATES = ("won", "lost", "quit")


def wrap_message(message, font, width):
    lines = []
    line = ""
    for word in message.split():
        candidate = f"{line} {word}".strip()
        if line and font.size(candidate)[0] > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    lines.append(line)
    return lines


def play_music():
    audio_file = Path(__file__).resolve().with_name("ghost_audio.ogg")
    if not audio_file.is_file():
        return
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(str(audio_file))
        pygame.mixer.music.play(-1)
    except pygame.error as error:
        print(f"Unable to play optional audio: {error}")


def stop_music():
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()


def draw(screen, title_font, font, small_font, game, lines, scroll, entry):
    def label(value, x, y, face=font, color=INK):
        screen.blit(face.render(value, True, color), (x, y))

    screen.fill(BACKGROUND)
    label("Sewanee Inn Game", 28, 22, title_font, ACCENT)
    status = f"Room: {game.current_room.name.title()}   |   Exits: {game.current_room.list_exits()}"
    if game.ghost_active:
        status += f"   |   Turns left: {game.moves_left}"
    if game.has_key:
        status += "   |   Exit key acquired"
    label(status, 30, 72, small_font, MUTED)

    pygame.draw.rect(screen, PANEL, (26, 106, 848, 332), border_radius=10)
    end = len(lines) - scroll
    for row, line in enumerate(lines[max(0, end - 13):end]):
        label(line, 43, 117 + row * 24, color=ACCENT if line.startswith(">") else INK)
    label("Page Up / Page Down or mouse wheel to read earlier messages", 30, 447, small_font, MUTED)

    label(PROMPTS[game.state], 30, 473, small_font, ACCENT)
    pygame.draw.rect(screen, PANEL, (26, 497, 848, 40), border_radius=8)
    label(f"> {entry}", 40, 506)
    label("Commands: look, go bathroom/bedroom/exit, examine <item>, open safe, use key, quit",
          30, 551, small_font, MUTED)
    pygame.display.flip()


async def main():
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sewanee Inn Game")
    title_font = pygame.font.Font(None, 48)
    font = pygame.font.Font(None, 25)
    small_font = pygame.font.Font(None, 22)
    pygame.key.start_text_input()

    game = Game()
    entry = ""
    scroll = 0
    lines = []
    message_count = 0
    music_started = False
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN) and not music_started:
                play_music()
                music_started = True

            if event.type == pygame.TEXTINPUT and game.state not in (*END_STATES, "walk"):
                entry = (entry + event.text)[:72]
            elif event.type == pygame.MOUSEWHEEL:
                scroll += event.y * 3
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if game.state in END_STATES:
                        game = Game()
                        lines.clear()
                        message_count = 0
                        play_music()
                    else:
                        game.submit(entry)
                        if game.state in END_STATES:
                            stop_music()
                    entry = ""
                    scroll = 0
                elif event.key == pygame.K_BACKSPACE:
                    entry = entry[:-1]
                elif event.key == pygame.K_PAGEUP:
                    scroll += 10
                elif event.key == pygame.K_PAGEDOWN:
                    scroll -= 10

        for message in game.messages[message_count:]:
            lines.extend(wrap_message(message, font, 810))
        message_count = len(game.messages)
        scroll = max(0, min(scroll, len(lines) - 13))
        draw(screen, title_font, font, small_font, game, lines, scroll, entry)
        clock.tick(60)
        await asyncio.sleep(0)

    stop_music()
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
