#!/usr/bin/env python3
"""
Test script for phonetic alphabet conversion and ticket number formatting
"""
from api import convert_phonetic_to_letters, format_ticket_number_for_speech

def test_ticket_number_formatting():
    """Test the ticket number speech formatting function"""
    
    test_cases = [
        ("INC190244", "INC1 9 zero 2 4 4"),
        ("INC000123", "INCzero zero zero 1 2 3"),
        ("INC100200", "INC1 zero zero 2 zero zero"),
        ("TICKET001", "TICKETzero zero 1"),
        ("", ""),  # Empty string
        ("ABC123", "ABC1 2 3"),  # No zeros
    ]
    
    print("Testing Ticket Number Speech Formatting")
    print("=" * 50)
    
    all_passed = True
    
    for input_text, expected in test_cases:
        result = format_ticket_number_for_speech(input_text)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | Input: '{input_text}' -> Output: '{result}' (Expected: '{expected}')")
    
    print("=" * 50)
    if all_passed:
        print("🎉 All ticket formatting tests passed!")
    else:
        print("⚠️  Some ticket formatting tests failed!")
    
    return all_passed

def test_phonetic_conversion():
    """Test the phonetic alphabet conversion function"""
    
    test_cases = [
        ("Golf-Delta-Kilo-7575", "GDK7575"),
        ("Alpha-Bravo-Charlie", "ABC"),
        ("Hotel-Echo-Lima-Papa", "HELP"),
        ("Mike-Yankee-Papa-Charlie-123", "MYPC123"),
        ("golf delta kilo 7575", "GDK7575"),
        ("GOLF-DELTA-KILO-7575", "GDK7575"),
        ("Regular-Computer-Name", "REGULAR-COMPUTER-NAME"),  # Non-phonetic should stay as-is
        ("", ""),  # Empty string
        ("123-456", "123456"),  # Numbers only
    ]
    
    print("Testing Phonetic Alphabet Conversion")
    print("=" * 50)
    
    all_passed = True
    
    for input_text, expected in test_cases:
        result = convert_phonetic_to_letters(input_text)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | Input: '{input_text}' -> Output: '{result}' (Expected: '{expected}')")
    
    print("=" * 50)
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed!")
    
    return all_passed

if __name__ == "__main__":
    print("Running all tests...\n")
    
    # Test ticket number formatting
    ticket_passed = test_ticket_number_formatting()
    print()
    
    # Test phonetic conversion
    phonetic_passed = test_phonetic_conversion()
    print()
    
    # Overall results
    print("=" * 50)
    if ticket_passed and phonetic_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED!")
        if not ticket_passed:
            print("   - Ticket number formatting tests failed")
        if not phonetic_passed:
            print("   - Phonetic alphabet conversion tests failed")
