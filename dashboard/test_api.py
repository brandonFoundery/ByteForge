#!/usr/bin/env python3
"""
Test script for the Requirements Generation Dashboard API
"""

import requests
import json
import sys

def test_summary_endpoint(base_url="http://localhost:8001"):
    """Test the summary endpoint"""
    print(f"Testing summary endpoint at {base_url}/api/summary")
    
    try:
        response = requests.get(f"{base_url}/api/summary")
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        data = response.json()
        print("\nSummary data:")
        print(json.dumps(data, indent=2))
        
        # Check if we have documents
        if "documents" in data and data["documents"]:
            print(f"\nFound {len(data['documents'])} documents:")
            for doc_id, doc_info in data["documents"].items():
                print(f"  - {doc_id}: {doc_info.get('status', 'unknown')}")
        else:
            print("\nNo documents found in summary data")
            
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        return False

def test_logs_endpoint(base_url="http://localhost:8001"):
    """Test the logs endpoint"""
    print(f"\nTesting logs endpoint at {base_url}/api/logs")
    
    try:
        response = requests.get(f"{base_url}/api/logs")
        response.raise_for_status()
        
        data = response.json()
        
        if "logs" in data and data["logs"]:
            print(f"\nFound {len(data['logs'])} log entries:")
            for i, log in enumerate(data["logs"][:5]):  # Show first 5 logs
                print(f"  {i+1}. {log}")
            
            if len(data["logs"]) > 5:
                print(f"  ... and {len(data['logs']) - 5} more")
        else:
            print("\nNo logs found")
            
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        return False

def main():
    """Main entry point"""
    # Use custom base URL if provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001"
    
    print("Testing Requirements Generation Dashboard API")
    print("============================================")
    
    # Test summary endpoint
    summary_ok = test_summary_endpoint(base_url)
    
    # Test logs endpoint
    logs_ok = test_logs_endpoint(base_url)
    
    # Print overall result
    if summary_ok and logs_ok:
        print("\n✅ All API tests passed!")
    else:
        print("\n❌ Some API tests failed")
        
    print("\nIf the API tests passed, you can access the dashboard at:")
    print(f"http://localhost:5173")

if __name__ == "__main__":
    main()