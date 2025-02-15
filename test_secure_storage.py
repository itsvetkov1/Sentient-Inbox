import unittest
from secure_storage import SecureStorageManager
import os
import shutil
from datetime import datetime, timedelta
import json
import time
from pathlib import Path

class TestSecureStorageManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.test_dir = "test_secure_storage"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.storage = SecureStorageManager(self.test_dir)
        
    def tearDown(self):
        """Clean up after each test."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_basic_operations(self):
        """Test basic record operations."""
        # Test adding a record
        email_data = {
            "message_id": "test123",
            "timestamp": datetime.now().isoformat()
        }
        record_id, success = self.storage.add_record(email_data)
        self.assertTrue(success)
        self.assertTrue(record_id)
        
        # Test checking processed status
        is_processed, success = self.storage.is_processed("test123")
        self.assertTrue(success)
        self.assertTrue(is_processed)
        
        # Test record count
        count = self.storage.get_record_count()
        self.assertEqual(count, 1)
        
    def test_data_integrity(self):
        """Test data structure verification and integrity checks."""
        # Test with valid data
        email_data = {
            "message_id": "test456",
            "timestamp": datetime.now().isoformat()
        }
        record_id, success = self.storage.add_record(email_data)
        self.assertTrue(success)
        
        # Test with invalid data
        invalid_data = None
        record_id, success = self.storage.add_record(invalid_data)
        self.assertFalse(success)
        
        # Test with empty data
        empty_data = {}
        record_id, success = self.storage.add_record(empty_data)
        self.assertFalse(success)
        
    def test_backup_restore(self):
        """Test backup creation and restoration."""
        # Add initial record
        email_data = {
            "message_id": "test789",
            "timestamp": datetime.now().isoformat()
        }
        record_id, success = self.storage.add_record(email_data)
        self.assertTrue(success)
        
        # Verify backup was created
        backup_files = list(Path(self.test_dir).glob("backups/records_backup_*.bin"))
        self.assertTrue(len(backup_files) > 0)
        
        # Store the original record
        original_record = {
            "message_id": "test789",
            "timestamp": datetime.now().isoformat()
        }
        
        # Corrupt the main data file
        with open(self.storage.record_file, 'wb') as f:
            f.write(b'corrupted data')
            
        # Verify the record is still accessible after corruption
        
        # Verify original record is still accessible
        is_processed, success = self.storage.is_processed("test789")
        self.assertTrue(success)
        self.assertTrue(is_processed)
        
    def test_key_rotation(self):
        """Test encryption key rotation."""
        # Add initial record
        email_data = {
            "message_id": "testABC",
            "timestamp": datetime.now().isoformat()
        }
        record_id, success = self.storage.add_record(email_data)
        self.assertTrue(success)
        
        # Force key rotation
        success = self.storage.rotate_key()
        self.assertTrue(success)
        
        # Verify data is still accessible
        is_processed, success = self.storage.is_processed("testABC")
        self.assertTrue(success)
        self.assertTrue(is_processed)
        
        # Verify key history
        self.assertTrue(len(self.storage.keys) <= 3)  # Should keep max 3 keys
        
    def test_error_recovery(self):
        """Test error handling and recovery mechanisms."""
        # Test with invalid message ID
        is_processed, success = self.storage.is_processed(None)
        self.assertTrue(success)  # Operation should succeed
        self.assertFalse(is_processed)  # But message not found
        
        # Test with non-existent file
        os.remove(self.storage.record_file)
        is_processed, success = self.storage.is_processed("test123")
        self.assertTrue(success)  # Should recreate file
        self.assertFalse(is_processed)
        
    def test_concurrent_operations(self):
        """Test handling of rapid consecutive operations."""
        # Add multiple records quickly
        for i in range(10):
            email_data = {
                "message_id": f"test{i}",
                "timestamp": datetime.now().isoformat()
            }
            record_id, success = self.storage.add_record(email_data)
            self.assertTrue(success)
            
        # Verify all records
        for i in range(10):
            is_processed, success = self.storage.is_processed(f"test{i}")
            self.assertTrue(success)
            self.assertTrue(is_processed)
            
    def test_cleanup(self):
        """Test automatic cleanup of old records."""
        # Add old record
        old_date = datetime.now() - timedelta(days=31)
        email_data = {
            "message_id": "old_test",
            "timestamp": old_date.isoformat()
        }
        record_id, success = self.storage.add_record(email_data, force_cleanup=True)
        self.assertTrue(success)
        
        # Add new record to trigger cleanup
        new_data = {
            "message_id": "new_test",
            "timestamp": datetime.now().isoformat()
        }
        record_id, success = self.storage.add_record(new_data, force_cleanup=True)
        self.assertTrue(success)
        
        # Verify old record was cleaned up
        is_processed, success = self.storage.is_processed("old_test")
        self.assertTrue(success)
        self.assertFalse(is_processed)
        
        # Verify new record exists
        is_processed, success = self.storage.is_processed("new_test")
        self.assertTrue(success)
        self.assertTrue(is_processed)

if __name__ == '__main__':
    unittest.main(verbosity=2)
