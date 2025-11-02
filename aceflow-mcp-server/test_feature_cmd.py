#!/usr/bin/env python3
"""
Test script for aceflow feature commands
"""

import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
try:
    from aceflow_mcp_server.cli.feature import feature_group
    from aceflow_mcp_server.contract.config import ContractConfig
    print("✅ Imports successful!")
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test ContractConfig methods
try:
    print("\n📝 Testing ContractConfig methods...")
    config = ContractConfig()

    # Test get_features
    features = config.get_features()
    print(f"  get_features(): {type(features)} - OK")

    # Test add_feature
    config.add_feature('test', {'enabled': True})
    print("  add_feature() - OK")

    # Test get_feature
    feature = config.get_feature('test')
    print(f"  get_feature(): {feature} - OK")

    # Test remove_feature
    config.remove_feature('test')
    print("  remove_feature() - OK")

    print("✅ All ContractConfig tests passed!")

except Exception as e:
    print(f"❌ Test error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All tests passed!")
