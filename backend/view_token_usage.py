#!/usr/bin/env python3
"""
Token Usage Viewer
Utility script to view and analyze token usage data
"""

import argparse
import json
from datetime import datetime, timedelta
from db_token_usage import token_db

def print_usage_summary(summary):
    """Print formatted usage summary"""
    print("\n" + "="*60)
    print("TOKEN USAGE SUMMARY")
    print("="*60)
    
    # Print totals
    totals = summary.get("totals", {})
    print(f"Total Sessions: {totals.get('sessions', 0)}")
    print(f"Total Input Tokens: {totals.get('input_tokens', 0):,}")
    print(f"Total Output Tokens: {totals.get('output_tokens', 0):,}")
    print(f"Total Tokens: {totals.get('total_tokens', 0):,}")
    
    # Print by service
    print("\nBY SERVICE:")
    print("-" * 40)
    
    for service_type, models in summary.get("by_service", {}).items():
        print(f"\n{service_type.upper()} SERVICE:")
        for model_name, stats in models.items():
            print(f"  Model: {model_name}")
            print(f"    Sessions: {stats.get('session_count', 0)}")
            print(f"    Input Tokens: {stats.get('input_tokens', 0):,}")
            print(f"    Output Tokens: {stats.get('output_tokens', 0):,}")
            print(f"    Total Tokens: {stats.get('total_tokens', 0):,}")
            print(f"    Avg Tokens/Session: {stats.get('avg_tokens_per_session', 0)}")

def print_session_details(session_id):
    """Print detailed information for a specific session"""
    records = token_db.get_session_usage(session_id)
    
    if not records:
        print(f"No records found for session: {session_id}")
        return
    
    print("\n" + "="*60)
    print(f"SESSION DETAILS: {session_id}")
    print("="*60)
    
    total_input = 0
    total_output = 0
    
    for record in records:
        print(f"\nService: {record.service_type.upper()}")
        print(f"Model: {record.model_name}")
        print(f"User: {record.user_name}")
        print(f"Input Tokens: {record.input_tokens:,}")
        print(f"Output Tokens: {record.output_tokens:,}")
        print(f"Total Tokens: {record.total_tokens:,}")
        print(f"Session Start: {record.session_start}")
        print(f"Session End: {record.session_end}")
        
        total_input += record.input_tokens
        total_output += record.output_tokens
    
    print(f"\nSESSION TOTALS:")
    print(f"Total Input Tokens: {total_input:,}")
    print(f"Total Output Tokens: {total_output:,}")
    print(f"Total Tokens: {total_input + total_output:,}")

def main():
    parser = argparse.ArgumentParser(description="View token usage data")
    parser.add_argument("--summary", action="store_true", help="Show usage summary")
    parser.add_argument("--session", type=str, help="Show details for specific session ID")
    parser.add_argument("--days", type=int, default=7, help="Number of days to include (default: 7)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.session:
        # Show specific session details
        print_session_details(args.session)
    else:
        # Show summary
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
        
        summary = token_db.get_usage_summary(start_date, end_date)
        
        if args.json:
            print(json.dumps(summary, indent=2, default=str))
        else:
            print(f"\nShowing usage for last {args.days} days")
            print(f"From: {start_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"To: {end_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print_usage_summary(summary)

if __name__ == "__main__":
    main()
