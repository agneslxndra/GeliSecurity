import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


MODEL_NAMES = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite"
]


def get_response_text(response):
    try:
        if response.text:
            return response.text
    except Exception:
        pass

    try:
        candidates = response.candidates
        if candidates and candidates[0].content.parts:
            text = ""

            for part in candidates[0].content.parts:
                if hasattr(part, "text"):
                    text += part.text

            if text.strip():
                return text
    except Exception:
        pass

    return None


def call_gemini_with_fallback(prompt):
    if not GEMINI_API_KEY:
        return None, "GEMINI_API_KEY belum tersedia."

    last_error = ""

    for model_name in MODEL_NAMES:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            ai_text = get_response_text(response)

            if ai_text:
                return ai_text, None

        except Exception as e:
            last_error = str(e)
            continue

    return None, last_error


# =========================
# REMEDIATION ENGINE
# =========================

def build_prompt(finding_title, severity, description, affected_url, language):
    return f"""
You are a cybersecurity remediation assistant.

Your task is to analyze a vulnerability finding and generate a practical remediation report.

Rules:
- Use Bahasa Indonesia.
- Keep technical terms in English when needed.
- Make it clear for developers and non-security stakeholders.
- Do not provide exploit instructions.
- Focus only on defensive remediation.
- Give secure coding advice based on the selected programming language.
- Do not invent technical facts outside the provided finding.
- If code example is needed, provide safe defensive code only.

Finding Data:
- Finding Title: {finding_title}
- Severity: {severity}
- Affected URL: {affected_url}
- Description: {description}
- Target Programming Language: {language}

Please generate the output using this exact format:

## Vulnerability Summary
Explain the vulnerability briefly.

## Risk Level
Explain why the severity is {severity}.

## Technical Impact
Explain the possible technical impact.

## Business Impact
Explain the possible business impact in simple language.

## Sustainable Impact
Explain how fixing this issue helps create a safer digital ecosystem.

## Root Cause
Explain the likely root cause.

## Recommended Remediation
Give clear remediation steps.

## Secure Code Example in {language}
Give a defensive secure code example. If the exact context is not enough, give a general safe example.

## Retesting Steps
Give simple steps to verify the issue has been fixed.

## Final Recommendation
Give a short final recommendation.
"""


def generate_mock_remediation(finding_title, severity, description, affected_url, language):
    return f"""
## Vulnerability Summary
Finding ini terindikasi sebagai **{finding_title}** pada endpoint atau fitur terkait.

## Risk Level
Severity finding ini adalah **{severity}**, sehingga perlu diprioritaskan sesuai dampak dan kemungkinan eksploitasi.

## Technical Impact
Kerentanan ini dapat menyebabkan gangguan pada keamanan aplikasi, seperti akses tidak sah, manipulasi data, atau lemahnya kontrol keamanan.

## Business Impact
Jika tidak diperbaiki, celah ini bisa berdampak pada kepercayaan pengguna, keamanan data, dan reputasi organisasi.

## Sustainable Impact
Dengan memperbaiki celah ini, aplikasi menjadi lebih aman dan membantu membangun ekosistem digital yang lebih sehat.

## Root Cause
Kemungkinan penyebabnya adalah validasi, konfigurasi, atau kontrol keamanan yang belum diterapkan secara optimal.

## Recommended Remediation
1. Lakukan validasi input di sisi server.
2. Terapkan kontrol akses yang sesuai.
3. Tambahkan proteksi keamanan pada endpoint sensitif.
4. Gunakan logging dan monitoring.
5. Lakukan retesting setelah perbaikan.

## Secure Code Example in {language}
Contoh kode perlu disesuaikan dengan source code asli. Pastikan input user tidak diproses langsung tanpa validasi dan sanitasi.

## Retesting Steps
1. Coba akses ulang endpoint terkait.
2. Pastikan request tidak valid ditolak.
3. Pastikan perbaikan tidak merusak fitur utama.
4. Dokumentasikan hasil retest.

## Final Recommendation
Finding ini perlu diperbaiki berdasarkan prioritas severity **{severity}**.
"""


def generate_remediation(finding_title, severity, description, affected_url, language):
    prompt = build_prompt(
        finding_title=finding_title,
        severity=severity,
        description=description,
        affected_url=affected_url,
        language=language
    )

    ai_text, error = call_gemini_with_fallback(prompt)

    if ai_text:
        return ai_text

    return f"""
## AI Engine Notice
AI API belum berhasil menghasilkan response valid, jadi sistem memakai fallback lokal.

Detail error terakhir:
`{error}`

## Fallback Result
{generate_mock_remediation(finding_title, severity, description, affected_url, language)}
"""

# =========================
# AUTOFIX ENGINE
# =========================

def build_autofix_prompt(finding_title, severity, language, vulnerable_code):
    prompt = (
        "You are a secure code remediation assistant.\n\n"
        "Your task is to fix vulnerable code based on the security finding.\n\n"
        "Rules:\n"
        "- Use Bahasa Indonesia for explanation.\n"
        "- Keep technical terms in English when needed.\n"
        "- Focus only on defensive security.\n"
        "- Do not provide exploit instructions.\n"
        "- Do not add unrelated features.\n"
        "- Keep the fixed code simple and practical.\n"
        "- If the code context is incomplete, make safe assumptions and explain them.\n"
        "- Provide secure code only.\n"
        "- Do not remove the main business logic unless it is directly insecure.\n\n"
        "Finding Data:\n"
        f"- Finding Title: {finding_title}\n"
        f"- Severity: {severity}\n"
        f"- Target Programming Language: {language}\n\n"
        "Vulnerable Code:\n"
        "[CODE START]\n"
        f"{vulnerable_code}\n"
        "[CODE END]\n\n"
        "Please generate the output using this exact format:\n\n"
        "## AutoFix Summary\n"
        "Explain what was insecure in the original code.\n\n"
        "## Fixed Code\n"
        "Provide the safer fixed version of the code.\n\n"
        "## What Changed\n"
        "Explain the important security changes.\n\n"
        "## Why This Fix Works\n"
        "Explain why the fixed code reduces the vulnerability.\n\n"
        "## Developer Notes\n"
        "Mention anything the developer still needs to adjust manually.\n\n"
        "## Retesting Steps\n"
        "Give simple steps to verify the fix.\n"
    )

    return prompt


def generate_mock_autofix(finding_title, severity, language, vulnerable_code):
    result = (
        "## AutoFix Summary\n"
        f"Kode yang diberikan terindikasi memiliki risiko terkait **{finding_title}** "
        f"dengan severity **{severity}**. Karena AI API tidak tersedia, sistem menampilkan "
        "fallback AutoFix lokal.\n\n"

        "## Fixed Code\n"
        "Contoh fixed code perlu disesuaikan dengan source code asli.\n\n"
        "Prinsip utama:\n"
        "1. Jangan memproses input user secara langsung tanpa validasi.\n"
        "2. Gunakan prepared statement / parameterized query untuk database.\n"
        "3. Terapkan validasi input di sisi server.\n"
        "4. Gunakan error handling yang aman.\n"
        "5. Jangan tampilkan error sensitif ke user.\n\n"

        "## What Changed\n"
        "1. Input user perlu divalidasi sebelum diproses.\n"
        "2. Query database tidak boleh disusun langsung dari string input user.\n"
        "3. Error detail tidak boleh ditampilkan ke user akhir.\n"
        "4. Logging perlu dilakukan secara aman di sisi server.\n\n"

        "## Why This Fix Works\n"
        "Perbaikan ini mengurangi risiko penyalahgunaan input karena data user diperlakukan "
        "sebagai data biasa, bukan sebagai bagian dari logic atau query aplikasi.\n\n"

        "## Developer Notes\n"
        "Developer tetap perlu menyesuaikan kode dengan framework, struktur database, dan flow "
        "aplikasi yang sebenarnya.\n\n"

        "## Retesting Steps\n"
        "1. Jalankan ulang fitur dengan input normal.\n"
        "2. Uji input tidak valid.\n"
        "3. Pastikan aplikasi tidak menampilkan error sensitif.\n"
        "4. Pastikan fitur utama tetap berjalan normal.\n"
    )

    return result


def generate_autofix(finding_title, severity, language, vulnerable_code):
    prompt = build_autofix_prompt(
        finding_title=finding_title,
        severity=severity,
        language=language,
        vulnerable_code=vulnerable_code
    )

    ai_text, error = call_gemini_with_fallback(prompt)

    if ai_text:
        return ai_text

    return (
        "## AutoFix Engine Notice\n"
        "AI API belum berhasil menghasilkan AutoFix valid, jadi sistem memakai fallback lokal.\n\n"
        "Detail error terakhir:\n"
        f"`{error}`\n\n"
        "## Fallback AutoFix\n"
        f"{generate_mock_autofix(finding_title, severity, language, vulnerable_code)}"
    )