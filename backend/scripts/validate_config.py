#!/usr/bin/env python3
"""Configuration validation utility.

This script validates configuration for different environments and reports
any issues or warnings.
"""

import argparse
import sys
from pathlib import Path

# Add the backend directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from configuration.config import Config, Environment


def validate_environment_config(env: Environment, env_file: str = None) -> bool:
    """Validate configuration for a specific environment.

    Args:
        env: Environment to validate
        env_file: Optional environment file path

    Returns:
        True if validation passes, False otherwise
    """
    print(f"\n🔍 Validating {env.value} environment...")

    try:
        config = Config.create_for_environment(env, env_file)
        print(f"✅ Configuration loaded successfully")
        print(f"   Environment: {config.environment.value}")
        print(f"   LLM Provider: {config.llm_provider.value}")
        print(f"   LLM Model: {config.llm_model}")
        print(f"   Server: {config.server_host}:{config.server_port}")
        print(f"   Debug Mode: {config.debug}")

        # Run validation checks
        warnings = config.validate_configuration()
        if warnings:
            print(f"\n⚠️  Configuration warnings:")
            for warning in warnings:
                print(f"   - {warning}")

        print(f"✅ {env.value} environment validation passed")
        return True

    except Exception as e:
        print(f"❌ {env.value} environment validation failed: {e}")
        return False


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="Validate image-catalog configuration")
    parser.add_argument(
        "--env",
        choices=["development", "test", "production", "all"],
        default="all",
        help="Environment to validate (default: all)",
    )
    parser.add_argument(
        "--env-file",
        help="Custom environment file path",
    )

    args = parser.parse_args()

    print("🚀 Image Catalog Configuration Validator")
    print("=" * 50)

    success_count = 0
    total_count = 0

    if args.env == "all":
        environments = [Environment.DEVELOPMENT, Environment.TEST, Environment.PRODUCTION]
    else:
        environments = [Environment(args.env)]

    for env in environments:
        total_count += 1
        if validate_environment_config(env, args.env_file):
            success_count += 1

    print("\n" + "=" * 50)
    print(f"📊 Validation Results: {success_count}/{total_count} environments passed")

    if success_count == total_count:
        print("🎉 All validations passed!")
        return 0
    else:
        print("💥 Some validations failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())