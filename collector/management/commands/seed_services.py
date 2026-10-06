from django.core.management.base import BaseCommand
from django.db import transaction

from collector.models import (
    ServiceCategory,
    Service,
    ServiceRequirement,
)


SERVICE_DATA = [
    {
        "name": "Account & Registration Services",
        "icon": "account",
        "order": 1,
        "services": [
            {
                "name": "SS Number Online Application",
                "code": "ss-number-application",
                "description": (
                    "Assistance in applying for an SS Number through "
                    "the SSS online facility."
                ),
                "instructions": (
                    "Prepare your personal information, contact information, "
                    "email address, and applicable supporting document."
                ),
                "threshold": 20,
                "requirements": [
                    (
                        "information",
                        "Active email address",
                        "Required for the online application and confirmation.",
                    ),
                    (
                        "information",
                        "Personal and contact information",
                        "Provide the information requested by the SSS online application.",
                    ),
                    (
                        "document",
                        "Applicable supporting document",
                        "A readable colored JPEG or PDF may be uploaded when applicable.",
                    ),
                ],
            },
            {
                "name": "My.SSS Account Registration",
                "code": "mysss-registration",
                "description": (
                    "Assistance in creating a My.SSS member account."
                ),
                "instructions": (
                    "Prepare your SS Number/CRN, mobile number, email address "
                    "and one valid registration preference."
                ),
                "threshold": 15,
                "requirements": [
                    (
                        "information",
                        "SS Number or CRN",
                        "Member's SS Number or Common Reference Number.",
                    ),
                    (
                        "information",
                        "Active mobile number",
                        "Mobile number used during account registration.",
                    ),
                    (
                        "information",
                        "Active email address",
                        "Email address used for account activation.",
                    ),
                    (
                        "information",
                        "Registration preference",
                        (
                            "One applicable SSS registration preference, such as "
                            "UMID, PRN, employer/household ID, loan date, "
                            "transaction number, savings account number, "
                            "or pension check number."
                        ),
                    ),
                ],
            },
            {
                "name": "My.SSS Password Reset",
                "code": "mysss-password-reset",
                "description": (
                    "Assistance in recovering access to a My.SSS account."
                ),
                "instructions": (
                    "Use the official My.SSS account recovery facility."
                ),
                "threshold": 10,
                "requirements": [
                    (
                        "account",
                        "Existing My.SSS account",
                        "The member must already have a registered account.",
                    ),
                    (
                        "information",
                        "Registered account information",
                        "Information needed by the official account recovery process.",
                    ),
                ],
            },
        ],
    },

    {
        "name": "Contribution Services",
        "icon": "wallet",
        "order": 2,
        "services": [
            {
                "name": "PRN Generation - Contributions",
                "code": "prn-contribution",
                "description": (
                    "Assistance in generating a Payment Reference Number "
                    "for contribution payment."
                ),
                "instructions": (
                    "Log in to the applicable SSS online facility and "
                    "generate the PRN before contribution payment."
                ),
                "threshold": 10,
                "requirements": [
                    (
                        "information",
                        "SS Number",
                        "Member's SS Number.",
                    ),
                    (
                        "account",
                        "Access to SSS online facility",
                        "My.SSS or another applicable SSS PRN facility.",
                    ),
                ],
            },
            {
                "name": "Contribution Inquiry",
                "code": "contribution-inquiry",
                "description": (
                    "Assistance in viewing posted SSS contributions."
                ),
                "instructions": (
                    "The member's contribution records may be viewed "
                    "through the applicable My.SSS inquiry facility."
                ),
                "threshold": 10,
                "requirements": [
                    (
                        "account",
                        "My.SSS account",
                        "Access to the member's registered My.SSS account.",
                    ),
                ],
            },
        ],
    },

    {
        "name": "Disbursement Services",
        "icon": "wallet",
        "order": 3,
        "services": [
            {
                "name": "DAEM Assistance",
                "code": "daem-assistance",
                "description": (
                    "Assistance with enrollment of a disbursement account "
                    "through the Disbursement Account Enrollment Module."
                ),
                "instructions": (
                    "Prepare the account information and supporting files "
                    "required by SSS."
                ),
                "threshold": 15,
                "requirements": [
                    (
                        "account",
                        "My.SSS account",
                        "Access to the member's My.SSS account.",
                    ),
                    (
                        "document",
                        "Proof of account",
                        (
                            "Applicable proof showing the account holder "
                            "and account details."
                        ),
                    ),
                    (
                        "document",
                        "Government-issued ID",
                        "Readable image of an acceptable government-issued ID/document.",
                    ),
                    (
                        "document",
                        "Selfie with supporting documents",
                        (
                            "Selfie holding the applicable ID/document and "
                            "proof of account when required by the SSS facility."
                        ),
                    ),
                ],
            },
        ],
    },

    {
        "name": "Loan Services",
        "icon": "wallet",
        "order": 4,
        "services": [
            {
                "name": "Salary Loan Online Application",
                "code": "salary-loan",
                "description": (
                    "Assistance in filing an SSS Salary Loan application online."
                ),
                "instructions": (
                    "Salary loan applications are filed through My.SSS "
                    "or the MySSS mobile application."
                ),
                "threshold": 20,
                "requirements": [
                    (
                        "account",
                        "My.SSS account",
                        "Required for online salary loan filing.",
                    ),
                    (
                        "eligibility",
                        "Required posted contributions",
                        (
                            "36 posted monthly contributions for a one-month loan "
                            "or 72 for a two-month loan, subject to current SSS rules."
                        ),
                    ),
                    (
                        "eligibility",
                        "Recent contributions",
                        (
                            "At least six required contributions must be within "
                            "the applicable 12-month period."
                        ),
                    ),
                    (
                        "information",
                        "Updated contact information",
                        "Contact information in the SSS database must be updated.",
                    ),
                    (
                        "account",
                        "Active approved disbursement account",
                        "An eligible active disbursement account is required.",
                    ),
                    (
                        "eligibility",
                        "No disqualifying past-due SSS loan",
                        "Subject to current SSS loan eligibility rules.",
                    ),
                ],
            },
            {
                "name": "PRN Generation - Loan Payment",
                "code": "prn-loan",
                "description": (
                    "Assistance in generating the appropriate reference "
                    "for SSS loan repayment."
                ),
                "instructions": (
                    "Access the member's SSS online account and use "
                    "the applicable loan payment facility."
                ),
                "threshold": 10,
                "requirements": [
                    (
                        "account",
                        "My.SSS account",
                        "Access to the member's registered account.",
                    ),
                    (
                        "information",
                        "Existing SSS loan",
                        "Applicable loan record must exist.",
                    ),
                ],
            },
        ],
    },

    {
        "name": "Benefit Services",
        "icon": "heart",
        "order": 5,
        "services": [
            {
                "name": "Retirement Benefit - Online Filing",
                "code": "retirement-benefit",
                "description": (
                    "Assistance in filing an eligible retirement benefit "
                    "claim through My.SSS."
                ),
                "instructions": (
                    "Some retirement cases cannot be filed online and "
                    "must be processed by an SSS branch."
                ),
                "threshold": 25,
                "requirements": [
                    (
                        "account",
                        "Registered My.SSS account",
                        "Required for online retirement claim filing.",
                    ),
                    (
                        "account",
                        "Approved disbursement account or applicable payment account",
                        (
                            "Member must have an applicable approved account "
                            "for benefit disbursement."
                        ),
                    ),
                    (
                        "eligibility",
                        "Retirement eligibility",
                        (
                            "Member must satisfy the applicable age, contribution, "
                            "employment and other SSS retirement conditions."
                        ),
                    ),
                ],
            },
            {
                "name": "Unemployment Benefit - Online Filing",
                "code": "unemployment-benefit",
                "description": (
                    "Assistance in filing an unemployment benefit claim "
                    "through My.SSS."
                ),
                "instructions": (
                    "The claim is filed online and requires certification "
                    "of involuntary separation through the applicable process."
                ),
                "threshold": 25,
                "requirements": [
                    (
                        "account",
                        "Registered My.SSS account",
                        "Required for online filing.",
                    ),
                    (
                        "account",
                        "Approved disbursement account",
                        "Required for benefit payment.",
                    ),
                    (
                        "eligibility",
                        "Involuntary separation",
                        "Separation must satisfy applicable SSS unemployment rules.",
                    ),
                    (
                        "eligibility",
                        "Required contribution history",
                        (
                            "At least 36 monthly contributions, with 12 within "
                            "the applicable 18-month period."
                        ),
                    ),
                    (
                        "document",
                        "Proof of involuntary separation",
                        (
                            "Notice of termination or applicable affidavit/document "
                            "may be required during certification."
                        ),
                    ),
                    (
                        "document",
                        "Valid identification document",
                        (
                            "Applicable identification with signature and photo "
                            "for the certification process."
                        ),
                    ),
                ],
            },
            {
                "name": "Maternity Benefit Assistance",
                "code": "maternity-benefit",
                "description": (
                    "Assistance with maternity notification or online "
                    "maternity benefit filing."
                ),
                "instructions": (
                    "Requirements depend on employment status and the "
                    "maternity contingency."
                ),
                "threshold": 25,
                "requirements": [
                    (
                        "account",
                        "My.SSS account",
                        "Required for applicable online maternity transactions.",
                    ),
                    (
                        "eligibility",
                        "Required contribution history",
                        (
                            "At least three months of contributions in the "
                            "applicable 12-month period before the semester "
                            "of contingency."
                        ),
                    ),
                    (
                        "document",
                        "Proof of pregnancy for notification",
                        (
                            "Applicable pregnancy test, ultrasound, blood "
                            "pregnancy test or other accepted diagnostic proof."
                        ),
                    ),
                    (
                        "account",
                        "Approved DAEM disbursement account",
                        "Required for applicable maternity benefit disbursement.",
                    ),
                    (
                        "document",
                        "Supporting maternity documents",
                        (
                            "Applicable birth, death, medical, solo-parent "
                            "or other supporting documents depending on the case."
                        ),
                    ),
                ],
            },
            {
                "name": "Sickness Benefit Assistance",
                "code": "sickness-benefit",
                "description": (
                    "Assistance with applicable SSS sickness benefit "
                    "transactions and online facilities."
                ),
                "instructions": (
                    "Requirements vary according to employment status "
                    "and the sickness claim."
                ),
                "threshold": 25,
                "requirements": [
                    (
                        "account",
                        "My.SSS account",
                        "Required for applicable online services.",
                    ),
                    (
                        "account",
                        "Approved disbursement account",
                        "Required for applicable direct benefit payment.",
                    ),
                    (
                        "document",
                        "Applicable medical/supporting documents",
                        (
                            "Medical and other supporting documentation "
                            "depends on the sickness claim circumstances."
                        ),
                    ),
                ],
            },
            {
                "name": "Disability Benefit Assistance",
                "code": "disability-benefit",
                "description": (
                    "Assistance with applicable disability benefit services."
                ),
                "instructions": (
                    "Prepare the applicable claim and medical/supporting "
                    "information required by SSS."
                ),
                "threshold": 30,
                "requirements": [
                    (
                        "account",
                        "My.SSS account",
                        "Required for applicable online services.",
                    ),
                    (
                        "account",
                        "Approved disbursement account",
                        "Required for applicable benefit payment.",
                    ),
                    (
                        "document",
                        "Applicable medical/supporting documents",
                        "Documents depend on the nature of the disability claim.",
                    ),
                ],
            },
            {
                "name": "Funeral Benefit - Online Filing",
                "code": "funeral-benefit",
                "description": (
                    "Assistance for eligible SSS member-claimants filing "
                    "a funeral benefit claim online."
                ),
                "instructions": (
                    "Online filing is available to SSS member-claimants. "
                    "Non-SSS member-claimants file over the counter."
                ),
                "threshold": 30,
                "requirements": [
                    (
                        "account",
                        "Claimant has an SS Number",
                        "Required for online filing.",
                    ),
                    (
                        "account",
                        "Registered My.SSS account",
                        "Required for online funeral benefit filing.",
                    ),
                    (
                        "account",
                        "Approved DAEM disbursement account",
                        "Required for applicable online benefit payment.",
                    ),
                    (
                        "document",
                        "Proof of deceased member's SSS membership",
                        "Upload applicable proof establishing SSS membership.",
                    ),
                    (
                        "document",
                        "Death certificate",
                        "Applicable registered/issued death certificate.",
                    ),
                    (
                        "document",
                        "Proof of funeral expenses",
                        "Required when applicable to the claimant's case.",
                    ),
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Populate E-Center services using official SSS service information."

    @transaction.atomic
    def handle(self, *args, **options):

        service_count = 0
        requirement_count = 0

        for category_data in SERVICE_DATA:

            category, _ = ServiceCategory.objects.update_or_create(
                name=category_data["name"],
                defaults={
                    "icon": category_data["icon"],
                    "display_order": category_data["order"],
                    "is_active": True,
                },
            )

            for service_order, service_data in enumerate(
                category_data["services"],
                start=1,
            ):

                service, _ = Service.objects.update_or_create(
                    code=service_data["code"],
                    defaults={
                        "category": category,
                        "name": service_data["name"],
                        "description": service_data["description"],
                        "instructions": service_data["instructions"],
                        "threshold_minutes": service_data["threshold"],
                        "is_online": True,
                        "is_active": True,
                        "display_order": service_order,
                    },
                )

                service_count += 1

                # Rebuild seeded requirements so rerunning the
                # command does not create duplicates.
                service.requirements.all().delete()

                for order, requirement in enumerate(
                    service_data["requirements"],
                    start=1,
                ):
                    requirement_type, name, description = requirement

                    ServiceRequirement.objects.create(
                        service=service,
                        requirement_type=requirement_type,
                        name=name,
                        description=description,
                        is_required=True,
                        display_order=order,
                        is_active=True,
                    )

                    requirement_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully populated {service_count} services "
                f"and {requirement_count} requirements."
            )
        )