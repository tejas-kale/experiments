# Security Policy

## Privacy & Security Features

Secure RunPod Chat is designed with privacy and security as core principles:

### Data Protection

1. **Encrypted Communication**: All communication with RunPod instances uses SSH encryption
2. **Local History Encryption**: Chat histories are encrypted using Fernet (symmetric encryption)
3. **No Third-Party Data Sharing**: Your conversations are only between you and the RunPod instance
4. **Automatic Cleanup**: All remote data is wiped when you exit

### Security Measures

1. **API Key Protection**:
   - Never hard-code API keys
   - Use environment variables or .env files
   - Keys are never logged or transmitted except to RunPod API

2. **File Handling**:
   - Path sanitization to prevent directory traversal
   - Restricted file permissions on encryption keys (0600)
   - Automatic cleanup of uploaded files

3. **SSH Security**:
   - Uses paramiko for secure SSH connections
   - Auto-accepts host keys for RunPod instances
   - Connections timeout after inactivity

4. **Instance Isolation**:
   - Each session creates a fresh instance
   - Instances are terminated immediately on exit
   - No data persists between sessions

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please follow these steps:

### DO NOT

- Open a public GitHub issue
- Discuss the vulnerability publicly
- Exploit the vulnerability

### DO

1. Email the maintainers privately with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

2. Allow reasonable time for a fix (typically 90 days)

3. Coordinate disclosure timing with maintainers

### Response Timeline

- **24 hours**: Initial response acknowledging receipt
- **7 days**: Assessment and severity rating
- **30 days**: Fix development and testing
- **90 days**: Public disclosure (if needed)

## Security Best Practices

### For Users

1. **Protect Your API Keys**:
   ```bash
   # Good
   export RUNPOD_API_KEY="secret"

   # Bad
   --model llama --api-key secret  # Don't pass in CLI
   ```

2. **Monitor Costs**:
   ```bash
   # Set cost limits
   secure-runpod-chat --model llama --max-cost-per-hour 1.00
   ```

3. **Verify Instance Termination**:
   - Always exit properly
   - Check RunPod dashboard to confirm termination
   - Set up billing alerts

4. **Secure Chat History**:
   ```bash
   # Protect encryption key
   chmod 600 ~/.secure-runpod-chat/history/.key

   # Backup securely
   cp ~/.secure-runpod-chat/history/.key /secure/location/
   ```

5. **Review Uploaded Files**:
   - Don't upload files with secrets
   - Review files before uploading
   - Use --no-history for sensitive conversations

### For Developers

1. **Dependency Security**:
   ```bash
   # Regularly update dependencies
   pip install --upgrade -r requirements.txt

   # Check for vulnerabilities
   pip-audit
   ```

2. **Code Review**:
   - Review all code changes for security implications
   - Use static analysis tools
   - Follow secure coding practices

3. **Input Validation**:
   - Sanitize all user inputs
   - Validate file paths
   - Check command injection vectors

4. **Secret Management**:
   - Never commit secrets
   - Use .gitignore for sensitive files
   - Rotate API keys regularly

## Known Limitations

### Current Security Considerations

1. **SSH Host Key Verification**:
   - Currently auto-accepts RunPod host keys
   - Future: Implement host key verification

2. **Model Trust**:
   - Models from Hugging Face Hub are not verified
   - Use trusted models only
   - Review model code if possible

3. **Docker Image Trust**:
   - Uses public Docker images
   - Review image contents for production use

4. **Network Security**:
   - Relies on RunPod's network security
   - No additional firewall rules applied

## Compliance

### Data Residency

- Data is processed on RunPod GPU instances
- Instance location depends on RunPod datacenter availability
- Check RunPod's data residency policies for compliance

### Privacy Regulations

- **GDPR**: Chat history is stored locally, you control deletion
- **CCPA**: No data is sold or shared with third parties
- **HIPAA**: Not HIPAA compliant - don't use for PHI

## Security Checklist

Before using in production:

- [ ] API keys are stored securely
- [ ] Chat history encryption key is backed up
- [ ] Cost limits are configured
- [ ] Instance termination is verified
- [ ] Dependencies are up to date
- [ ] .env files are in .gitignore
- [ ] File uploads are reviewed
- [ ] Billing alerts are configured

## Security Updates

Subscribe to security updates:

1. Watch the GitHub repository
2. Enable GitHub security alerts
3. Check releases regularly

## Threat Model

### In Scope

- Unauthorized access to chat history
- API key exposure
- Remote code execution on local machine
- Data leakage to third parties
- Insufficient cleanup of remote data

### Out of Scope

- RunPod infrastructure security
- Hugging Face Hub security
- Model behavior and outputs
- DDoS attacks on RunPod
- Physical security of servers

## Incident Response

In case of a security incident:

1. **Immediate Actions**:
   - Rotate compromised API keys
   - Terminate all running instances
   - Delete compromised chat histories
   - Review access logs

2. **Assessment**:
   - Determine scope of breach
   - Identify affected users
   - Document timeline

3. **Recovery**:
   - Patch vulnerabilities
   - Restore from clean state
   - Update security measures

4. **Communication**:
   - Notify affected users
   - Publish security advisory
   - Update documentation

## Questions?

For security questions or concerns, please contact the maintainers privately.
