"""
hello_world_agent.py - Simple Multi-Agent Conversation Demo for ResQ-MAR

This script demonstrates a simple 2-agent conversation using AutoGen (AG2)
powered entirely by a local Ollama instance (llama3.1 model).
It requires Ollama to be running locally.
"""

from autogen import ConversableAgent

def main() -> None:
    """
    Sets up the local LLM configuration and runs a conversation
    between a planner agent and a critic agent to respond to an emergency.
    """
    
    print("Starting ResQ-MAR Hello World Agent Demo...\n")
    
    # 1. Configure an LLM config pointing to local Ollama
    # The base_url matches where Ollama serves the OpenAI-compatible API locally.
    llm_config = {
        "config_list": [
            {
                "model": "llama3.1",
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama", # Placeholder API key, required by client but ignored by Ollama
            }
        ]
    }
    
    # 2. Create two ConversableAgent instances
    print("Initializing agents...")
    
    # The planner agent proposes immediate actions
    planner_agent = ConversableAgent(
        name="planner_agent",
        system_message="You are an emergency response planner. When given an incident, suggest 3 immediate actions.",
        llm_config=llm_config,
        human_input_mode="NEVER",
    )
    
    # The critic agent reviews the planner's actions for safety
    critic_agent = ConversableAgent(
        name="critic_agent",
        system_message="You are a safety critic. Review the planner's actions and flag any safety concerns.",
        llm_config=llm_config,
        human_input_mode="NEVER",
    )
    
    # Create a user proxy to send the initial message to the planner
    user_proxy = ConversableAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        code_execution_config=False,
    )
    
    initial_message = "A flood has hit Sector 7. 50 people are trapped on rooftops. Water is rising."
    
    # 3. Start a conversation where the user_proxy sends the initial scenario to the planner_agent
    print(f"\n--- User Proxy initiates task with Planner Agent ---")
    user_proxy.initiate_chat(
        planner_agent,
        message=initial_message,
        max_turns=1 # The planner simply replies with its plan
    )
    
    # Extract the planner's proposed plan from the chat history
    planner_reply = planner_agent.last_message(user_proxy)["content"]
    
    # 4. Let the two agents discuss for 2 turns maximum.
    # The planner initiates chat with the critic to review the proposed plan.
    print(f"\n--- Planner Agent and Critic Agent discuss the plan ---")
    chat_result = planner_agent.initiate_chat(
        critic_agent,
        message=f"Here is my proposed plan for the recent incident:\n\n{planner_reply}\n\nPlease review it for safety concerns.",
        max_turns=2 # Agents discuss for 2 turns maximum
    )
    
    # 5. The full conversation transcript is automatically printed to the terminal
    # by the AutoGen initiate_chat calls above.
    
    print("\n--- Conversation Complete ---")

if __name__ == "__main__":
    main()
