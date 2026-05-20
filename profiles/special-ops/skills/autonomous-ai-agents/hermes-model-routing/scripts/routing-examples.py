#!/usr/bin/env python3
"""
Hermes Model Routing Examples

Practical examples of implementing the OpenAI 5.4/Kimi/GLM 5.1 routing pattern
using delegate_task in Hermes workflows.

Usage: Import these patterns or adapt for your specific tasks.
"""

def code_development_pattern():
    """
    Pattern: Feature Development
    OpenAI 5.4 → Kimi → OpenAI 5.4
    """
    return {
        "goal": "Build a user authentication system with JWT",
        "context": """
        This is a complex task requiring:
        1. Planning and architecture (OpenAI 5.4)
        2. Implementation (Kimi)
        3. Security review (OpenAI 5.4)
        
        Models to use:
        - OpenAI 5.4 for planning/review
        - Kimi for implementation work
        """,
        "workflow": [
            {
                "model": "openai-5.4",
                "task": "Plan the auth system architecture and security considerations"
            },
            {
                "model": "kimi", 
                "task": "Implement JWT authentication endpoints and user management"
            },
            {
                "model": "openai-5.4",
                "task": "Review the implementation for security best practices"
            }
        ]
    }

def research_plus_implementation_pattern():
    """
    Pattern: Research + Implementation
    OpenAI 5.4 → GLM 5.1 → Kimi → OpenAI 5.4
    """
    return {
        "goal": "Research GRPO papers and implement the method",
        "context": """
        Multi-step workflow:
        1. GLM 5.1: Do initial research and paper summarization
        2. Kimi: Implement the algorithm
        3. OpenAI 5.4: Review implementation against research
        
        Cost-effective by using GLM for research, Kimi for coding.
        """,
        "workflow": [
            {
                "model": "glm-5.1",
                "task": "Find and summarize key GRPO research papers, extract algorithm details"
            },
            {
                "model": "kimi",
                "task": "Implement GRPO training loop based on research summaries"
            },
            {
                "model": "openai-5.4", 
                "task": "Review implementation, ensure it matches research, suggest improvements"
            }
        ]
    }

def bulk_processing_pattern():
    """
    Pattern: Bulk Data Processing
    OpenAI 5.4 → GLM 5.1 → OpenAI 5.4
    """
    return {
        "goal": "Clean and analyze customer dataset",
        "context": """
        Repetitive task where GLM 5.1 can do the bulk work:
        1. OpenAI 5.4: Define the cleaning rules
        2. GLM 5.1: Execute the repetitive cleaning
        3. OpenAI 5.4: Analyze and summarize results
        """,
        "workflow": [
            {
                "model": "openai-5.4",
                "task": "Define data cleaning rules and analysis requirements"
            },
            {
                "model": "glm-5.1",
                "task": "Execute data cleaning, normalization, and basic statistical analysis"
            },
            {
                "model": "openai-5.4",
                "task": "Analyze results, create insights report, identify patterns"
            }
        ]
    }

def concurrent_hats_pattern():
    """
    Pattern: De Bono's Six Thinking Hats (Concurrent)
    Uses all 3 models in parallel for multi-perspective analysis
    """
    return {
        "goal": "Analyze a business decision using Six Thinking Hats",
        "context": """
        Run all hats concurrently for efficiency:
        - OpenAI 5.4: Blue hat (facilitator) and White hat (facts)
        - Kimi: Black hat (risks) and Yellow hat (benefits)  
        - GLM 5.1: Red hat (emotions) and Green hat (creativity)
        """,
        "tasks": [
            {
                "model": "openai-5.4",
                "goal": "Blue hat: Facilitate the analysis process and white hat: present factual information",
                "context": "Act as facilitator and fact-checker. Structure the analysis and provide objective data."
            },
            {
                "model": "kimi",
                "goal": "Black hat: Identify risks, problems, and potential failures",
                "context": "Critically analyze the decision. What could go wrong? What are the downsides?"
            },
            {
                "model": "glm-5.1", 
                "goal": "Red hat: Emotional response and green hat: creative alternatives",
                "context": "Express gut feelings about the decision. Generate creative alternatives and possibilities."
            }
        ]
    }

# Example of how to use these patterns in execute_code
def route_task_based_on_complexity(task_description: str) -> str:
    """
    Simple routing logic to choose appropriate model
    """
    if any(word in task_description.lower() for word in ['strategic', 'plan', 'review', 'decide']):
        return "openai-5.4"  # Strategic tasks
    elif any(word in task_description.lower() for word in ['code', 'implement', 'debug', 'build']):
        return "kimi"  # Implementation tasks  
    elif any(word in task_description.lower() for word in ['summarize', 'clean', 'format', 'bulk']):
        return "glm-5.1"  # Routine tasks
    else:
        return "openai-5.4"  # Default to orchestrator

# Usage example:
# pattern = code_development_pattern()
# for step in pattern['workflow']:
#     model = step['model']
#     task = step['task']
#     print(f"Dispatching to {model}: {task}")
#     # Use delegate_task here in actual Hermes code