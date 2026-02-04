#!/usr/bin/env python3
"""
RingCentral SCIM API Tool - User provisioning without EditAccounts permission
SCIM (System for Cross-domain Identity Management) may have different permission requirements
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.clients.ringcentral import RingCentralClient
import json


class SCIMProvisioning:
    def __init__(self):
        self.client: RingCentralClient | None = None
    
    async def __aenter__(self):
        self.client = RingCentralClient()
        return self
    
    async def __aexit__(self, *args):
        if self.client:
            await self.client.close()
    
    async def create_user_scim(self, first_name: str, last_name: str, email: str, extension: str | None = None):
        """Create user via SCIM API"""
        print(f"👤 Creating user via SCIM: {first_name} {last_name}")
        
        payload = {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            "userName": email,
            "name": {
                "givenName": first_name,
                "familyName": last_name
            },
            "emails": [{
                "value": email,
                "type": "work"
            }],
            "active": True
        }
        
        if extension:
            payload["urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"] = {
                "extensionNumber": extension
            }
        
        try:
            if not self.client:
                raise RuntimeError("Client not initialized")
            response = await self.client.post('/scim/v2/Users', json=payload)
            data = response.json()
            print(f"✅ User created via SCIM!")
            print(f"   ID: {data.get('id')}")
            print(f"   Username: {data.get('userName')}")
            return data
        except Exception as e:
            print(f"❌ SCIM Error: {e}")
            return None
    
    async def list_users_scim(self):
        """List users via SCIM API"""
        print("📋 Fetching users via SCIM...")
        
        try:
            if not self.client:
                raise RuntimeError("Client not initialized")
            response = await self.client.get('/scim/v2/Users')
            data = response.json()
            
            resources = data.get('Resources', [])
            print(f"\n📊 Found {len(resources)} users via SCIM:\n")
            
            for user in resources:
                name = user.get('name', {})
                print(f"  • {name.get('givenName')} {name.get('familyName')} ({user.get('userName')})")
            
            return resources
        except Exception as e:
            print(f"❌ SCIM Error: {e}")
            return []
    
    async def update_user_scim(self, user_id: str, updates: dict):
        """Update user via SCIM API"""
        print(f"🔄 Updating user {user_id} via SCIM...")
        
        try:
            if not self.client:
                raise RuntimeError("Client not initialized")
            response = await self.client.put(f'/scim/v2/Users/{user_id}', json=updates)
            data = response.json()
            print(f"✅ User updated via SCIM!")
            return data
        except Exception as e:
            print(f"❌ SCIM Error: {e}")
            return None
    
    async def delete_user_scim(self, user_id: str):
        """Delete user via SCIM API"""
        print(f"🗑️ Deleting user {user_id} via SCIM...")
        
        try:
            if not self.client:
                raise RuntimeError("Client not initialized")
            await self.client.delete(f'/scim/v2/Users/{user_id}')
            print(f"✅ User deleted via SCIM!")
            return True
        except Exception as e:
            print(f"❌ SCIM Error: {e}")
            return False


async def test_scim_endpoints():
    """Test which SCIM endpoints work with current permissions"""
    print("🧪 Testing SCIM API endpoints...\n")
    
    async with SCIMProvisioning() as scim:
        # Test 1: List users
        print("=" * 50)
        print("TEST 1: List Users via SCIM")
        print("=" * 50)
        users = await scim.list_users_scim()
        
        print("\n" + "=" * 50)
        print("TEST 2: Create User via SCIM")
        print("=" * 50)
        result = await scim.create_user_scim(
            "SCIM", 
            "Test", 
            "scim.test@example.com",
            "9999"
        )
        
        if result:
            user_id = result.get('id')
            
            print("\n" + "=" * 50)
            print("TEST 3: Update User via SCIM")
            print("=" * 50)
            await scim.update_user_scim(user_id, {
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
                "name": {
                    "givenName": "SCIM-Updated"
                }
            })
            
            print("\n" + "=" * 50)
            print("TEST 4: Delete User via SCIM")
            print("=" * 50)
            await scim.delete_user_scim(user_id)
        
        print("\n" + "=" * 50)
        print("SCIM API Testing Complete!")
        print("=" * 50)


async def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("\n🔧 RingCentral SCIM Provisioning Tool\n")
        print("Usage:")
        print("  python scim_provisioning.py test              # Test SCIM API access")
        print("  python scim_provisioning.py list              # List users via SCIM")
        print("  python scim_provisioning.py create <first> <last> <email> [ext]")
        print("  python scim_provisioning.py delete <user_id>")
        return
    
    command = sys.argv[1]
    
    if command == "test":
        await test_scim_endpoints()
    
    elif command == "list":
        async with SCIMProvisioning() as scim:
            await scim.list_users_scim()
    
    elif command == "create":
        if len(sys.argv) < 5:
            print("Usage: create <first> <last> <email> [extension]")
            return
        async with SCIMProvisioning() as scim:
            await scim.create_user_scim(
                sys.argv[2],
                sys.argv[3],
                sys.argv[4],
                sys.argv[5] if len(sys.argv) > 5 else None
            )
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: delete <user_id>")
            return
        async with SCIMProvisioning() as scim:
            await scim.delete_user_scim(sys.argv[2])
    
    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    asyncio.run(main())
