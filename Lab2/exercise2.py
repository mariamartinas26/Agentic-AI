from enum import Enum
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class LogAnalysis(BaseModel):
    severity: SeverityLevel = Field(description="Overall severity of the event")
    error_code: int = Field(description="HTTP or system error code found in the log, or -1 if none")
    is_compromised: bool = Field(description="True if active unauthorized access succeeded, else False")
    summary: str = Field(description="One-sentence technical summary of the event")
    recommended_fix: list[str] = Field(description="Concrete remediation steps")

SYSTEM_PROMPT = (
    "You are a SIEM log triage engine. Classify the given raw server log into a "
    "structured incident record. Set is_compromised to true only when the log shows "
    "unauthorized access that actually succeeded. Extract any HTTP/system error code "
    "as an integer, or -1 if none is present. Keep the summary to one technical sentence "
    "and list concrete remediation steps."
)

def parse_server_log(raw_log: str) -> LogAnalysis:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"Analyze the following raw server log:\n{raw_log}",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=LogAnalysis,
        ),
    )
    return LogAnalysis.model_validate_json(response.text)

if __name__ == "__main__":
    sample = (
        "2026-10-15 02:11:44 [ALERT] sshd[9012]: Accepted password for root "
        "from 198.51.100.77 port 44122 ssh2 (ErrorCode=401 bypassed via PAM bug)"
    )
    print(parse_server_log(sample).model_dump_json(indent=2))

def test_ssh_breach_log_parsing():
    sample_log = (
        "2026-10-15 02:11:44 [ALERT] sshd[9012]: Accepted password for root "
        "from 198.51.100.77 port 44122 ssh2 (ErrorCode=401 bypassed via PAM bug)"
    )

    result = parse_server_log(sample_log)

    assert result.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]
    assert result.error_code == 401
    assert result.is_compromised is True
    assert len(result.recommended_fix) >= 1