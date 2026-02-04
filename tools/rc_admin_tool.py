#!/usr/bin/env python3
"""
RingCentral Admin Tool - Alternative to API for restricted operations
Uses direct SDK calls with elevated permissions
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ringcentral import SDK
import json


class RingCentralAdminTool:
    def __init__(self, config_path: str = "config/rc_credentials.json"):
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.sdk = SDK(
            self.config['client_id'],
            self.config['client_secret'],
            self.config['base_url']
        )
        self.platform = self.sdk.platform()
    
    def login(self):
        """Login using JWT"""
        print("🔐 Authenticating with RingCentral...")
        self.platform.login(jwt=self.config['jwt'])
        print("✅ Authenticated successfully!")
    
    def create_user(self, first_name: str, last_name: str, email: str, extension: str | None = None):
        """Create a new user extension"""
        print(f"👤 Creating user: {first_name} {last_name}")
        
        payload = {
            "contact": {
                "firstName": first_name,
                "lastName": last_name,
                "email": email
            },
            "extensionNumber": extension,
            "type": "User",
            "status": "Enabled"
        }
        
        try:
            response = self.platform.post('/restapi/v1.0/account/~/extension', payload)
            data = response.json_dict()
            print(f"✅ User created successfully!")
            print(f"   ID: {data.get('id')}")
            print(f"   Extension: {data.get('extensionNumber')}")
            return data
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def list_users(self, per_page: int = 50):
        """List all user extensions"""
        print("📋 Fetching users...")
        
        try:
            response = self.platform.get('/restapi/v1.0/account/~/extension', {
                'type': 'User',
                'perPage': per_page
            })
            data = response.json_dict()
            
            print(f"\n📊 Found {len(data.get('records', []))} users:\n")
            for user in data.get('records', []):
                print(f"  • {user.get('name')} (Ext: {user.get('extensionNumber')}) - {user.get('status')}")
            
            return data.get('records', [])
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def update_user_extension(self, extension_id: str, new_extension: str):
        """Update user's extension number"""
        print(f"🔄 Updating extension for user {extension_id} to {new_extension}")
        
        try:
            response = self.platform.put(
                f'/restapi/v1.0/account/~/extension/{extension_id}',
                {'extensionNumber': new_extension}
            )
            data = response.json()
            print(f"✅ Extension updated successfully!")
            return data
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def bulk_create_users(self, users_csv: str):
        """Bulk create users from CSV file"""
        import csv
        
        print(f"📦 Bulk creating users from {users_csv}")
        
        created = []
        failed = []
        
        with open(users_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                result = self.create_user(
                    row['firstName'],
                    row['lastName'],
                    row['email'],
                    row.get('extension')
                )
                if result:
                    created.append(result)
                else:
                    failed.append(row)
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Created: {len(created)}")
        print(f"   ❌ Failed: {len(failed)}")
        
        return created, failed
    
    def create_call_queue(self, name: str, extension: str, member_ids: list):
        """Create a call queue"""
        print(f"📞 Creating call queue: {name}")
        
        payload = {
            "name": name,
            "extensionNumber": extension,
            "members": [{"id": mid} for mid in member_ids]
        }
        
        try:
            response = self.platform.post('/restapi/v1.0/account/~/call-queues', payload)
            data = response.json()
            print(f"✅ Call queue created successfully!")
            print(f"   ID: {data.get('id')}")
            print(f"   Extension: {data.get('extensionNumber')}")
            return data
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def create_ivr_menu(self, name: str, extension: str, keys_config: dict):
        """Create an IVR menu"""
        print(f"🎛️ Creating IVR menu: {name}")
        
        payload = {
            "name": name,
            "extensionNumber": extension,
            "prompt": {"mode": "Audio"},
            "actions": keys_config
        }
        
        try:
            response = self.platform.post('/restapi/v1.0/account/~/ivr-menus', payload)
            data = response.json()
            print(f"✅ IVR menu created successfully!")
            return data
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_account_info(self):
        """Get account information"""
        print("🏢 Fetching account info...")
        
        try:
            response = self.platform.get('/restapi/v1.0/account/~')
            data = response.json_dict()
            
            print(f"\n📊 Account Information:")
            print(f"   Company: {data.get('name', 'N/A')}")
            print(f"   ID: {data.get('id', 'N/A')}")
            print(f"   Main Number: {data.get('mainNumber', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            
            return data
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """CLI interface"""
    tool = RingCentralAdminTool()
    tool.login()
    
    if len(sys.argv) < 2:
        print("\n🔧 RingCentral Admin Tool\n")
        print("Usage:")
        print("  python rc_admin_tool.py list-users")
        print("  python rc_admin_tool.py create-user <first> <last> <email> [extension]")
        print("  python rc_admin_tool.py update-extension <user_id> <new_ext>")
        print("  python rc_admin_tool.py account-info")
        print("  python rc_admin_tool.py bulk-create <users.csv>")
        return
    
    command = sys.argv[1]
    
    if command == "list-users":
        tool.list_users()
    
    elif command == "create-user":
        if len(sys.argv) < 5:
            print("Usage: create-user <first> <last> <email> [extension]")
            return
        tool.create_user(
            sys.argv[2],
            sys.argv[3],
            sys.argv[4],
            sys.argv[5] if len(sys.argv) > 5 else None
        )
    
    elif command == "update-extension":
        if len(sys.argv) < 4:
            print("Usage: update-extension <user_id> <new_extension>")
            return
        tool.update_user_extension(sys.argv[2], sys.argv[3])
    
    elif command == "account-info":
        tool.get_account_info()
    
    elif command == "bulk-create":
        if len(sys.argv) < 3:
            print("Usage: bulk-create <users.csv>")
            return
        tool.bulk_create_users(sys.argv[2])
    
    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()
