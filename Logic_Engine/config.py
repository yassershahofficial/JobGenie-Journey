"""
Configuration settings for the Logic Engine

Contains default weights, paths, and constants used throughout the matching system.
"""

from pathlib import Path

# Scoring weights (must sum to 1.0)
# Legacy weights (kept for backward compatibility)
WEIGHT_PERSONALITY = 0.4  # 40%
WEIGHT_KNOWLEDGE = 0.4    # 40% (Degree/Knowledge domains)
WEIGHT_SKILLS = 0.2       # 20% (Technical skills)

# Dual-Track Weight Configurations

# Track 1: Pragmatic Match (Capability Focus)
# Focus: "Can I get hired?"
PRAGMATIC_WEIGHTS = {
    "knowledge": 0.5,    # 50% - Degree is the entry ticket
    "skills": 0.3,       # 30% - Tools make me useful
    "personality": 0.2   # 20% - Secondary factor
}

# Track 2: Passion Match (Compatibility Focus)
# Focus: "Will I be happy?"
PASSION_WEIGHTS = {
    "personality": 0.7,  # 70% - Defines daily satisfaction
    "knowledge": 0.2,    # 20% - Somewhat related to studies
    "skills": 0.1        # 10% - Can learn tools later
}

# Default number of top results to return
DEFAULT_TOP_N = 10

# Path to jobs database (relative to project root)
# Logic_Engine is at: project_root/Logic_Engine/
# Database is at: project_root/ETL_pipeline/output/jobs_database.json
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_PATH = PROJECT_ROOT / "ETL_pipeline" / "output" / "jobs_database.json"

# RIASEC normalization constants
# User input: 1-7 scale
# Database format: 0.0-1.0 scale
RIASEC_MIN_SCALE = 1.0
RIASEC_MAX_SCALE = 7.0

# Advanced Statistical Hybrid Model Configuration

# Sigmoid activation parameters
SIGMOID_CENTER = 0.15  # Center point (average expectation for Jaccard)
SIGMOID_STEEPNESS = 20.0  # How strictly to punish bad matches

# Fuzzy matching threshold
FUZZY_MATCH_THRESHOLD = 0.70  # 70% similarity required for fuzzy match

# Cosine baseline normalization
COSINE_BASELINE_SAMPLE_SIZE = 100  # Number of random pairs to sample for baseline

