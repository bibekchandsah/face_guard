# 🔑 Security Key System Guide

## Overview

The Security Key System allows trusted users to temporarily disable security alerts by entering a pre-configured security key. This is useful when you have trusted individuals (family, colleagues, etc.) who need temporary access without triggering false alarms.

## ✅ Implementation Status: **FULLY IMPLEMENTED**

The security key system has been completely implemented with the following components:

### 🔧 Core Functionality
- **Secure Key Storage**: Keys are hashed using SHA-256 and stored in `face_guard_data/security_key.json`
- **Session Management**: Trusted sessions with configurable timeouts
- **Automatic Timeout**: Sessions automatically expire after the configured duration
- **Status Monitoring**: Real-time status tracking and reporting
- **Integration**: Seamlessly integrated with the main face detection system

### 📁 File Structure

#### `face_guard_data/security_key.json`
```json
{
    "security_key_hash": "hashed_key_value",
    "security_key_enabled": true,
    "security_key_timeout": 600,
    "trusted_session_active": false,
    "trusted_session_start": 0,
    "trusted_user_name": "",
    "last_updated": "2025-09-01 12:39:03",
    "creation_date": "2025-09-01 12:39:03"
}
```

### 🎯 Key Features

#### Security Key Management
- **Set Security Key**: Configure a secure key with custom timeout
- **Key Verification**: SHA-256 hashed key verification
- **Timeout Configuration**: 1 minute to 2 hours (120 minutes)
- **Enable/Disable**: Can be enabled or disabled as needed

#### Trusted Sessions
- **Session Start**: Begin trusted session with user identification
- **Session Monitoring**: Real-time session status and remaining time
- **Auto-Timeout**: Automatic session expiration
- **Manual End**: Ability to end sessions early

#### Security Integration
- **Alert Suppression**: Disables unknown face alerts during trusted sessions
- **Logging**: All security key operations are logged
- **Status Display**: Visual feedback for session status

## 🚀 How to Use

### Setting Up Security Key

1. **Open Camera Preview**: Press `Ctrl+Shift+C` or use system tray
2. **Click "🔑 Set Security Key"** button
3. **Enter Security Key**: Minimum 4 characters, choose something secure
4. **Set Timeout**: Choose duration (1-120 minutes, default 10 minutes)
5. **Confirm**: Key is hashed and saved securely

### Starting a Trusted Session

1. **Click "📊 Security Status"** button in camera preview
2. **Click "🔑 Enter Security Key"** in the status dialog
3. **Enter Your Key**: Type the security key you configured
4. **Enter User Name**: Identify yourself for logging purposes
5. **Session Active**: Security alerts are now disabled for the timeout period

### Managing Sessions

#### Check Status
- **Security Status Dialog**: Shows current session status, remaining time, configuration
- **System Tray**: Status updates appear as toast notifications
- **Logs**: All operations are logged with timestamps

#### End Session Early
- **Manual End**: Use "🚪 End Session" button in status dialog
- **Automatic End**: Session ends automatically when timeout reached

## 🔍 Technical Details

### Security Features

#### Key Security
- **SHA-256 Hashing**: Keys are never stored in plain text
- **Salt-free Design**: Uses consistent hashing for verification
- **Minimum Length**: 4 character minimum requirement
- **Case Sensitive**: Keys are case-sensitive for better security

#### Session Security
- **Time-based Expiration**: Sessions automatically expire
- **User Identification**: Each session is associated with a user name
- **Audit Trail**: All operations logged with timestamps
- **Status Persistence**: Session state survives application restarts

### Integration Points

#### Main Detection Loop
```python
# In main detection loop
if face_boxes and not owner_here:
    security_status = get_security_key_status()
    
    if security_status['session_active']:
        # Skip security alerts - trusted session active
        log(f"Unknown face detected but trusted session active")
    else:
        # Normal security measures
        self.on_toast("🚨 UNKNOWN FACE DETECTED", "red")
```

#### Timeout Monitoring
```python
# Automatic timeout checking in main loop
def check_security_key_timeout(self):
    timed_out, message = check_trusted_session_timeout()
    if timed_out:
        self.on_toast("🔑 Trusted session expired", "orange")
```

### Core Functions

#### Key Management
- `set_security_key(key, timeout_minutes)`: Set new security key
- `verify_security_key(key)`: Verify entered key against stored hash
- `hash_security_key(key)`: Generate SHA-256 hash of key

#### Session Management
- `start_trusted_session(user_name)`: Start new trusted session
- `end_trusted_session()`: End current session
- `check_trusted_session_timeout()`: Check for session timeout

#### Status & Data
- `get_security_key_status()`: Get comprehensive status information
- `load_security_key_data()`: Load data from JSON file
- `save_security_key_data(data)`: Save data to JSON file

## 🖥️ User Interface

### Camera Preview Buttons
- **🔑 Set Security Key**: Configure new security key and timeout
- **📊 Security Status**: View current status and manage sessions

### Security Status Dialog
- **Real-time Status**: Shows configuration, session status, remaining time
- **🔄 Refresh**: Update status display
- **🔑 Enter Security Key**: Start new trusted session
- **🚪 End Session**: End current session early
- **✅ Close**: Close dialog

### Status Information Display
```
🔑 SECURITY KEY STATUS
==================================================

🔧 Configuration:
   • Enabled: ✅ Yes
   • Configured: ✅ Yes
   • Timeout: 10 minutes
   • Created: 2025-09-01 12:39:03
   • Updated: 2025-09-01 12:39:03

🎯 Current Session:
   • Status: 🟢 ACTIVE
   • User: John Doe
   • Remaining: 8 minutes
   • Security alerts: 🔕 DISABLED
```

## 🧪 Testing

Comprehensive testing suite included:

```bash
python test_security_key.py
```

**Test Coverage**:
- ✅ Security key creation and storage
- ✅ Key verification and authentication  
- ✅ Trusted session management
- ✅ Session timeout handling
- ✅ JSON file structure and persistence
- ✅ Status reporting and monitoring

## 📝 Usage Examples

### Example 1: Family Member Visit
1. Set security key: "family2025" with 30-minute timeout
2. When family member arrives, they enter the key
3. Security alerts disabled for 30 minutes
4. System logs: "Trusted session started for 'Mom'"
5. After 30 minutes, session auto-expires

### Example 2: Office Environment
1. Set security key: "office_secure" with 60-minute timeout
2. Colleague enters key when working late
3. No false alarms during their work session
4. Manual session end when leaving early
5. Full audit trail maintained

### Example 3: Service Personnel
1. Set security key: "service123" with 15-minute timeout
2. Maintenance person enters key upon arrival
3. Short timeout ensures security after they leave
4. System automatically re-enables alerts
5. All activity logged for security review

## 🚨 Important Security Notes

### Best Practices
1. **Choose Strong Keys**: Use complex, unique security keys
2. **Appropriate Timeouts**: Set timeouts based on expected visit duration
3. **Regular Updates**: Change security keys periodically
4. **Monitor Logs**: Review security key usage regularly
5. **User Training**: Ensure trusted users understand the system

### Security Considerations
1. **Key Sharing**: Only share keys with truly trusted individuals
2. **Timeout Settings**: Shorter timeouts are more secure
3. **Session Monitoring**: Check active sessions regularly
4. **Log Review**: Monitor for unauthorized key usage
5. **Emergency Override**: Owner presence always overrides security key sessions

## ✅ Feature Complete

The security key system is **fully implemented and production-ready**. Users can:

- ✅ Set secure keys with custom timeouts
- ✅ Start and manage trusted sessions
- ✅ Monitor session status in real-time
- ✅ Benefit from automatic timeout protection
- ✅ Maintain full audit trails
- ✅ Integrate seamlessly with existing security features

The system provides a perfect balance between security and convenience, allowing trusted access while maintaining comprehensive monitoring and automatic protection.