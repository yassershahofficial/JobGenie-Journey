# Logic Engine - Job Matching System

A sophisticated job matching engine that matches user profiles against job databases using personality traits (RIASEC), knowledge domains, and technical skills.

## Architecture Overview

The Logic Engine implements a 6-phase matching pipeline:

1. **Phase 1: Database Loader** - Loads jobs database into memory for fast access
2. **Phase 2: Similarity Calculators** - Cosine similarity for vectors, Jaccard similarity for sets
3. **Phase 3: Preprocessor** - Normalizes user input to match database format
4. **Phase 4: Main Loop** - Iterates through all jobs, computing similarity scores
5. **Phase 5: Weighted Scoring** - Combines three scores into final compatibility score
6. **Phase 6: Final Sort** - Ranks and returns top N matches

## Installation

The Logic Engine is part of the project and uses the shared virtual environment:

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Dependencies are already installed (pandas, etc.)
```

## Quick Start

### Basic Usage

```python
from Logic_Engine import load_jobs_database, match_jobs

# Load database
jobs_database = load_jobs_database()

# Define user profile
user_profile = {
    "riasec": [2.0, 5.0, 3.0, 4.0, 6.0, 4.0],  # 1-7 scale
    "knowledge_domains": ["Computer Science", "Mathematics", "Statistics"],
    "tech_skills": ["Python", "SQL", "Machine Learning"]
}

# Match jobs
results = match_jobs(user_profile, jobs_database, top_n=10)

# Display results
for i, result in enumerate(results, 1):
    print(f"{i}. {result['title']} (Score: {result['final_score']:.4f})")
```

### Running Example

```bash
# Run example usage
python -m Logic_Engine.main

# Run CLI interface
python -m Logic_Engine.main --cli
```

## Input Format

### User Profile

The user profile is a dictionary with the following structure:

```python
user_profile = {
    "riasec": [float, float, float, float, float, float],  # 6 values, 1-7 scale
    "knowledge_domains": [str, str, ...],                   # List of strings
    "tech_skills": [str, str, ...]                          # List of strings
}
```

**RIASEC Order:**
1. Realistic
2. Investigative
3. Artistic
4. Social
5. Enterprising
6. Conventional

**Example:**
```python
user_profile = {
    "riasec": [2.0, 5.0, 3.0, 4.0, 6.0, 4.0],
    "knowledge_domains": ["Python", "Mathematics", "Statistics"],
    "tech_skills": ["Python", "SQL", "Machine Learning", "TensorFlow"]
}
```

## Output Format

The `match_jobs()` function returns a list of dictionaries, each containing:

```python
{
    "job_id": "11-1021.00",           # O*NET-SOC Code
    "title": "Data Scientist",         # Job title
    "description": "Job description...", # Job description
    "final_score": 0.8542,             # Combined weighted score (0.0-1.0)
    "scores": {
        "personality": 0.9234,         # RIASEC similarity (0.0-1.0)
        "knowledge": 0.7500,           # Knowledge overlap (0.0-1.0)
        "skills": 0.8889               # Skills overlap (0.0-1.0)
    }
}
```

Results are sorted by `final_score` in descending order (highest first).

## Dual-Track Matching System

The Logic Engine uses a **dual-track matching system** that evaluates jobs from two perspectives:

### Track 1: Pragmatic Match (Capability)
**Focus:** "Can I get hired?"

- **Knowledge:** 50% - Your degree is the entry ticket
- **Skills:** 30% - Your tools make you useful
- **Personality:** 20% - Secondary factor

This track prioritizes jobs where your education and technical skills align, maximizing your chances of getting hired.

### Track 2: Passion Match (Compatibility)
**Focus:** "Will I be happy?"

- **Personality:** 70% - Defines your daily satisfaction
- **Knowledge:** 20% - Somewhat related to your studies
- **Skills:** 10% - You can learn the tools later

This track prioritizes jobs that match your personality and interests, maximizing long-term job satisfaction.

### Using Dual-Track

**Get both tracks (default):**
```python
results = match_jobs(user_profile, track="both")
# Returns: {"pragmatic": [...], "passion": [...]}
```

**Get only pragmatic track:**
```python
results = match_jobs(user_profile, track="pragmatic")
# Returns: List of results
```

**Get only passion track:**
```python
results = match_jobs(user_profile, track="passion")
# Returns: List of results
```

### Custom Weights

You can still provide custom weights (overrides track selection):

```python
custom_weights = {
    "personality": 0.5,
    "knowledge": 0.3,
    "skills": 0.2
}

results = match_jobs(user_profile, jobs_database, weights=custom_weights)
```

## API Reference

### `load_jobs_database(force_reload=False)`

Loads the jobs database from `ETL_pipeline/output/jobs_database.json`.

**Parameters:**
- `force_reload` (bool): If True, reload from file even if cached. Default: False

**Returns:**
- List of job dictionaries

**Raises:**
- `FileNotFoundError`: If database file doesn't exist
- `json.JSONDecodeError`: If file contains invalid JSON

### `match_jobs(user_profile, jobs_database=None, top_n=10, track="both", weights=None)`

Matches user profile against all jobs in database using dual-track logic.

**Parameters:**
- `user_profile` (dict): User profile dictionary (see Input Format)
- `jobs_database` (list, optional): Pre-loaded jobs database. If None, loads from file.
- `top_n` (int): Number of top results to return per track. Default: 10
- `track` (str): Which track to use: `"pragmatic"`, `"passion"`, or `"both"` (default: `"both"`)
- `weights` (dict, optional): Custom weights dict (overrides track) with keys: `personality`, `knowledge`, `skills`. Must sum to 1.0.

**Returns:**
- If `track="both"`: Dictionary with keys `"pragmatic"` and `"passion"`, each containing a list of result dictionaries
- If `track="pragmatic"` or `track="passion"`: List of result dictionaries (see Output Format)

**Raises:**
- `ValueError`: If weights don't sum to 1.0 or invalid track value

### `normalize_riasec(user_riasec)`

Normalizes RIASEC scores from 1-7 scale to 0.0-1.0 scale.

**Parameters:**
- `user_riasec` (list): List of 6 floats (1-7 scale)

**Returns:**
- List of 6 floats (0.0-1.0 scale)

### `standardize_text(text_list)`

Converts text to lowercase and removes empty strings.

**Parameters:**
- `text_list` (list): List of strings

**Returns:**
- List of lowercase strings

### `cosine_similarity(vector_a, vector_b)`

Calculates cosine similarity between two vectors.

**Parameters:**
- `vector_a` (list): First vector (list of floats)
- `vector_b` (list): Second vector (list of floats)

**Returns:**
- Float between 0.0 and 1.0

### `jaccard_similarity(list_a, list_b)`

Calculates Jaccard similarity between two lists of strings.

**Parameters:**
- `list_a` (list): First list of strings
- `list_b` (list): Second list of strings

**Returns:**
- Float between 0.0 and 1.0

## Configuration

Configuration settings are in `config.py`:

```python
# Scoring weights
WEIGHT_PERSONALITY = 0.4  # 40%
WEIGHT_KNOWLEDGE = 0.4    # 40%
WEIGHT_SKILLS = 0.2       # 20%

# Default top N results
DEFAULT_TOP_N = 10

# Database path (relative to project root)
DATABASE_PATH = PROJECT_ROOT / "ETL_pipeline" / "output" / "jobs_database.json"
```

## Testing

Run unit tests:

```bash
python -m Logic_Engine.test_matcher
```

Or with verbose output:

```bash
python -m Logic_Engine.test_matcher -v
```

## Performance

- **Database Loading**: ~1-2 seconds (one-time, cached in memory)
- **Matching**: ~50-100ms for 438 jobs (depends on hardware)
- **Memory Usage**: ~1-2 MB for cached database

## Dependencies

- Python 3.10+
- Standard library only (json, math, pathlib, typing, unittest)

## File Structure

```
Logic_Engine/
├── __init__.py              # Public API exports
├── config.py                # Configuration settings
├── database_loader.py       # Phase 1: Database loading
├── similarity.py            # Phase 2: Similarity calculators
├── preprocessor.py          # Phase 3: Input preprocessing
├── matcher.py               # Phase 4-6: Main matching engine
├── main.py                  # Example usage and CLI
├── test_matcher.py          # Unit tests
└── README.md               # This file
```

## Examples

### Example 1: Data Scientist Profile

```python
from Logic_Engine import match_jobs, load_jobs_database

user_profile = {
    "riasec": [2.0, 6.0, 3.0, 3.0, 4.0, 3.0],
    "knowledge_domains": [
        "Computer Science",
        "Mathematics",
        "Statistics",
        "Machine Learning"
    ],
    "tech_skills": [
        "Python",
        "R",
        "SQL",
        "TensorFlow",
        "PyTorch",
        "Pandas",
        "Scikit-learn"
    ]
}

jobs = load_jobs_database()
results = match_jobs(user_profile, jobs, top_n=5)

for result in results:
    print(f"{result['title']}: {result['final_score']:.4f}")
```

### Example 2: Software Engineer Profile

```python
user_profile = {
    "riasec": [3.0, 5.0, 4.0, 3.0, 5.0, 4.0],
    "knowledge_domains": [
        "Computer Science",
        "Software Engineering",
        "Algorithms"
    ],
    "tech_skills": [
        "Python",
        "Java",
        "JavaScript",
        "React",
        "Node.js",
        "Git"
    ]
}

results = match_jobs(user_profile, top_n=10)
```

## Troubleshooting

### Database Not Found

If you get `FileNotFoundError`, ensure the ETL pipeline has been run:

```bash
python ETL_pipeline/transformation.py
```

This will generate `ETL_pipeline/output/jobs_database.json`.

### Invalid RIASEC Vector

RIASEC vector must have exactly 6 values. If you get `ValueError`, check your input:

```python
# Correct
riasec = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]

# Wrong (only 5 values)
riasec = [1.0, 2.0, 3.0, 4.0, 5.0]
```

### Weights Don't Sum to 1.0

Custom weights must sum to exactly 1.0:

```python
# Correct
weights = {"personality": 0.4, "knowledge": 0.4, "skills": 0.2}

# Wrong (sums to 0.9)
weights = {"personality": 0.4, "knowledge": 0.3, "skills": 0.2}
```

## License

Part of the Final Year Project.

