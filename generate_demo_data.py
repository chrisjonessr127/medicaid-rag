"""Generate a fictional, license-safe benefits-office example dataset."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BANNER = "FICTIONAL DEMO DATA — NOT REAL POLICY"
POLICIES = {
    "demo_intake.txt": (
        "The imaginary Sample Benefits Office accepts fictional applications through a demo portal. "
        "Each submission receives a tracking code beginning with DEMO. These codes do not represent real clients.",
        "The synthetic intake clerk acknowledges each sample application within three business days. "
        "The clerk checks for a completed test form and an example checklist."
    ),
    "demo_documents.txt": (
        "A fictional submission can include simulated proof of residence, an invented eligibility worksheet, "
        "and a non-identifying sample consent form. Never provide real identity documents in this demo.",
        "When a test attachment is missing, the simulated review team marks the request Incomplete "
        "and sends a mock reminder within two business days."
    ),
    "demo_review.txt": (
        "The fictional review phase begins after the demo checklist is complete. "
        "A reviewer targets five business days to finish the sample verification.",
        "All example decisions are labeled DEMONSTRATION ONLY and have no effect on actual benefits, "
        "insurance coverage, billing, eligibility, or care."
    ),
    "demo_escalation.txt": (
        "The invented support desk sends technical issues to a Demo Queue when a local test fails. "
        "Issues remain local and never require uploading private documents.",
        "For a fictional urgent case, a tester marks the example ticket High Priority. "
        "This classification has no connection to real clinical emergencies."
    ),
    "demo_privacy.txt": (
        "The hypothetical office uses invented names and identifiers only. No real patient, client, "
        "employer, banking, or staff information belongs in this RAG evaluation dataset.",
        "The fictional document retention period is fourteen days for sample tickets, "
        "but the repository itself does not enforce retention or automatically delete data."
    ),
    "demo_appeals.txt": (
        "A person testing the fictional system may submit a mock appeal within seven calendar days "
        "of a simulated decision notice. This timeline is completely invented.",
        "The mock appeal result is stored as a demonstration note only and cannot change any real policy, "
        "customer record, or agency determination."
    ),
    "demo_status.txt": (
        "The synthetic workflow recognizes New, Incomplete, In Review, and Closed as sample statuses. "
        "Only test records with a completed demo checklist progress to In Review.",
        "A fictional request moves to Closed when the sample reviewer records a mock result. "
        "No real payment, benefits, or eligibility action is performed."
    ),
    "demo_contact.txt": (
        "The imaginary Demo Help Desk answers sample questions during a made-up weekday support window. "
        "There is no genuine service number or email address in this demonstration.",
        "Users should test the chatbot with fictional questions about status, acknowledgment, and sample "
        "documents rather than enter personal or confidential details."
    ),
}


def generate():
    data = ROOT / "data"
    data.mkdir(exist_ok=True)
    created = []
    for name, paragraphs in POLICIES.items():
        dest = data / name
        if dest.exists():
            raise FileExistsError(f"Won't overwrite an existing file: {dest}")
        dest.write_text(BANNER + "\n\n" + "\n\n".join(paragraphs) + "\n", encoding="utf-8")
        created.append(dest)
    return created


if __name__ == "__main__":
    files = generate()
    print(f"Generated {len(files)} fictional test documents in data/ (ignored by Git).")
