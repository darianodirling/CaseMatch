#!/usr/bin/env python3
"""
Mock data that matches the actual topic_vectors table structure
Used for development when CAS server is not accessible
"""

import random
import uuid

def generate_mock_topic_vectors(num_rows=10):
    """
    Generate mock data matching the actual topic_vectors table structure
    Based on the columns seen in the SAS Data Explorer screenshot
    """
    mock_data = []
    
    for i in range(num_rows):
        row = {
            "__uniqueid__": str(uuid.uuid4())[:8],
            "Case Number": f"CS{10000000 + i}",
            "Assignment Group": random.choice(["IT Support", "Network Team", "Database Team", "Security Team"]),
            "Resolution": random.choice([
                "Issue resolved by restarting the service",
                "Configuration updated to resolve performance issue", 
                "User access permissions corrected",
                "Network connectivity restored",
                "Database query optimized"
            ]),
            "Concern": random.choice([
                "System performance degradation",
                "User unable to access application",
                "Database connection timeout",
                "Network connectivity issues",
                "Authentication failure"
            ]),
            "Description": random.choice([
                "User reported slow system response times during peak hours",
                "Application throwing connection errors intermittently",
                "Database queries taking longer than expected to execute",
                "Users experiencing timeout errors when logging in",
                "Network latency affecting application performance"
            ]),
            # Topic vectors - realistic values between 0 and 1
            "_TextTopic_1": round(random.uniform(0.1, 0.9), 4),
            "_TextTopic_2": round(random.uniform(0.1, 0.9), 4),
            "_TextTopic_3": round(random.uniform(0.1, 0.9), 4),
            "_TextTopic_4": round(random.uniform(0.1, 0.9), 4),
            "_TextTopic_5": round(random.uniform(0.1, 0.9), 4),
            # Additional columns
            "_Col1_": round(random.uniform(0.0, 1.0), 4),
            "_Col2_": round(random.uniform(0.0, 1.0), 4),
            "_Col3_": round(random.uniform(0.0, 1.0), 4),
            "_Col4_": round(random.uniform(0.0, 1.0), 4),
            "_Col5_": round(random.uniform(0.0, 1.0), 4)
        }
        mock_data.append(row)
    
    return mock_data

def get_sample_case_numbers():
    """Get list of sample case numbers for testing"""
    return [f"CS{10000000 + i}" for i in range(10)]