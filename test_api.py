import requests
import json

# Test the API
base_url = "http://localhost:8000/api/v1"
auth_token = "fdf120852ce30af3c730346cd2905b97173db2e1b0ed00eb407c16166a3bb57a"

headers = {
    "Authorization": f"Bearer {auth_token}",
    "Content-Type": "application/json"
}

# Test data matching the API documentation format
test_data_url = {
    "documents": ["https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09X3f1%3A2420"],
    "questions": [
        "What is the grace period for premium payment under the National Parlvar Mediclain Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the No Claim Discount (NCD) offered in this policy?",
        "Is there a benefit for preventive health check-ups?",
        "How does the policy define a 'Hospital'?",
        "What is the extent of coverage for AYUSH treatments?",
        "Are there any sub-limits on room rent and ICU charges for Plan A?"
    ]
}

# Test data with local PDF file
test_data_local = {
    "documents": [r"g:\PROGRAMMING\Hackathon\Bajaj - LLM Query Retrieval\extracted_Arogya Sanjeevani Policy\text\pdf_text.txt"],
    "questions": [
        "What is the grace period for premium payment?",
        "What is the waiting period for pre-existing diseases?",
        "Does this policy cover maternity expenses?",
        "What is the No Claim Discount offered?",
        "Is there coverage for AYUSH treatments?"
    ]
}

# Test data with local PDF file for dynamic extraction
test_data_local_pdf = {
    "documents": [r"g:\PROGRAMMING\Hackathon\Bajaj - LLM Query Retrieval\pdf-extract\Arogya Sanjeevani Policy.pdf"],
    "questions": [
        "What is the grace period for premium payment?",
        "What is the waiting period for pre-existing diseases?",
        "Does this policy cover maternity expenses?",
        "What is the No Claim Discount offered?"
    ]
}

def test_api(test_type="local"):
    """
    Test the API with different document sources
    Args:
        test_type (str): "local" for extracted text, "url" for PDF URL, "pdf" for local PDF extraction
    """
    try:
        # Choose test data based on parameter
        if test_type == "local":
            test_data = test_data_local
            print("Testing with LOCAL extracted text file:")
            print(f"Document: {test_data['documents'][0]}")
        elif test_type == "pdf":
            test_data = test_data_local_pdf
            print("Testing with LOCAL PDF file (dynamic extraction):")
            print(f"Document: {test_data['documents'][0]}")
        else:  # url
            test_data = test_data_url
            print("Testing with PDF URL (dynamic download & extraction):")
            print(f"Document: {test_data['documents'][0][:80]}...")
        
        print("\n" + "-" * 60)
        
        # Test health endpoint first
        health_response = requests.get(f"{base_url}/health")
        print("Health check:", health_response.json())
        
        # Test main endpoint
        response = requests.post(
            f"{base_url}/hackrx/run",
            headers=headers,
            json=test_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*60)
            print("API Test Successful!")
            print("="*60)
            
            for answer in result["answers"]:
                print(f"\nQ: {answer['question']}")
                print(f"A: {answer['answer']}")
                print("-" * 40)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error testing API: {e}")

def test_all():
    """Test all three options"""
    print("=" * 80)
    print("TESTING LOCAL EXTRACTED TEXT FILE")
    print("=" * 80)
    test_api(test_type="local")
    
    print("\n\n" + "=" * 80)
    print("TESTING LOCAL PDF FILE (DYNAMIC EXTRACTION)")
    print("=" * 80)
    test_api(test_type="pdf")
    
    print("\n\n" + "=" * 80)
    print("TESTING PDF URL (DYNAMIC DOWNLOAD & EXTRACTION)")
    print("=" * 80)
    test_api(test_type="url")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        option = sys.argv[1].lower()
        if option == "local":
            print("Testing with LOCAL extracted text file...")
            test_api(test_type="local")
        elif option == "pdf":
            print("Testing with LOCAL PDF file...")
            test_api(test_type="pdf")
        elif option == "url":
            print("Testing with PDF URL...")
            test_api(test_type="url")
        elif option == "all":
            print("Testing ALL options...")
            test_all()
        else:
            print("Usage: python test_api.py [local|pdf|url|all]")
            print("  local - Test with local extracted text file (fastest)")
            print("  pdf   - Test with local PDF file (dynamic extraction)")
            print("  url   - Test with PDF URL (dynamic download & extraction)")
            print("  all   - Test all three options")
    else:
        print("Choose test option:")
        print("1. Test with LOCAL extracted text file (fastest)")
        print("2. Test with LOCAL PDF file (dynamic extraction)")
        print("3. Test with PDF URL (dynamic download & extraction)")
        print("4. Test ALL options")
        
        choice = input("Enter choice (1/2/3/4): ").strip()
        
        if choice == "1":
            test_api(test_type="local")
        elif choice == "2":
            test_api(test_type="pdf")
        elif choice == "3":
            test_api(test_type="url")
        elif choice == "4":
            test_all()
        else:
            print("Invalid choice. Testing with local extracted text by default...")
            test_api(test_type="local")
