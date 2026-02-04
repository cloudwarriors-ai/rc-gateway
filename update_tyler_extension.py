#!/usr/bin/env python3
"""
Update Tyler Pratt's extension to 626.
"""
import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.clients.ringcentral import RingCentralClient
from app.services.extensions import ExtensionService
from app.schemas.ringcentral import ExtensionUpdateRequest


async def update_tyler_to_626():
    """Update Tyler Pratt's extension to 626."""
    print("🎯 Updating Tyler Pratt's extension to 626...")
    
    tyler_id = "63346611031"  # Tyler Pratt's ID
    new_extension = "626"
    
    try:
        async with RingCentralClient() as client:
            service = ExtensionService(client)
            
            # First get current details
            print("📋 Getting current extension details...")
            current = await service.get_extension(tyler_id)
            print(f"   Current Extension: {current.extension_number}")
            print(f"   Name: {current.name}")
            
            # Update extension number
            print(f"\n🔄 Updating extension to {new_extension}...")
            updated = await service.update_extension_number(tyler_id, new_extension)
            
            print("✅ Update successful!")
            print(f"   Previous Extension: {current.extension_number}")
            print(f"   New Extension: {updated.extension_number}")
            print(f"   Name: {updated.name}")
            print(f"   Status: {updated.status}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error updating extension: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(update_tyler_to_626())
    sys.exit(0 if success else 1)