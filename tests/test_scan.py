from backend.services.scan_service import ScanService

service = ScanService()
result = service.run_scan()

print("=" * 50)
print("SCAN COMPLETED")
print("=" * 50)
print("Provider:", result.provider)
print("Assets count:", result.assets)
print("Findings count:", len(result.findings))
print("Relationships mapped:")
for rel in result.relationships:
    print(f"  {rel.source} --({rel.relation})--> {rel.target}")

print("Attack Paths discovered:")
for path in result.attack_paths:
    print(f"  Path: {' -> '.join(path.nodes)}")
    print(f"    Title: {path.title}")
    print(f"    Severity: {path.severity}")
    print(f"    Risk Score: {path.risk_score}")