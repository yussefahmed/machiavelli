import json
import time
from diplomacy import Game
from diplomacy.utils.export import to_saved_game_format
import ollama

#import agent class (machiavelli) directly next time 
class Agent:
    def __init__(self, name: str, model: str = "qwen2.5:3b", personality: str = None):
        self.name: str = name
        self.model: str = model
        self.personality: str = personality
        self.conversation_history: list[dict[str, str]] = []
        if personality:
            system_message = {"role": "system", "content": f"You are {name} with a {personality}"}
            self.conversation_history.append(system_message)

    def respond_to(self, message_content: str, from_name: str) -> str:
        user_message = {"role": "user", "content": f"{from_name}: {message_content}"}
        self.conversation_history.append(user_message)
        try:
            response = ollama.chat(
                model=self.model,
                messages=self.conversation_history,
                options={"temperature": 0.7}
            )
            response_content = response["message"]["content"]
            assistant_message = {"role": "assistant", "content": response_content}
            self.conversation_history.append(assistant_message)
            return response_content
        except Exception as e:
            print(f"Error: {self.name} failed to respond: {e}")
            return f"[Error: {self.name} couldn't generate a response]"


def build_game_prompt(game: Game, power_name: str) -> str:
    state = game.get_state()
    messages = dict(game.messages) if game.messages else {}
    prompt = (
        f"Game State:\n{json.dumps(state, indent=2)}\n\n"
        f"Message History:\n{json.dumps(messages, indent=2)}\n\n"
        f"You are playing as {power_name} in a game of Diplomacy. "
        "Based on the above state and recent messages, decide your orders for this phase "
        "and, if appropriate, include a message for the other players. "
        "Return your response in JSON format with exactly two keys: 'orders' (a list) and 'message' (a string)."
    )
    return prompt   
     


    
    


def main():
    MAX_DURATION = 180  # GAME TAKES TOO LONG SO STOP AT 3 MINS AND FORCE A DRAW 
    start_time = time.time()
    
    # Initialize the game
    game = Game()
    game.controlled_powers = ["FRANCE", "ENGLAND"]

    # Create two agents
    agent_france = Agent(name="FRANCE", personality="strategic and diplomatic")
    agent_england = Agent(name="ENGLAND", personality="cautious and pragmatic")
    agents = {"FRANCE": agent_france, "ENGLAND": agent_england}

    phase_counter = 0
    while not game.is_game_done:
        
        if time.time() - start_time > MAX_DURATION:
            print("Maximum simulation time reached; forcing a draw.")
            game.draw()
            break

        print(f"\n--- Processing Phase {phase_counter}: {game.phase} ---")
        for power_name in game.controlled_powers:
            prompt = build_game_prompt(game, power_name)
            print(f"\nPrompt for {power_name}:\n{prompt}\n")
            response_text = agents[power_name].respond_to(prompt, "GameState")
            print(f"Raw response from {power_name}:\n{response_text}\n")
            try:
                response_data = json.loads(response_text)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {power_name}'s response. Skipping orders.")
                continue

            orders = response_data.get("orders", [])
            msg_text = response_data.get("message", "")
            print(f"{power_name} orders: {orders}")
            print(f"{power_name} message: {msg_text}")

            try:
                game.set_orders(power_name, orders)
            except Exception as e:
                print(f"Error setting orders for {power_name}: {e}")
            if msg_text.strip():
                try:
                    message_obj = game.new_power_message(recipient="GLOBAL", body=msg_text)
                    game.add_message(message_obj)
                except Exception as e:
                    print(f"Error adding message for {power_name}: {e}")

        try:
            phase_data = game.process()
            print(f"Phase processed. Phase data archived for phase {phase_data.name}")
        except Exception as e:
            print(f"Error processing phase: {e}")
            break

        phase_counter += 1
        
        time.sleep(0.1)

    to_saved_game_format(game, output_path='game.json')
    print("Game completed. Final state saved to game.json.")

if __name__ == "__main__":
    main()
