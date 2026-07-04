def correlate_findings(current_findings: list):
    has_public_ec2 = any(f['id'].endswith('-EC2-PublicSSH') or f['id'].endswith('-EC2-PublicRDP') or f['id'].endswith('-EC2-AllTrafficPublic') for f in current_findings)
    admin_users = [f for f in current_findings if f['id'].endswith('-IAM-AdminAccess')]
    no_mfa_users = [f for f in current_findings if f['id'].endswith('-IAM-NoMFA')]
    
    admin_no_mfa = []
    for admin in admin_users:
        admin_res_id = admin['resource_id']
        for no_mfa in no_mfa_users:
            if no_mfa['resource_id'] == admin_res_id:
                admin_no_mfa.append(admin_res_id)
                
    if has_public_ec2 and admin_no_mfa:
        correlation_id = "CORR-001-PublicEC2-AdminNoMFA"
        # Only add if not already in findings
        if not any(f['id'] == correlation_id for f in current_findings):
            current_findings.append({
                "id": correlation_id,
                "severity": "CRITICAL",
                "service": "Cross-Service",
                "resource_id": "Multiple",
                "title": "Critical Exposure Path Detected",
                "description": f"Attack path identified: Public EC2 instance combined with Admin IAM users lacking MFA ({', '.join(admin_no_mfa)}).",
                "recommendation": "Immediately secure the EC2 security groups and enforce MFA on admin users."
            })
        
    return current_findings
