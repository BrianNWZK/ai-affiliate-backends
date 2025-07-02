import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger("ArielMatrix.EthicsGuard")

class EthicsGuard:
    """Ethics and compliance monitoring system"""
    
    def __init__(self):
        self.violations = []
        self.compliance_rules = self._load_compliance_rules()
        self.audit_history = []
        self.strict_mode = True
        
    def _load_compliance_rules(self):
        """Load compliance rules and ethical guidelines"""
        return {
            "data_privacy": {
                "gdpr_compliance": True,
                "data_retention_days": 365,
                "user_consent_required": True,
                "data_encryption": True,
                "right_to_deletion": True
            },
            "advertising_ethics": {
                "no_misleading_claims": True,
                "affiliate_disclosure": True,
                "age_appropriate_content": True,
                "respect_user_privacy": True,
                "honest_testimonials": True
            },
            "financial_compliance": {
                "accurate_reporting": True,
                "tax_compliance": True,
                "anti_money_laundering": True,
                "fraud_prevention": True,
                "transparent_fees": True
            },
            "content_standards": {
                "no_harmful_content": True,
                "respect_ip_rights": True,
                "fact_checking": True,
                "content_moderation": True,
                "accessibility_standards": True
            },
            "api_usage": {
                "respect_rate_limits": True,
                "terms_of_service_compliance": True,
                "proper_attribution": True,
                "no_unauthorized_scraping": True,
                "data_usage_consent": True
            },
            "ai_ethics": {
                "algorithmic_transparency": True,
                "bias_prevention": True,
                "human_oversight": True,
                "explainable_decisions": True,
                "fair_treatment": True
            }
        }
    
    async def check_compliance(self, action: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Comprehensive compliance check"""
        logger.info("Performing ethics and compliance check...")
        
        try:
            compliance_result = {
                "timestamp": datetime.utcnow().isoformat(),
                "action_checked": action,
                "violations_found": [],
                "compliance_score": 100,
                "recommendations": [],
                "status": "compliant",
                "audit_id": f"audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            }
            
            violations = []
            
            if action:
                # Check specific action compliance
                violations.extend(await self._check_action_compliance(action))
            else:
                # Perform system-wide compliance audit
                violations.extend(await self._check_system_compliance())
            
            # Process violations
            compliance_result["violations_found"] = violations
            compliance_result["compliance_score"] = max(0, 100 - (len(violations) * 15))
            
            if violations:
                compliance_result["status"] = "violations_found"
                self.violations.extend(violations)
                
                # Generate recommendations
                compliance_result["recommendations"] = await self._generate_recommendations(violations)
                
                # Log violations
                for violation in violations:
                    logger.warning(f"Compliance violation: {violation.get('description', 'Unknown violation')}")
            
            # Store audit result
            self.audit_history.append(compliance_result)
            
            # Keep only last 100 audits
            if len(self.audit_history) > 100:
                self.audit_history = self.audit_history[-100:]
            
            logger.info(f"Compliance check completed. Score: {compliance_result['compliance_score']}/100")
            return compliance_result
            
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            raise
    
    async def _check_action_compliance(self, action: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check compliance for a specific action"""
        violations = []
        action_type = action.get("type", "unknown")
        
        # Data Privacy Checks
        if action_type in ["data_collection", "user_tracking", "profile_creation"]:
            if not action.get("user_consent", False):
                violations.append({
                    "type": "data_privacy",
                    "severity": "high",
                    "description": "Data collection without explicit user consent",
                    "rule_violated": "user_consent_required",
                    "action_type": action_type
                })
            
            if not action.get("data_encrypted", True):
                violations.append({
                    "type": "data_privacy",
                    "severity": "high",
                    "description": "Data not properly encrypted",
                    "rule_violated": "data_encryption",
                    "action_type": action_type
                })
        
        # Advertising Ethics Checks
        if action_type in ["campaign_launch", "ad_creation", "content_promotion"]:
            if action.get("misleading_claims", False):
                violations.append({
                    "type": "advertising_ethics",
                    "severity": "high",
                    "description": "Potentially misleading advertising claims detected",
                    "rule_violated": "no_misleading_claims",
                    "action_type": action_type
                })
            
            if not action.get("affiliate_disclosure", True):
                violations.append({
                    "type": "advertising_ethics",
                    "severity": "medium",
                    "description": "Missing affiliate relationship disclosure",
                    "rule_violated": "affiliate_disclosure",
                    "action_type": action_type
                })
        
        # Financial Compliance Checks
        if action_type in ["revenue_generation", "payment_processing", "financial_reporting"]:
            if not action.get("accurate_reporting", True):
                violations.append({
                    "type": "financial_compliance",
                    "severity": "high",
                    "description": "Inaccurate financial reporting detected",
                    "rule_violated": "accurate_reporting",
                    "action_type": action_type
                })
        
        # API Usage Checks
        if action_type in ["api_call", "data_scraping", "external_integration"]:
            if action.get("rate_limit_exceeded", False):
                violations.append({
                    "type": "api_usage",
                    "severity": "medium",
                    "description": "API rate limits exceeded",
                    "rule_violated": "respect_rate_limits",
                    "action_type": action_type
                })
            
            if not action.get("terms_compliance", True):
                violations.append({
                    "type": "api_usage",
                    "severity": "high",
                    "description": "Terms of service violation detected",
                    "rule_violated": "terms_of_service_compliance",
                    "action_type": action_type
                })
        
        # AI Ethics Checks
        if action_type in ["ai_decision", "automated_action", "algorithm_execution"]:
            if not action.get("human_oversight", False):
                violations.append({
                    "type": "ai_ethics",
                    "severity": "medium",
                    "description": "AI action without human oversight",
                    "rule_violated": "human_oversight",
                    "action_type": action_type
                })
            
            if action.get("bias_detected", False):
                violations.append({
                    "type": "ai_ethics",
                    "severity": "high",
                    "description": "Algorithmic bias detected",
                    "rule_violated": "bias_prevention",
                    "action_type": action_type
                })
        
        return violations
    
    async def _check_system_compliance(self) -> List[Dict[str, Any]]:
        """Perform system-wide compliance checks"""
        violations = []
        
        # Simulate system compliance checks
        system_checks = [
            {
                "check": "data_encryption_status",
                "compliant": True,
                "category": "data_privacy"
            },
            {
                "check": "user_consent_tracking",
                "compliant": True,
                "category": "data_privacy"
            },
            {
                "check": "financial_audit_trail",
                "compliant": True,
                "category": "financial_compliance"
            },
            {
                "check": "content_moderation_active",
                "compliant": True,
                "category": "content_standards"
            },
            {
                "check": "api_usage_monitoring",
                "compliant": True,
                "category": "api_usage"
            },
            {
                "check": "ai_decision_logging",
                "compliant": True,
                "category": "ai_ethics"
            }
        ]
        
        for check in system_checks:
            if not check["compliant"]:
                violations.append({
                    "type": "system_compliance",
                    "severity": "medium",
                    "description": f"System compliance issue: {check['check']}",
                    "rule_violated": check["check"],
                    "category": check["category"]
                })
        
        return violations
    
    async def _generate_recommendations(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations based on violations"""
        recommendations = []
        
        violation_types = set(v.get("type") for v in violations)
        
        for violation_type in violation_types:
            if violation_type == "data_privacy":
                recommendations.extend([
                    "Implement explicit user consent mechanisms",
                    "Enable end-to-end data encryption",
                    "Review and update privacy policy",
                    "Implement data retention policies"
                ])
            elif violation_type == "advertising_ethics":
                recommendations.extend([
                    "Add clear affiliate disclosures to all campaigns",
                    "Review advertising claims for accuracy",
                    "Implement content review process",
                    "Train team on advertising ethics"
                ])
            elif violation_type == "financial_compliance":
                recommendations.extend([
                    "Implement automated financial reporting",
                    "Set up audit trail systems",
                    "Review tax compliance procedures",
                    "Enable fraud detection systems"
                ])
            elif violation_type == "api_usage":
                recommendations.extend([
                    "Implement proper rate limiting",
                    "Review API terms of service compliance",
                    "Add request monitoring and alerting",
                    "Implement retry logic with backoff"
                ])
            elif violation_type == "ai_ethics":
                recommendations.extend([
                    "Add human oversight to AI decisions",
                    "Implement bias detection and mitigation",
                    "Enable explainable AI features",
                    "Regular algorithm auditing"
                ])
        
        # Remove duplicates and return
        return list(set(recommendations))
    
    async def get_compliance_summary(self) -> Dict[str, Any]:
        """Get comprehensive compliance summary"""
        total_violations = len(self.violations)
        recent_violations = [
            v for v in self.violations
            if datetime.fromisoformat(v.get("timestamp", datetime.utcnow().isoformat())) > 
               datetime.utcnow() - timedelta(days=30)
        ]
        
        # Violation breakdown by type
        violation_types = {}
        severity_counts = {}
        
        for violation in self.violations:
            v_type = violation.get("type", "unknown")
            severity = violation.get("severity", "unknown")
            
            violation_types[v_type] = violation_types.get(v_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Calculate compliance score
        recent_audit = self.audit_history[-1] if self.audit_history else None
        current_score = recent_audit.get("compliance_score", 100) if recent_audit else 100
        
        return {
            "total_violations": total_violations,
            "recent_violations": len(recent_violations),
            "violation_types": violation_types,
            "severity_breakdown": severity_counts,
            "current_compliance_score": current_score,
            "total_audits": len(self.audit_history),
            "last_audit": recent_audit.get("timestamp") if recent_audit else None,
            "compliance_rules_count": sum(len(rules) for rules in self.compliance_rules.values()),
            "strict_mode": self.strict_mode
        }
    
    async def set_strict_mode(self, enabled: bool):
        """Enable or disable strict compliance mode"""
        self.strict_mode = enabled
        logger.info(f"Strict compliance mode {'enabled' if enabled else 'disabled'}")
    
    async def clear_violations(self, older_than_days: int = 30):
        """Clear old violations"""
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
        
        original_count = len(self.violations)
        self.violations = [
            v for v in self.violations
            if datetime.fromisoformat(v.get("timestamp", datetime.utcnow().isoformat())) > cutoff_date
        ]
        
        cleared_count = original_count - len(self.violations)
        logger.info(f"Cleared {cleared_count} violations older than {older_than_days} days")
        
        return cleared_count
