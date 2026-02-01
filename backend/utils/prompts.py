"""
Configuration for suggested prompts.
"""

GENERIC_PROMPTS = [
    {
        "label": "Market Overview",
        "prompt": "Give me a brief overview of the current market landscape for our industry.",
        "complexity": "simple",
        "expected_flow": ["Founder", "Market Researcher", "Founder"],
    },
    {
        "label": "Competitor Analysis",
        "prompt": "Who are our main competitors and what are their strengths and weaknesses?",
        "complexity": "medium",
        "expected_flow": ["Founder", "Market Researcher", "Founder"],
    },
    {
        "label": "SWOT Analysis",
        "prompt": "Conduct a SWOT analysis for our company based on available data.",
        "complexity": "medium",
        "expected_flow": ["Founder", "Market Researcher", "Founder"],
    },
]

COMPANY_PROMPTS = {
    "solaris": [
        {
            "label": "Sustainability Audit",
            "prompt": "Review our current sustainability practices and suggest improvements.",
            "complexity": "complex",
            "expected_flow": ["Founder", "Sustainability Expert", "Founder"],
        },
        {
            "label": "New Coffee Blend",
            "prompt": "Propose a marketing campaign for a new single-origin Ethiopian blend.",
            "complexity": "complex",
            "expected_flow": ["Founder", "Marketing Head", "Content Creator", "Founder"],
        },
    ],
    "promptsmint": [
        {
            "label": "Prompt Optimization",
            "prompt": "Analyze our top-performing prompts and suggest optimizations.",
            "complexity": "medium",
            "expected_flow": ["Founder", "Prompt Engineer", "Founder"],
        },
        {
            "label": "New AI Models",
            "prompt": "What are the latest AI models we should support in our platform?",
            "complexity": "simple",
            "expected_flow": ["Founder", "Tech Lead", "Founder"],
        },
    ],
}
