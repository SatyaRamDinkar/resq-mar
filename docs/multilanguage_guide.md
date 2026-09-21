# ResQ-MAR Multi-Language Support (i18n)

## 1. Why Multi-Language Support Matters
Emergency situations often involve panic, making it difficult for citizens to communicate outside their native language. 
- **Inclusivity:** Supports non-English speaking regions (e.g., rural Andhra Pradesh, local Sri Lankan districts).
- **Accuracy:** Prevents critical miscommunications during disaster reporting.
- **Novelty:** Traditional RAG systems in the literature assume English-only inputs. ResQ-MAR natively translates inputs and outputs on the fly, making it genuinely deployable across diverse demographics.

## 2. Supported Languages
While the core system can theoretically support any language Gemini supports, ResQ-MAR is heavily tested and optimized for the following deployment regions:
- **English (en):** Primary system language.
- **Telugu (te):** For primary deployment in Andhra Pradesh, India.
- **Hindi (hi):** Broad coverage for Indian deployment.
- **Sinhala (si):** For Sri Lankan deployment contexts.
- **Tamil (ta):** For Sri Lankan and southern Indian deployment contexts.

## 3. Architecture & Gemini Free Tier
The `LanguageService` module leverages the **Gemini 1.5 Flash API**.
- **Zero-Cost Constraint:** We use the Gemini Free Tier, which allows up to 15 requests per minute and 1,500 requests per day.
- **Caching Mechanism:** To preserve API quotas and reduce latency, every translation and language detection call is hashed and cached in memory. If a dispatcher repeatedly views the same translated SOP, it costs 0 API calls after the first view.
- **Graceful Fallback:** If the API key is missing, internet is down, or quotas are exhausted, the system seamlessly degrades to English processing, ensuring the core emergency routing pipeline never crashes.

## 4. How It Works
1. **Auto-Detection:** When an incident report arrives via text or Whisper Voice Intake, `detect_language()` identifies the 2-letter ISO code.
2. **Translation to English (Backend):** The text is translated to English (if necessary) so the local `Llama 3.1` model and embedding models can perform optimal semantic matching.
3. **Translation to Native (Frontend):** 
   - Retrieved SOPs are passed through `translate_sop()` to preserve markdown formatting while converting the text back to the citizen/dispatcher's native language.
   - Emergency contacts are fetched via `get_localized_emergency_numbers()`, providing culturally accurate hotlines (e.g., 100/101/108 for India, 119/1990 for Sri Lanka).

## 5. ASCII Compliance
To ensure complete system stability across all terminal environments and logging systems, internal labels and code references use ASCII phonetic transliterations (e.g., "Polisiya" instead of native Unicode scripts) where necessary. This prevents `UnicodeEncodeError` crashes during automated pipeline execution.
