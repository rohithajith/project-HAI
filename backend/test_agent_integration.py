import asyncio
import json
from datetime import datetime
from ai_agents.agent_manager_corrected import agent_manager_corrected # Assuming singleton instance

async def run_agent_tests():
    """Runs integration tests against the AgentManagerCorrected."""

    test_messages = [
        "I want towels", # Should trigger RoomServiceAgent (fast path)
        "The sink in my room is broken, it's leaking!", # Should trigger MaintenanceAgent
        "I need to book a conference room for 10 people tomorrow morning.", # Should trigger ServicesBookingAgent
        "Tell me about the spa treatments available.", # Should trigger WellnessAgent
        "Are there any special offers or promotions tonight?", # Should trigger PromotionAgent
    ]

    output_file = "agent_test_results.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Agent Test Run - {timestamp}\n")
        f.write("=" * 30 + "\n\n")

        for i, message in enumerate(test_messages):
            print(f"Testing message {i+1}: '{message}'")
            f.write(f"--- Test Case {i+1} ---\n")
            f.write(f"Input Message: {message}\n")

            try:
                # Assuming history is not needed for these basic tests
                response_output = await agent_manager_corrected.process(message, history=None)

                # Convert AgentOutput to a dictionary for easier serialization
                response_dict = response_output.model_dump(mode='json') # Use model_dump for Pydantic v2+

                f.write("Output Response:\n")
                # Pretty print the JSON representation of the AgentOutput
                f.write(json.dumps(response_dict, indent=2))
                f.write("\n\n")
                print(f"  Response captured.")

            except Exception as e:
                print(f"  Error processing message: {e}")
                f.write(f"Error processing message: {type(e).__name__} - {e}\n\n")

    print(f"\nTest results saved to {output_file}")

if __name__ == "__main__":
    # Ensure the script is run from the 'backend' directory or adjust paths accordingly
    # If running from the root directory, imports might need adjustment (e.g., from backend.ai_agents...)
    print("Starting agent integration test...")
    asyncio.run(run_agent_tests())
    print("Agent integration test finished.")