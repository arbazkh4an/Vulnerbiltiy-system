## Functional Requirements

1. User can submit URL
2. System validates URL
3. System blocks:
   * localhost
   * 127.0.0.1
   * 10.x.x.x
   * 192.168.x.x
4. System creates scan record
5. Background worker processes scan
6. System updates scan status
7. AI generates vulnerability report
8. User can view scan history
9. Rate limit: max 5 scans/hour

---

## Non-Functional Requirements

* Response time (API): < 500ms
* Scan duration: < 90 seconds
* System uptime: 99%+
* Secure storage
* Scalable to 20 concurrent scans
* Zero blocking API calls

---

## Security Requirements

* HTTPS enforced
* JWT-based authentication
* Row-Level Security
* Strict input validation
* Scan consent logging
* No scanning private networks
