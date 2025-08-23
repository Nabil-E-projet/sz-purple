# Guide: Payslip File Privacy

This project supports automatic deletion of uploaded payslip files after analysis to protect user privacy.

## Settings

- DELETE_PAYSLIP_FILE_AFTER_ANALYSIS
  - Type: boolean (env var)
  - Default: true
  - Behavior: When true, the uploaded file is deleted from disk after a successful analysis.

- DELETE_PAYSLIP_FILE_ON_ERROR
  - Type: boolean (env var)
  - Default: false
  - Behavior: When true, the uploaded file is deleted even if analysis fails. Use with caution as it prevents retrying with the same file.

Configure via environment variables in `sz-back/salariz/.env` or your deployment environment, for example:

```env
DELETE_PAYSLIP_FILE_AFTER_ANALYSIS=true
DELETE_PAYSLIP_FILE_ON_ERROR=false
```

## API Behavior when files are deleted

- GET /documents/payslips/{id}/file
  - If the file has been deleted (privacy) or is missing on disk, the API returns:
    - Status: 410 Gone
    - JSON body:
      - When deleted after analysis:
        ```json
        {"error": "file_deleted", "message": "Le fichier a été supprimé après analyse pour des raisons de confidentialité.", "filename": "<original>"}
        ```
      - When missing on disk:
        ```json
        {"error": "file_missing", "message": "Le fichier source n'est plus disponible sur le serveur.", "filename": "<original>"}
        ```

## Notes

- Files are deleted after single-document analyses via the analysis service when `DELETE_PAYSLIP_FILE_AFTER_ANALYSIS=true`.
- Bulk upload flows currently do not force deletion after each analysis; future improvements may extend this behavior.
- The model keeps `original_filename` for display purposes and sets `file_deleted=true` once the file is removed.
