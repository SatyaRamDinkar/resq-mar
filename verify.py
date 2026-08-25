"""
verify.py - Environment verification script for ResQ-MAR

This script checks the installation and connectivity of all core components
in the tech stack, including Python packages, Ollama, ChromaDB, and OR-Tools.
"""

import sys
import requests
import typing

def check_imports() -> bool:
    """Verifies that all required packages can be imported."""
    print("--- 1. Package Import Test ---")
    packages = ["autogen", "chromadb", "streamlit", "ortools", "fastapi"]
    all_passed = True
    
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"[PASS] {pkg} imported successfully")
        except ImportError as e:
            print(f"[FAIL] Failed to import {pkg}: {e}")
            all_passed = False
            
    return all_passed

def check_ollama() -> bool:
    """Verifies that Ollama is running and accessible locally."""
    print("\n--- 2. Ollama Connectivity Test ---")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("[PASS] Ollama is running")
            models = response.json().get("models", [])
            if models:
                model_names = [model.get("name") for model in models]
                print(f"  Available models: {', '.join(model_names)}")
            else:
                print("  No models downloaded yet. Run 'ollama pull llama3.1'")
            return True
        else:
            print(f"[FAIL] Ollama returned unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("[FAIL] Ollama is not running. Start it with: ollama serve")
        return False

def check_chromadb() -> bool:
    """Verifies that ChromaDB can be instantiated and basic operations work."""
    print("\n--- 3. ChromaDB Test ---")
    try:
        import chromadb
        # Create a temporary ephemeral client for testing
        client = chromadb.EphemeralClient()
        collection = client.create_collection(name="test_collection")
        
        # Add 2 test documents
        collection.add(
            documents=["This is a document about emergency response", "This is a document about route optimization"],
            metadatas=[{"source": "test1"}, {"source": "test2"}],
            ids=["id1", "id2"]
        )
        
        # Query them
        results = collection.query(
            query_texts=["emergency"],
            n_results=1
        )
        
        if results['documents'] and len(results['documents'][0]) > 0:
            print("[PASS] ChromaDB working")
            return True
        else:
            print("[FAIL] ChromaDB query returned unexpected empty results")
            return False
            
    except Exception as e:
        print(f"[FAIL] ChromaDB test failed: {e}")
        return False

def check_ortools() -> bool:
    """Verifies that OR-Tools routing model works with a simple VRP."""
    print("\n--- 4. OR-Tools Test ---")
    try:
        from ortools.constraint_solver import routing_enums_pb2
        from ortools.constraint_solver import pywrapcp
        
        # Create a tiny VRP with 1 vehicle and 3 nodes (0 is depot)
        # Distance matrix: 0->1=10, 1->2=20, 2->0=15
        distance_matrix = [
            [0, 10, 15],
            [10, 0, 20],
            [15, 20, 0]
        ]
        
        manager = pywrapcp.RoutingIndexManager(len(distance_matrix), 1, 0)
        routing = pywrapcp.RoutingModel(manager)
        
        def distance_callback(from_index: int, to_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]
            
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            print("[PASS] OR-Tools working")
            return True
        else:
            print("[FAIL] OR-Tools failed to find a solution")
            return False
            
    except Exception as e:
        print(f"[FAIL] OR-Tools test failed: {e}")
        return False

def main() -> None:
    """Main execution function to run all tests."""
    print("========================================")
    print("ResQ-MAR Stack Verification")
    print("========================================\n")
    
    results = {
        "Imports": check_imports(),
        "Ollama": check_ollama(),
        "ChromaDB": check_chromadb(),
        "OR-Tools": check_ortools()
    }
    
    print("\n========================================")
    # 5. Print a final summary
    all_passed = all(results.values())
    
    if all_passed:
        print("All systems operational")
    else:
        print("The following systems are broken:")
        for system, passed in results.items():
            if not passed:
                print(f"- {system}")
                
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
