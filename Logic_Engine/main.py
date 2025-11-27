"""
Main Entry Point - Example Usage and CLI Interface

Demonstrates how to use the Logic Engine for job matching.
"""

import json
from .database_loader import load_jobs_database
from .matcher import match_jobs


def example_usage():
    """Example usage of the Logic Engine."""
    
    print("=" * 70)
    print("LOGIC ENGINE - JOB MATCHING EXAMPLE")
    print("=" * 70)
    
    # Example user profile
    user_profile = {
        "riasec": [2.0, 5.0, 3.0, 4.0, 6.0, 4.0],  # 1-7 scale
        "knowledge_domains": [
            "Computer Science",
            "Mathematics",
            "Statistics",
            "Machine Learning"
        ],
        "tech_skills": [
            "Python",
            "SQL",
            "Machine Learning",
            "TensorFlow",
            "Pandas"
        ]
    }
    
    print("\nUser Profile:")
    print(f"  RIASEC: {user_profile['riasec']}")
    print(f"  Knowledge Domains: {user_profile['knowledge_domains']}")
    print(f"  Tech Skills: {user_profile['tech_skills']}")
    
    # Load database
    print("\nLoading jobs database...")
    jobs_database = load_jobs_database()
    
    # Match jobs with dual-track
    print(f"\nMatching against {len(jobs_database)} jobs...")
    print("Using dual-track matching: Pragmatic (Capability) + Passion (Compatibility)")
    results = match_jobs(user_profile, jobs_database, top_n=10, track="both")
    
    # Display Pragmatic results
    print(f"\n{'=' * 70}")
    print(f"TRACK 1: PRAGMATIC MATCH (Capability - Can I get hired?)")
    print(f"{'=' * 70}")
    print(f"Focus: Knowledge 50%, Skills 30%, Personality 20%")
    print(f"TOP {len(results['pragmatic'])} MATCHES\n")
    
    for i, result in enumerate(results['pragmatic'], 1):
        print(f"{i}. {result['title']} (ID: {result['job_id']})")
        print(f"   Final Score: {result['final_score']:.4f}")
        print(f"   Breakdown:")
        print(f"     - Knowledge:    {result['scores']['knowledge']:.4f} (50% weight)")
        print(f"     - Skills:       {result['scores']['skills']:.4f} (30% weight)")
        print(f"     - Personality: {result['scores']['personality']:.4f} (20% weight)")
        print(f"   Description: {result['description'][:100]}...")
        print()
    
    # Display Passion results
    print(f"\n{'=' * 70}")
    print(f"TRACK 2: PASSION MATCH (Compatibility - Will I be happy?)")
    print(f"{'=' * 70}")
    print(f"Focus: Personality 70%, Knowledge 20%, Skills 10%")
    print(f"TOP {len(results['passion'])} MATCHES\n")
    
    for i, result in enumerate(results['passion'], 1):
        print(f"{i}. {result['title']} (ID: {result['job_id']})")
        print(f"   Final Score: {result['final_score']:.4f}")
        print(f"   Breakdown:")
        print(f"     - Personality: {result['scores']['personality']:.4f} (70% weight)")
        print(f"     - Knowledge:    {result['scores']['knowledge']:.4f} (20% weight)")
        print(f"     - Skills:       {result['scores']['skills']:.4f} (10% weight)")
        print(f"   Description: {result['description'][:100]}...")
        print()


def cli_interface():
    """Simple CLI interface for testing."""
    
    print("=" * 70)
    print("LOGIC ENGINE - CLI INTERFACE")
    print("=" * 70)
    print("\nEnter your profile information:")
    print("(Press Enter to use example values)")
    
    # Get RIASEC scores
    print("\nRIASEC Scores (1-7 scale, comma-separated, 6 values):")
    print("Order: Realistic, Investigative, Artistic, Social, Enterprising, Conventional")
    riasec_input = input("> ").strip()
    
    if not riasec_input:
        riasec = [2.0, 5.0, 3.0, 4.0, 6.0, 4.0]
        print(f"Using example: {riasec}")
    else:
        try:
            riasec = [float(x.strip()) for x in riasec_input.split(',')]
            if len(riasec) != 6:
                raise ValueError("Must have exactly 6 values")
        except ValueError as e:
            print(f"Error: {e}")
            return
    
    # Get knowledge domains
    print("\nKnowledge Domains (comma-separated):")
    knowledge_input = input("> ").strip()
    if not knowledge_input:
        knowledge_domains = ["Computer Science", "Mathematics", "Statistics"]
        print(f"Using example: {knowledge_domains}")
    else:
        knowledge_domains = [x.strip() for x in knowledge_input.split(',')]
    
    # Get tech skills
    print("\nTech Skills (comma-separated):")
    skills_input = input("> ").strip()
    if not skills_input:
        tech_skills = ["Python", "SQL", "Machine Learning"]
        print(f"Using example: {tech_skills}")
    else:
        tech_skills = [x.strip() for x in skills_input.split(',')]
    
    # Get top N
    print("\nNumber of results to return (default: 10):")
    top_n_input = input("> ").strip()
    top_n = int(top_n_input) if top_n_input else 10
    
    # Create user profile
    user_profile = {
        "riasec": riasec,
        "knowledge_domains": knowledge_domains,
        "tech_skills": tech_skills
    }
    
    # Match jobs
    print("\n" + "=" * 70)
    print("Matching jobs...")
    print("=" * 70)
    
    # Ask which track to use
    print("\nWhich track would you like to use?")
    print("1. Pragmatic (Capability - Can I get hired?)")
    print("2. Passion (Compatibility - Will I be happy?)")
    print("3. Both tracks")
    track_choice = input("Enter choice (1/2/3, default: 3): ").strip()
    
    track_map = {"1": "pragmatic", "2": "passion", "3": "both", "": "both"}
    selected_track = track_map.get(track_choice, "both")
    
    try:
        results = match_jobs(user_profile, top_n=top_n, track=selected_track)
        
        # Display results based on track
        if selected_track == "both":
            print(f"\n{'=' * 70}")
            print("PRAGMATIC MATCHES (Capability):")
            print(f"{'=' * 70}\n")
            for i, result in enumerate(results['pragmatic'], 1):
                print(f"{i}. {result['title']} (ID: {result['job_id']})")
                print(f"   Score: {result['final_score']:.4f} "
                      f"(K:{result['scores']['knowledge']:.2f} "
                      f"S:{result['scores']['skills']:.2f} "
                      f"P:{result['scores']['personality']:.2f})")
                print()
            
            print(f"\n{'=' * 70}")
            print("PASSION MATCHES (Compatibility):")
            print(f"{'=' * 70}\n")
            for i, result in enumerate(results['passion'], 1):
                print(f"{i}. {result['title']} (ID: {result['job_id']})")
                print(f"   Score: {result['final_score']:.4f} "
                      f"(P:{result['scores']['personality']:.2f} "
                      f"K:{result['scores']['knowledge']:.2f} "
                      f"S:{result['scores']['skills']:.2f})")
                print()
        else:
            track_name = "Pragmatic (Capability)" if selected_track == "pragmatic" else "Passion (Compatibility)"
            print(f"\n{'=' * 70}")
            print(f"{track_name.upper()} MATCHES:")
            print(f"{'=' * 70}\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']} (ID: {result['job_id']})")
                print(f"   Score: {result['final_score']:.4f} "
                      f"(P:{result['scores']['personality']:.2f} "
                      f"K:{result['scores']['knowledge']:.2f} "
                      f"S:{result['scores']['skills']:.2f})")
                print()
        
        # Option to save results
        save = input("Save results to JSON file? (y/n): ").strip().lower()
        if save == 'y':
            filename = input("Filename (default: match_results.json): ").strip()
            if not filename:
                filename = "match_results.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Results saved to {filename}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        cli_interface()
    else:
        example_usage()

