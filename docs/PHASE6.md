# LALA Phase 6: Online Cybersecurity Intelligence Platform

System Identity: **LALA**  
Target User: **Mandar**

---

## 🎯 Phase 6 Overview

Phase 6 evolves LALA into an **Online Cybersecurity Intelligence & Threat Investigation Platform**.

### Key Features:
1. **Secrets & API Key Manager**: Environment-based secret loading (`LALA_VIRUSTOTAL_API_KEY`, etc.).
2. **Network Security Engine**: Domain allowlisting (`virustotal.com`, `api.abuseipdb.com`, `otx.alienvault.com`, `urlhaus-api.abuse.ch`, `mb-api.abuse.ch`, `services.nvd.nist.gov`, `www.cisa.gov`).
3. **Response Sanitizer**: Strips HTML tags, prompt injection phrases, and script tags from untrusted API payloads.
4. **Intelligence Cache**: SQLite TTL cache (`F:\LALA\Memory\lala_intel_cache.db`).
5. **Rate Limiter**: Exponential backoff and request throttling (`MAX_PROVIDER_RETRIES = 2`).
6. **IOC Correlation**: Multi-indicator graph matching (Hash -> IP -> Domain -> ATT&CK -> CVE).
7. **Investigation Cases**: Case tracking and report generation (`F:\LALA\Investigations\Reports\`).
8. **Explicit Privacy Toggle**: `online_intelligence_enabled = False` by default.
