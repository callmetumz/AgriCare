# Step 5 prototype traceability

| Requirement / use case | Prototype evidence |
|---|---|
| UC01 / FR-02 to FR-04 - animal profiles | `POST /api/animals`, `GET /api/animals`, Animals screen |
| UC02 / FR-05 to FR-06 - vaccination | `POST /api/animals/{id}/vaccinations`; due-date calculation; Veterinarian-only role check |
| UC03 / FR-07 - illness reporting | `POST /api/animals/{id}/illness`; Low/Moderate/Urgent classification |
| UC04 / FR-08 - quarantine | `POST /api/animals/{id}/quarantine`; transition table; Veterinarian-only role check |
| UC06 / FR-10 - possible outbreak | 72-hour enclosure/body-system counting rule creates `OutbreakAlert` |
| UC08 / FR-12 - dashboard | `GET /api/dashboard` and dashboard cards |
| UC10 / FR-14 - audit trail | `AuditLog`, `GET /api/audit`, role restriction |
| NFR-02 - least privilege | backend role checks on clinical actions |
| NFR-04 - integrity | duplicate tag validation and invalid quarantine transitions rejected |
| NFR-06/NFR-07 - usability/accessibility | short forms, responsive layout, text labels paired with status colour |
| NFR-09 - maintainability | separated backend models/schemas/database/API and separate frontend assets |
