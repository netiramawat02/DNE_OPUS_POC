from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import os

def create_contract(filename, title, vendor, client, start_date, end_date, content):
    c = canvas.Canvas(filename, pagesize=LETTER)
    width, height = LETTER

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, title)

    c.setFont("Helvetica", 12)
    c.drawString(100, height - 80, f"Vendor: {vendor}")
    c.drawString(100, height - 100, f"Client: {client}")
    c.drawString(100, height - 120, f"Contract Start Date: {start_date}")
    c.drawString(100, height - 140, f"Contract End Date: {end_date}")

    text = c.beginText(100, height - 180)
    text.setFont("Helvetica", 12)
    for line in content.split('\n'):
        text.textLine(line)
    c.drawText(text)

    c.save()
    print(f"Created {filename}")

def main():
    os.makedirs("sample_contracts", exist_ok=True)

    # Contract 1
    create_contract(
        "sample_contracts/vendor_service_agreement.pdf",
        "IT Service Agreement",
        "TechSolutions Inc.",
        "Global Corp",
        "2023-01-01",
        "2025-12-31",
        """This Service Agreement is entered into by the parties listed above.

        1. Scope of Services
        TechSolutions Inc. shall provide 24/7 server monitoring and maintenance.

        2. Payment Terms
        Global Corp shall pay $5,000 monthly, net 30 days.

        3. Renewal Clause
        This agreement shall automatically renew for successive one-year terms
        unless either party gives written notice of non-renewal at least 60 days
        prior to the end of the current term.

        4. Termination
        Either party may terminate this agreement for cause with 30 days notice.
        """
    )

    # Contract 2
    create_contract(
        "sample_contracts/software_license.pdf",
        "Enterprise Software License",
        "SoftWareHouse Ltd.",
        "Global Corp",
        "2024-06-01",
        "2025-05-31",
        """Software License Agreement.

        1. Grant of License
        SoftWareHouse Ltd. grants Global Corp a non-exclusive license to use
        the 'DataFlow' software for 500 users.

        2. Fees
        Annual license fee is $20,000, payable in advance.

        3. Expiry
        This license expires on 2025-05-31.

        4. Support
        Standard support is included. Premium support requires an additional addendum.
        """
    )

if __name__ == "__main__":
    main()
