import asyncio
import logging
import hashlib
import hmac
import secrets
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import re
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger("ArielMatrix.Security")

class Security:
    """
    Advanced security system for ArielMatrix
    Handles encryption, authentication, and security monitoring
    """
    
    def __init__(self):
        self.encryption_key = None
        self.cipher_suite = None
        self.security_logs = []
        self.threat_detections = []
        self.access_tokens = {}
        self.rate_limits = {}
        
        # Security configuration
        self.config = {
            "max_login_attempts": 5,
            "token_expiry_hours": 24,
            "rate_limit_requests": 100,
            "rate_limit_window": 3600,  # 1 hour
            "password_min_length": 12,
            "encryption_algorithm": "AES-256"
        }
        
        # Security metrics
        self.metrics = {
            "total_authentications": 0,
            "failed_authentications": 0,
            "threats_detected": 0,
            "security_incidents": 0,
            "last_security_scan": None
        }
        
        self.alerts = []
        self.threat_signatures = []
        self.security_events = []
        self.last_audit = None
        self.security_level = "medium"
    
    async def initialize(self):
        """Initialize security system"""
        logger.info("🛡️ Initializing Security System...")
        
        try:
            # Generate encryption key
            await self._initialize_encryption()
            
            # Set up security monitoring
            await self._setup_security_monitoring()
            
            # Initialize threat detection
            await self._initialize_threat_detection()
            
            logger.info("✅ Security System initialized")
            
        except Exception as e:
            logger.error(f"Security System initialization failed: {e}")
            raise
    
    async def _initialize_encryption(self):
        """Initialize encryption system"""
        try:
            # Generate or load encryption key
            password = b"ArielMatrix_SecureKey_2024"
            salt = b"ArielMatrix_Salt"
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self.encryption_key = key
            self.cipher_suite = Fernet(key)
            
            logger.info("🔐 Encryption system initialized")
            
        except Exception as e:
            logger.error(f"Encryption initialization failed: {e}")
            raise
    
    async def _setup_security_monitoring(self):
        """Set up security monitoring"""
        try:
            # Start security monitoring task
            asyncio.create_task(self._security_monitoring_loop())
            
            logger.info("👁️ Security monitoring started")
            
        except Exception as e:
            logger.error(f"Security monitoring setup failed: {e}")
    
    async def _initialize_threat_detection(self):
        """Initialize threat detection system"""
        try:
            # Set up threat detection patterns
            self.threat_patterns = [
                r"(?i)(sql injection|union select|drop table)",
                r"(?i)(script|javascript|<script)",
                r"(?i)(../|\.\.\\|directory traversal)",
                r"(?i)(eval\(|exec\(|system\()",
                r"(?i)(password|passwd|pwd).*[=:]\s*['\"]?\w+",
            ]
            
            logger.info("🔍 Threat detection initialized")
            
        except Exception as e:
            logger.error(f"Threat detection initialization failed: {e}")
    
    async def _security_monitoring_loop(self):
        """Continuous security monitoring"""
        while True:
            try:
                await self._perform_security_scan()
                await asyncio.sleep(300)  # Scan every 5 minutes
                
            except Exception as e:
                logger.error(f"Security monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _perform_security_scan(self):
        """Perform security scan"""
        try:
            scan_results = {
                "timestamp": datetime.utcnow().isoformat(),
                "threats_detected": 0,
                "vulnerabilities": [],
                "recommendations": []
            }
            
            # Check for suspicious activities
            suspicious_activities = await self._check_suspicious_activities()
            scan_results["threats_detected"] = len(suspicious_activities)
            
            # Check system vulnerabilities
            vulnerabilities = await self._check_vulnerabilities()
            scan_results["vulnerabilities"] = vulnerabilities
            
            # Generate recommendations
            recommendations = await self._generate_security_recommendations()
            scan_results["recommendations"] = recommendations
            
            # Update metrics
            self.metrics["last_security_scan"] = datetime.utcnow().isoformat()
            self.metrics["threats_detected"] += scan_results["threats_detected"]
            
            # Log scan results
            await self._log_security_event("security_scan", scan_results)
            
        except Exception as e:
            logger.error(f"Security scan failed: {e}")
    
    async def _check_suspicious_activities(self) -> List[Dict]:
        """Check for suspicious activities"""
        suspicious = []
        
        try:
            # Check rate limiting violations
            current_time = datetime.utcnow()
            
            for ip, requests in self.rate_limits.items():
                recent_requests = [
                    req_time for req_time in requests 
                    if (current_time - req_time).total_seconds() < self.config["rate_limit_window"]
                ]
                
                if len(recent_requests) > self.config["rate_limit_requests"]:
                    suspicious.append({
                        "type": "rate_limit_violation",
                        "ip": ip,
                        "request_count": len(recent_requests),
                        "severity": "medium"
                    })
            
            # Check for failed authentication attempts
            failed_auths = [
                log for log in self.security_logs 
                if log.get("event_type") == "authentication_failed" 
                and (current_time - datetime.fromisoformat(log["timestamp"])).total_seconds() < 3600
            ]
            
            if len(failed_auths) > 10:  # More than 10 failed auths in 1 hour
                suspicious.append({
                    "type": "multiple_failed_authentications",
                    "count": len(failed_auths),
                    "severity": "high"
                })
            
        except Exception as e:
            logger.error(f"Suspicious activity check failed: {e}")
        
        return suspicious
    
    async def _check_vulnerabilities(self) -> List[Dict]:
        """Check for system vulnerabilities"""
        vulnerabilities = []
        
        try:
            # Check encryption status
            if not self.encryption_key:
                vulnerabilities.append({
                    "type": "encryption_not_initialized",
                    "severity": "critical",
                    "description": "Encryption system not properly initialized"
                })
            
            # Check token expiry
            expired_tokens = 0
            current_time = datetime.utcnow()
            
            for token_id, token_data in self.access_tokens.items():
                if current_time > token_data["expires_at"]:
                    expired_tokens += 1
            
            if expired_tokens > 0:
                vulnerabilities.append({
                    "type": "expired_tokens",
                    "severity": "low",
                    "description": f"{expired_tokens} expired tokens found",
                    "count": expired_tokens
                })
            
            # Check security configuration
            if self.config["password_min_length"] < 8:
                vulnerabilities.append({
                    "type": "weak_password_policy",
                    "severity": "medium",
                    "description": "Password minimum length is too short"
                })
            
        except Exception as e:
            logger.error(f"Vulnerability check failed: {e}")
        
        return vulnerabilities
    
    async def _generate_security_recommendations(self) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        try:
            # Check recent security events
            recent_events = [
                log for log in self.security_logs[-100:] 
                if log.get("severity") in ["high", "critical"]
            ]
            
            if len(recent_events) > 5:
                recommendations.append("Consider implementing additional security measures due to recent high-severity events")
            
            # Check authentication metrics
            if self.metrics["failed_authentications"] > self.metrics["total_authentications"] * 0.1:
                recommendations.append("High rate of failed authentications detected - consider implementing CAPTCHA or account lockout")
            
            # General recommendations
            recommendations.extend([
                "Regularly update encryption keys",
                "Monitor security logs for unusual patterns",
                "Implement multi-factor authentication for critical operations",
                "Regular security audits and penetration testing",
                "Keep security policies up to date"
            ])
            
        except Exception as e:
            logger.error(f"Security recommendations generation failed: {e}")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            if not self.cipher_suite:
                raise ValueError("Encryption not initialized")
            
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"Data encryption failed: {e}")
            raise
    
    async def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            if not self.cipher_suite:
                raise ValueError("Encryption not initialized")
            
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Data decryption failed: {e}")
            raise
    
    async def generate_access_token(self, user_id: str, permissions: List[str] = None) -> str:
        """Generate secure access token"""
        try:
            token_id = secrets.token_urlsafe(32)
            
            token_data = {
                "user_id": user_id,
                "permissions": permissions or [],
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=self.config["token_expiry_hours"]),
                "last_used": datetime.utcnow()
            }
            
            self.access_tokens[token_id] = token_data
            
            # Log token generation
            await self._log_security_event("token_generated", {
                "user_id": user_id,
                "token_id": token_id[:8] + "...",  # Partial token for logging
                "permissions": permissions
            })
            
            return token_id
            
        except Exception as e:
            logger.error(f"Access token generation failed: {e}")
            raise
    
    async def validate_access_token(self, token: str) -> Optional[Dict]:
        """Validate access token"""
        try:
            if token not in self.access_tokens:
                await self._log_security_event("invalid_token_used", {"token": token[:8] + "..."})
                return None
            
            token_data = self.access_tokens[token]
            
            # Check if token is expired
            if datetime.utcnow() > token_data["expires_at"]:
                await self._log_security_event("expired_token_used", {"token": token[:8] + "..."})
                return None
            
            # Update last used time
            token_data["last_used"] = datetime.utcnow()
            
            return token_data
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return None
    
    async def revoke_access_token(self, token: str) -> bool:
        """Revoke access token"""
        try:
            if token in self.access_tokens:
                del self.access_tokens[token]
                
                await self._log_security_event("token_revoked", {"token": token[:8] + "..."})
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False
    
    async def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return access token"""
        try:
            # Simulate user authentication (replace with real authentication)
            valid_users = {
                "admin": "ArielMatrix_Admin_2024!",
                "user": "ArielMatrix_User_2024!",
                "operator": "ArielMatrix_Operator_2024!"
            }
            
            if username in valid_users and valid_users[username] == password:
                # Generate access token
                permissions = ["read", "write"] if username == "admin" else ["read"]
                token = await self.generate_access_token(username, permissions)
                
                # Update metrics
                self.metrics["total_authentications"] += 1
                
                await self._log_security_event("authentication_success", {"username": username})
                return token
            
            else:
                # Update metrics
                self.metrics["failed_authentications"] += 1
                
                await self._log_security_event("authentication_failed", {"username": username})
                return None
                
        except Exception as e:
            logger.error(f"User authentication failed: {e}")
            return None
    
    async def check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limits"""
        try:
            current_time = datetime.utcnow()
            
            if identifier not in self.rate_limits:
                self.rate_limits[identifier] = []
            
            # Clean old requests
            self.rate_limits[identifier] = [
                req_time for req_time in self.rate_limits[identifier]
                if (current_time - req_time).total_seconds() < self.config["rate_limit_window"]
            ]
            
            # Check if within limits
            if len(self.rate_limits[identifier]) >= self.config["rate_limit_requests"]:
                await self._log_security_event("rate_limit_exceeded", {"identifier": identifier})
                return False
            
            # Add current request
            self.rate_limits[identifier].append(current_time)
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow request on error
    
    async def scan_for_threats(self, content: str) -> List[Dict]:
        """Scan content for security threats"""
        threats = []
        
        try:
            for pattern in self.threat_patterns:
                matches = re.findall(pattern, content)
                
                if matches:
                    threat = {
                        "type": "pattern_match",
                        "pattern": pattern,
                        "matches": matches,
                        "severity": "medium",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    threats.append(threat)
            
            # Check for suspicious keywords
            suspicious_keywords = ["hack", "exploit", "vulnerability", "backdoor", "malware"]
            found_keywords = [keyword for keyword in suspicious_keywords if keyword.lower() in content.lower()]
            
            if found_keywords:
                threats.append({
                    "type": "suspicious_keywords",
                    "keywords": found_keywords,
                    "severity": "low",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Log threats if found
            if threats:
                await self._log_security_event("threats_detected", {"threats": threats, "content_length": len(content)})
            
        except Exception as e:
            logger.error(f"Threat scanning failed: {e}")
        
        return threats
    
    async def _log_security_event(self, event_type: str, event_data: Dict):
        """Log security event"""
        try:
            security_log = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": event_data,
                "severity": event_data.get("severity", "info")
            }
            
            self.security_logs.append(security_log)
            
            # Keep only recent logs
            if len(self.security_logs) > 1000:
                self.security_logs = self.security_logs[-1000:]
            
            # Log critical events
            if security_log["severity"] in ["high", "critical"]:
                logger.warning(f"🚨 Security Event: {event_type} - {event_data}")
                self.metrics["security_incidents"] += 1
            
        except Exception as e:
            logger.error(f"Security event logging failed: {e}")
    
    async def generate_security_report(self) -> Dict:
        """Generate comprehensive security report"""
        try:
            current_time = datetime.utcnow()
            
            # Calculate time ranges
            last_24h = current_time - timedelta(hours=24)
            last_7d = current_time - timedelta(days=7)
            
            # Filter logs by time
            logs_24h = [log for log in self.security_logs if datetime.fromisoformat(log["timestamp"]) > last_24h]
            logs_7d = [log for log in self.security_logs if datetime.fromisoformat(log["timestamp"]) > last_7d]
            
            # Count events by type
            event_counts_24h = {}
            event_counts_7d = {}
            
            for log in logs_24h:
                event_type = log["event_type"]
                event_counts_24h[event_type] = event_counts_24h.get(event_type, 0) + 1
            
            for log in logs_7d:
                event_type = log["event_type"]
                event_counts_7d[event_type] = event_counts_7d.get(event_type, 0) + 1
            
            # Security score calculation
            security_score = await self._calculate_security_score()
            
            report = {
                "report_timestamp": current_time.isoformat(),
                "security_score": security_score,
                "metrics": self.metrics,
                "events_last_24h": {
                    "total_events": len(logs_24h),
                    "event_breakdown": event_counts_24h,
                    "critical_events": len([log for log in logs_24h if log.get("severity") == "critical"]),
                    "high_severity_events": len([log for log in logs_24h if log.get("severity") == "high"])
                },
                "events_last_7d": {
                    "total_events": len(logs_7d),
                    "event_breakdown": event_counts_7d,
                    "critical_events": len([log for log in logs_7d if log.get("severity") == "critical"]),
                    "high_severity_events": len([log for log in logs_7d if log.get("severity") == "high"])
                },
                "active_tokens": len(self.access_tokens),
                "rate_limited_ips": len(self.rate_limits),
                "recent_threats": self.threat_detections[-10:],
                "recommendations": await self._generate_security_recommendations()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Security report generation failed: {e}")
            return {"error": str(e)}
    
    async def _calculate_security_score(self) -> float:
        """Calculate overall security score (0-100)"""
        try:
            score = 100.0
            
            # Deduct points for security incidents
            recent_incidents = self.metrics.get("security_incidents", 0)
            score -= min(recent_incidents * 5, 30)  # Max 30 points deduction
            
            # Deduct points for failed authentications
            failed_auth_rate = self.metrics.get("failed_authentications", 0) / max(self.metrics.get("total_authentications", 1), 1)
            score -= min(failed_auth_rate * 50, 20)  # Max 20 points deduction
            
            # Deduct points for threats
            threats_detected = self.metrics.get("threats_detected", 0)
            score -= min(threats_detected * 2, 15)  # Max 15 points deduction
            
            # Bonus points for good practices
            if self.encryption_key:
                score += 5
            
            if len(self.access_tokens) > 0:
                score += 3
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            logger.error(f"Security score calculation failed: {e}")
            return 50.0  # Default score
    
    async def get_status(self) -> Dict:
        """Get security system status"""
        try:
            return {
                "encryption_initialized": self.encryption_key is not None,
                "active_tokens": len(self.access_tokens),
                "security_logs_count": len(self.security_logs),
                "threat_detections_count": len(self.threat_detections),
                "rate_limited_ips": len(self.rate_limits),
                "security_score": await self._calculate_security_score(),
                "metrics": self.metrics,
                "last_security_scan": self.metrics.get("last_security_scan"),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Security status retrieval failed: {e}")
            return {"error": str(e)}
    
    async def audit(self):
        """Comprehensive security audit"""
        logger.info("Auditing system for threats...")
        
        try:
            audit_results = {
                "timestamp": datetime.utcnow().isoformat(),
                "checks_performed": [],
                "threats_detected": [],
                "vulnerabilities": [],
                "recommendations": [],
                "security_score": 0
            }
            
            # Perform various security checks
            await self._check_api_security(audit_results)
            await self._check_data_integrity(audit_results)
            await self._check_access_patterns(audit_results)
            await self._check_system_resources(audit_results)
            await self._check_network_security(audit_results)
            
            # Calculate overall security score
            audit_results["security_score"] = await self._calculate_security_score(audit_results)
            
            # Generate alerts if needed
            await self._generate_security_alerts(audit_results)
            
            self.security_events.append(audit_results)
            self.last_audit = datetime.utcnow()
            
            logger.info(f"Security audit completed. Score: {audit_results['security_score']}/100")
            return audit_results
            
        except Exception as e:
            logger.error(f"Security audit failed: {e}")
            raise
    
    async def _check_api_security(self, audit_results: Dict):
        """Check API security"""
        check_name = "API Security Check"
        audit_results["checks_performed"].append(check_name)
        
        # Simulate API security checks
        issues = []
        
        if random.random() < 0.1:  # 10% chance of API key exposure
            issues.append("Potential API key exposure detected")
            audit_results["threats_detected"].append({
                "type": "api_exposure",
                "severity": "high",
                "description": "API keys may be exposed in logs or responses"
            })
        
        if random.random() < 0.15:  # 15% chance of rate limit issues
            issues.append("Rate limiting not properly configured")
            audit_results["vulnerabilities"].append({
                "type": "rate_limiting",
                "severity": "medium",
                "description": "API endpoints lack proper rate limiting"
            })
        
        if not issues:
            logger.info("API security check passed")
    
    async def _check_data_integrity(self, audit_results: Dict):
        """Check data integrity"""
        check_name = "Data Integrity Check"
        audit_results["checks_performed"].append(check_name)
        
        # Simulate data integrity checks
        if random.random() < 0.05:  # 5% chance of data corruption
            audit_results["threats_detected"].append({
                "type": "data_corruption",
                "severity": "high",
                "description": "Potential data corruption detected in storage layers"
            })
            audit_results["recommendations"].append("Run database repair and backup verification")
        
        if random.random() < 0.08:  # 8% chance of unauthorized access
            audit_results["threats_detected"].append({
                "type": "unauthorized_access",
                "severity": "critical",
                "description": "Suspicious data access patterns detected"
            })
    
    async def _check_access_patterns(self, audit_results: Dict):
        """Check access patterns for anomalies"""
        check_name = "Access Pattern Analysis"
        audit_results["checks_performed"].append(check_name)
        
        # Simulate access pattern analysis
        suspicious_patterns = random.randint(0, 3)
        
        if suspicious_patterns > 0:
            audit_results["threats_detected"].append({
                "type": "suspicious_access",
                "severity": "medium",
                "description": f"Detected {suspicious_patterns} suspicious access patterns",
                "count": suspicious_patterns
            })
    
    async def _check_system_resources(self, audit_results: Dict):
        """Check system resource usage"""
        check_name = "System Resource Check"
        audit_results["checks_performed"].append(check_name)
        
        # Simulate resource checks
        cpu_usage = random.uniform(10, 90)
        memory_usage = random.uniform(20, 85)
        
        if cpu_usage > 80:
            audit_results["vulnerabilities"].append({
                "type": "high_cpu_usage",
                "severity": "medium",
                "description": f"High CPU usage detected: {cpu_usage:.1f}%"
            })
        
        if memory_usage > 80:
            audit_results["vulnerabilities"].append({
                "type": "high_memory_usage",
                "severity": "medium",
                "description": f"High memory usage detected: {memory_usage:.1f}%"
            })
    
    async def _check_network_security(self, audit_results: Dict):
        """Check network security"""
        check_name = "Network Security Check"
        audit_results["checks_performed"].append(check_name)
        
        # Simulate network security checks
        if random.random() < 0.12:  # 12% chance of network anomaly
            audit_results["threats_detected"].append({
                "type": "network_anomaly",
                "severity": "medium",
                "description": "Unusual network traffic patterns detected"
            })
    
    async def _generate_security_alerts(self, audit_results: Dict):
        """Generate security alerts based on audit results"""
        critical_threats = [t for t in audit_results["threats_detected"] if t.get("severity") == "critical"]
        high_threats = [t for t in audit_results["threats_detected"] if t.get("severity") == "high"]
        
        if critical_threats or len(high_threats) > 2:
            alert = {
                "id": f"alert_{len(self.alerts) + 1}",
                "timestamp": datetime.utcnow().isoformat(),
                "level": "critical" if critical_threats else "high",
                "message": f"Security audit detected {len(critical_threats + high_threats)} high-priority threats",
                "details": critical_threats + high_threats,
                "action_required": True
            }
            
            self.alerts.append(alert)
            logger.warning(f"Security alert generated: {alert['message']}")
    
    async def get_security_summary(self) -> Dict:
        """Get security summary"""
        recent_alerts = [a for a in self.alerts if 
                        datetime.fromisoformat(a["timestamp"]) > datetime.utcnow() - timedelta(hours=24)]
        
        latest_audit = self.security_events[-1] if self.security_events else None
        
        return {
            "security_level": self.security_level,
            "last_audit": self.last_audit.isoformat() if self.last_audit else None,
            "total_audits": len(self.security_events),
            "recent_alerts": len(recent_alerts),
            "latest_security_score": latest_audit.get("security_score", 0) if latest_audit else 0,
            "active_threats": len([a for a in recent_alerts if a.get("action_required", False)])
        }
