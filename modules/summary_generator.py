def generate_text_summary(findings: list) -> str:
    """Generates a brief plain-text summary paragraph of all audit findings."""
    total = len(findings)
    if total == 0:
        return "No visual findings recorded."

    high = sum(1 for f in findings if f.get("Severity") == "High")
    med = sum(1 for f in findings if f.get("Severity") == "Medium")
    low = sum(1 for f in findings if f.get("Severity") == "Low")

    return (
        f"Audit completed across {total} photo(s). Identified {high} high-severity issue(s), "
        f"{med} medium-severity issue(s), and {low} low-severity issue(s). "
        f"Immediate corrective action is recommended for high-severity findings."
    )
