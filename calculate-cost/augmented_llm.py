import re
import json
from typing import Tuple, Optional

def calculate_cost(hours: float, rate: float) -> float:
    """
    Calculate the total cost based on hours worked and hourly rate.
    
    Args:
        hours: Number of hours worked
        rate: Hourly rate
        
    Returns:
        Total cost (hours * rate)
    """
    return hours * rate

def create_llm_prompt(user_query: str) -> str:
    """
    Create a prompt that instructs the LLM about tool usage.
    
    Args:
        user_query: The user's original question
        
    Returns:
        Formatted prompt with tool instructions
    """
    prompt = f"""You are a helpful assistant. You can call cost(hours, rate) to compute cost calculations.

When you decide a task requires calculating cost, return TOOL: hours=X rate=Y on its own line, where X and Y are the numeric values.

User query: {user_query}

Please provide a helpful response. If cost calculation is needed, use the tool format specified above."""
    
    return prompt

def parse_tool_call(text: str) -> Optional[Tuple[float, float]]:
    """
    Parse the LLM output to extract tool call parameters.
    
    Args:
        text: LLM output text
        
    Returns:
        Tuple of (hours, rate) if tool call found, None otherwise
    """
    # Look for TOOL: hours=X rate=Y pattern
    pattern = r'TOOL:\s*hours=([0-9.]+)\s*rate=([0-9.]+)'
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        hours = float(match.group(1))
        rate = float(match.group(2))
        return (hours, rate)
    
    return None

def substitute_tool_result(text: str, hours: float, rate: float, result: float) -> str:
    """
    Replace the tool call with the actual result.
    
    Args:
        text: Original LLM output
        hours: Hours parameter
        rate: Rate parameter
        result: Calculated result
        
    Returns:
        Text with tool call replaced by result
    """
    # Replace the TOOL: line with the result
    pattern = r'TOOL:\s*hours=[0-9.]+\s*rate=[0-9.]+'
    replacement = f'Result: ${result:.2f}'
    return re.sub(pattern, replacement, text, flags=re.IGNORECASE)

def mock_llm_call(prompt: str) -> str:
    """
    Mock LLM function for demonstration purposes.
    In a real implementation, this would call an actual LLM API.
    
    Args:
        prompt: The prompt to send to the LLM
        
    Returns:
        Mock LLM response
    """
    # Simple pattern matching for demonstration
    if "freelance" in prompt.lower() or "project" in prompt.lower():
        return "For a freelance project, I need to calculate the total cost. TOOL: hours=40 rate=75"
    elif "consulting" in prompt.lower():
        return "For consulting work, let me calculate the cost. TOOL: hours=20 rate=150"
    elif "cost" in prompt.lower() and "hour" in prompt.lower():
        return "I can help calculate that cost. TOOL: hours=8 rate=50"
    else:
        return "I can help you with various calculations. If you need cost calculations, please provide hours and rate information."

def run_augmented_llm(user_query: str, max_iterations: int = 3) -> str:
    """
    Main function that runs the augmented LLM with tool calling capability.
    
    Args:
        user_query: The user's question
        max_iterations: Maximum number of tool calls to prevent infinite loops
        
    Returns:
        Final response after tool execution
    """
    current_prompt = create_llm_prompt(user_query)
    iteration = 0
    
    while iteration < max_iterations:
        # Get LLM response
        llm_response = mock_llm_call(current_prompt)
        print(f"LLM Response (iteration {iteration + 1}): {llm_response}")
        
        # Check if tool call is needed
        tool_params = parse_tool_call(llm_response)
        
        if tool_params is None:
            # No tool call found, return the response
            return llm_response
        
        # Execute the tool
        hours, rate = tool_params
        result = calculate_cost(hours, rate)
        print(f"Tool executed: calculate_cost({hours}, {rate}) = {result}")
        
        # Substitute the result back into the response
        final_response = substitute_tool_result(llm_response, hours, rate, result)
        
        # For this implementation, we return after one tool call
        # In more complex scenarios, you might feed this back to the LLM
        return final_response
        
    return "Maximum iterations reached"

def main():
    """
    Example usage of the augmented LLM system.
    """
    print("Augmented LLM with Cost Calculator Tool")
    print("=" * 40)
    
    # Test cases
    test_queries = [
        "How much would a freelance project cost?",
        "Calculate the cost for consulting work",
        "What's the cost for 8 hours at $50 per hour?",
        "Tell me about Python programming"
    ]
    
    for query in test_queries:
        print(f"\nUser Query: {query}")
        print("-" * 30)
        response = run_augmented_llm(query)
        print(f"Final Response: {response}")
        print()

if __name__ == "__main__":
    main()