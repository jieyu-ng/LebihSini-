# LebihSini GreenProof Privacy Controls

These are MVP privacy and retention controls for the current extraction workflow.

- Raw uploads are not intended for public exposure.
- API credentials remain server-side and must not be embedded in frontend code.
- Raw site documents may contain names, prices, phone numbers, and addresses.
- Structured fields should be retained in preference to storing full document contents.
- Raw evidence should be referenced through content references rather than embedded file blobs whenever possible.
- User confirmation is required before confirmed demand data becomes the system of record.
- Images and raw evidence should remain removable in a future persistence layer.
- Logs must not contain full raw documents or credential values.
- AI output does not certify safety, maintenance quality, or ESG compliance.
