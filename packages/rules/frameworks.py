from enum import Enum

class Framework(str, Enum):
    """Enumeration of supported compliance frameworks."""

    PCI = "PCI"
    GDPR = "GDPR"
    DPDP = "DPDP"
    ISO_27001 = "ISO 27001"
    NIST = "NIST"
    HIPAA = "HIPAA"
    FEDRAMP_LOW = "FedRAMP Low"
    FEDRAMP_MODERATE = "FedRAMP Moderate"
    FEDRAMP_HIGH = "FedRAMP High"
    SOC_2 = "SOC 2"
    CIS = "CIS"
    CCPA = "CCPA"

__all__ = ["Framework"]
