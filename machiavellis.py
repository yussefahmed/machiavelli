import ollama
import time
import argparse
from typing import List , Dict , Any

class Agent:
    def __init__(self , name : str , model: str = "qwen2.5:3b", personality : str = None ):
        """
        Initializing an Diplomacy agent with a name and optional personality(may be useful in future research)

        Args: 
            name : the name of the agent
            model : the Ollama model name to be used
            personality : Optional agent personality to guide the agents responses eg; agressive , tame etc

        """
        self.name : str= name
        self.model: str= model
        self.personality : str = personality
        self.conversation_history: List [Dict[str,str]] = []
        
        ###personality init if exists
        if personality :
            system_message = {"role" : "system" , "content" : f"You are {name} with a {personality}"} 
            self.conversation_history.append(system_message)


    def respond_to(self,message_content : str , from_name: str) -> str:
        """
        Generate a response to the given message.
        Args:
           message_content : the content of the message to respond to 
           from_name : the name of the sender of the message

        Returns :
                 the agent's response
        """
        ## add the message received to the history of the LLM
        user_message = {"role" : "user" , "content" : f"{from_name} : {message_content}"}
        self.conversation_history.append(user_message)

        try:
            response = ollama.chat(
                model=self.model,
                messages=self.conversation_history,
                options={"temperature": 0.7}  # Add some randomness
            )

            response_content = response["message"]["content"]

                # Add the response to conversation history
            assistant_message = {"role": "assistant", "content": response_content}
            self.conversation_history.append(assistant_message)
            
            return response_content
            
        except Exception as e:
            print(f"Error: {self.name} failed to respond: {e}")
            return f"[Error: {self.name} couldn't generate a response]"


            


def simulate_conversation(agent1 : Agent,agent2: Agent,initial_prompt: str,num_turns: int = 5 ,delay : float = 0.5):
    """
    Simulate a conversation between two agents.

    Args:
         agent1: the first Agent 
         agent2 : the second Agent
         initial_prompt : the initial message to start the communication
         num_turns : the number of conversations turns to simulate
         delay : delay between responses for readability
    
    """
    print(f"\n{'=*50'}")
    print(f"Starting conversation between {agent1.name} and {agent2.name}")
    print(f"Initial prompt: {initial_prompt}")
    print(f"{'='*50}\n")


    #Start with the initial prompt from agent1

    current_message = initial_prompt
    current_speaker = agent1
    next_speaker = agent2

    for turn in range(num_turns * 2):
        print(f"{current_speaker.name}: {current_message}")
        time.sleep(delay)

        response = next_speaker.respond_to(current_message, current_speaker.name)

        current_speaker , next_speaker = next_speaker , current_speaker 
        current_message = response 

        print("-" * 30)

    print(f"\n{'='*50}")
    print("Conversation ended")
    print(f"{'='*50}\n")




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulate a conversation between two Qwen2.5 agents')
    parser.add_argument('--prompt', type=str, default="Hello, how are you today?", 
                        help='Initial prompt to start the conversation')
    parser.add_argument('--turns', type=int, default=5, 
                        help='Number of conversation turns')
    parser.add_argument('--delay', type=float, default=1.0, 
                        help='Delay between responses (seconds)')
    parser.add_argument('--agent1', type=str, default="Philosopher", 
                        help='Name of first agent')
    parser.add_argument('--agent2', type=str, default="Scientist", 
                        help='Name of second agent')
    parser.add_argument('--personality1', type=str, 
                        default="You are a thoughtful philosopher who considers deep questions about existence and meaning.", 
                        help='Personality for first agent')
    parser.add_argument('--personality2', type=str, 
                        default="You are a scientific-minded person who values empirical evidence and logical reasoning.", 
                        help='Personality for second agent')
                        
    args = parser.parse_args()
    
    # Create the two agents
    agent1 = Agent(
        name=args.agent1,
        personality=args.personality1
    )
    
    agent2 = Agent(
        name=args.agent2,
        personality=args.personality2
    )
    
    # Start the conversation
    simulate_conversation(
        agent1=agent1,
        agent2=agent2,
        initial_prompt=args.prompt,
        num_turns=args.turns,
        delay=args.delay
    )
