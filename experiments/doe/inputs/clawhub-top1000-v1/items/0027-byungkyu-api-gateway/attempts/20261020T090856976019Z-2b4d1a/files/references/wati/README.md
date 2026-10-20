# WATI

## API Reference

> **Safety:** All write operations (POST, PUT, PATCH, DELETE) require explicit user confirmation before execution. Verify the target resource and intended effect with the user first. See the main [SKILL.md](../../SKILL.md#security--permissions) for full security policy.

**App name:** `wati`
**Upstream base URL:** `{tenant}.wati.io`

Replace the upstream base URL with the app name. Everything after the base URL including query strings is kept as-is. Any account-specific part of the base URL and the API credentials are stored in the Maton connection, and the gateway injects both so requests never carry them. For example:

- Upstream: `{tenant}.wati.io/api/v1/sendTemplateMessages`
- Gateway: `api.maton.ai/wati/api/v1/sendTemplateMessages`

**Note:** Both v1 and v2 endpoints are supported. v2 provides enhanced response formats with message tracking IDs.

### Contacts API

> **Adding or updating a contact writes personal data into WATI.** Phone numbers, names, and
> custom attributes are stored on the connected account and may enrol the person in later
> messaging. Use only details the user supplied for a contact they named, and confirm before
> writing.

#### Get Contacts

```bash
maton api '/wati/api/v1/getContacts?pageSize=10&pageNumber=1'
```

Optional filters: `name`, `attribute`, `createdDate`

**Query parameters:**
- `pageSize` - Number of results per page
- `pageNumber` - Page number (1-indexed)
- `name` (optional) - Filter by contact name
- `attribute` (optional) - Filter by attribute (format: `[{"name": "name", "operator": "contain", "value": "test"}]`)
- `createdDate` (optional) - Filter by created date (YYYY-MM-DD)

**Attribute operators:** `contain`, `notContain`, `exist`, `notExist`, `==`, `!=`, `valid`, `invalid`

#### Add Contact

```bash
maton api -X POST '/wati/api/v1/addContact/{whatsappNumber}' -H 'Content-Type: application/json' --input - <<'JSON'
{
  "name": "John Doe",
  "customParams": [
    {
      "name": "member",
      "value": "VIP"
    }
  ]
}
JSON
```

**Note:** `{whatsappNumber}` stands for a real value; fill it in before sending the request.

#### Update Contact Attributes

```bash
maton api -X POST '/wati/api/v1/updateContactAttributes/{whatsappNumber}' -H 'Content-Type: application/json' --input - <<'JSON'
{
  "customParams": [
    {
      "name": "member",
      "value": "VIP"
    }
  ]
}
JSON
```

**Note:** `{whatsappNumber}` stands for a real value; fill it in before sending the request.

### Messages API

#### Get Messages

```bash
maton api '/wati/api/v1/getMessages/{whatsappNumber}?pageSize=10&pageNumber=1'
```

**Note:** `{whatsappNumber}` stands for a real value; fill it in before sending the request.

**Query parameters:**
- `pageSize` - Number of results per page
- `pageNumber` - Page number (1-indexed)

#### Post a Session Message

Send a text message within an active session (24-hour window):

```bash
maton api -X POST '/wati/api/v1/sendSessionMessage/{whatsappNumber}' -H 'Content-Type: application/x-www-form-urlencoded' --input - <<'BODY'
messageText=Hello%20from%20WATI!
BODY
```

**Note:** `{whatsappNumber}` stands for a real value; fill it in before sending the request.

#### Post a Session File

> **The file's contents leave the machine.** The bytes of the file the user named are transmitted to WATI and delivered to the recipient's WhatsApp; confirm the exact file and recipient before sending. Assembling the multipart body locally is only how the upload is packaged — nothing here reads any file the user did not name.

```bash
# `maton api` sends a body verbatim but does not build a multipart envelope: assemble it
# first, then hand the result to --input. Nothing here handles a credential — the CLI injects it.
# Read only the path the user gave. The assembled body contains a copy of that file's bytes,
# so it is written under /tmp and deleted as soon as the upload returns.
FILE="$USER_SUPPLIED_PATH"            # exactly the path the user gave, never a discovered one
umask 077
BODY="$(mktemp "${TMPDIR:-/tmp}/wati-upload.XXXXXX")" || exit 1
trap 'rm -f -- "$BODY"' EXIT HUP INT TERM
BOUNDARY="maton-$$"
{
  printf -- '--%s\r\nContent-Disposition: form-data; name="file"; filename="%s"\r\nContent-Type: application/octet-stream\r\n\r\n' "$BOUNDARY" "$(basename "$FILE")"
  cat "$FILE"
  printf -- '\r\n'
  printf -- '--%s--\r\n' "$BOUNDARY"
} > "$BODY"

maton api -X POST '/wati/api/v1/sendSessionFile/{whatsappNumber}' \
  -H "Content-Type: multipart/form-data; boundary=$BOUNDARY" \
  --input "$BODY"
```

**Note:** `{whatsappNumber}` stands for a real value; fill it in before sending the request.

#### Post Session File

Send a file within an active session:

> **The file's contents leave the machine.** Read only the path the user named - never a file
> discovered on disk or a default name - and confirm the exact file and recipient before sending.

```bash
# maton api sends a body verbatim but does not build a multipart envelope:
# assemble it first, then hand the file to --input.
FILE="$USER_SUPPLIED_PATH"            # exactly the path the user gave, never a discovered one
BOUNDARY="maton-$$"
umask 077
BODY="$(mktemp "${TMPDIR:-/tmp}/wati-upload.XXXXXX")" || exit 1
trap 'rm -f -- "$BODY"' EXIT HUP INT TERM
{
  printf -- '--%s\r\nContent-Disposition: form-data; name="file"; filename="%s"\r\nContent-Type: application/octet-stream\r\n\r\n' "$BOUNDARY" "$(basename "$FILE")"
  cat "$FILE"
  printf -- '\r\n'
  printf -- '--%s--\r\n' "$BOUNDARY"
} > "$BODY"

maton api -X POST '/wati/api/v1/sendSessionFile/{whatsappNumber}?caption=Check%20this%20out' \
  -H "Content-Type: multipart/form-data; boundary=$BOUNDARY" \
  --input "$BODY"
```

**Note:** `{whatsappNumber}` stands for a real value; fill it in before sending the request.

### Message Templates API

> **Every send in this section delivers a real WhatsApp message to a real recipient.** That
> applies equally to the single-contact, bulk, v2, and CSV variants below. Recipient numbers and
> template variables are transmitted to WATI, messages cannot be recalled once sent, and bulk
> variants multiply the effect. Confirm the template, the personalisation fields, and the exact
> recipient list — including how many contacts it covers — with the user before sending.

#### Get Message Templates

```bash
maton api '/wati/api/v1/getMessageTemplates?pageSize=10&pageNumber=1'
```

#### Send Template Message

Send a pre-approved template message to a single contact:

```bash
maton api -X POST '/wati/api/v1/sendTemplateMessage?whatsappNumber={whatsappNumber}' -H 'Content-Type: application/json' --input - <<'JSON'
{
  "template_name": "order_update",
  "broadcast_name": "order_update",
  "parameters": [
    {
      "name": "name",
      "value": "John"
    },
    {
      "name": "ordernumber",
      "value": "12345"
    }
  ]
}
JSON
```

**Note:** `{whatsappNumber}` stands for a real value; fill it in before sending the request.

#### Send Template Messages (Bulk)

Send template messages to multiple contacts:

> **One call, many external messages.** Every recipient number and template variable below is
> transmitted to WATI and each contact receives a real WhatsApp message. Confirm the template, the
> personalisation fields and the exact recipient list - including how many contacts it covers -
> with the user before sending.

```bash
maton api -X POST '/wati/api/v1/sendTemplateMessages' -H 'Content-Type: application/json' --input - <<'JSON'
{
  "template_name": "order_update",
  "broadcast_name": "order_update",
  "receivers": [
    {
      "whatsappNumber": "14155551234",
      "customParams": [
        {
          "name": "name",
          "value": "John"
        },
        {
          "name": "ordernumber",
          "value": "12345"
        }
      ]
    },
    {
      "whatsappNumber": "14155555678",
      "customParams": [
        {
          "name": "name",
          "value": "Jane"
        },
        {
          "name": "ordernumber",
          "value": "67890"
        }
      ]
    }
  ]
}
JSON
```

#### Send Template Message via CSV

> **A CSV of contacts is personal data in bulk.** Every row — phone numbers, names, template variables — is transmitted to WATI and each contact receives a message. Confirm the file, the row count and the template with the user before uploading, and use only a CSV the user supplied.

```bash
# maton api sends a body verbatim but does not build a multipart envelope:
# assemble it first, then hand the file to --input.
CSV="$USER_SUPPLIED_PATH"             # exactly the CSV the user gave, never a discovered one
BOUNDARY="maton-$$"
umask 077
BODY="$(mktemp "${TMPDIR:-/tmp}/wati-upload.XXXXXX")" || exit 1
trap 'rm -f -- "$BODY"' EXIT HUP INT TERM
{
  printf -- '--%s\r\nContent-Disposition: form-data; name="whatsapp_numbers_csv"; filename="%s"\r\nContent-Type: application/octet-stream\r\n\r\n' "$BOUNDARY" "$(basename "$CSV")"
  cat "$CSV"
  printf -- '\r\n'
  printf -- '--%s--\r\n' "$BOUNDARY"
} > "$BODY"

maton api -X POST '/wati/api/v1/sendTemplateMessageCSV?template_name=order_update&broadcast_name=order_update' \
  -H "Content-Type: multipart/form-data; boundary=$BOUNDARY" \
  --input "$BODY"
```

v2 endpoints return `localMessageId` for tracking.

#### Send Template Message (v2)

```bash
maton api -X POST '/wati/api/v2/sendTemplateMessage?whatsappNumber={whatsappNumber}' -H 'Content-Type: application/json' --input - <<'JSON'
{
  "template_name": "order_update",
  "broadcast_name": "order_update",
  "parameters": [
    {
      "name": "name",
      "value": "John"
    }
  ]
}
JSON
```

**Note:** `{whatsappNumber}` stands for a real value; fill it in before sending the request.

**Response:**
```json
{
  "result": true,
  "error": null,
  "templateName": "order_update",
  "receivers": [
    {
      "localMessageId": "38aca0c0-f80a-409c-81ed-607fa5206529",
      "waId": "14155551234",
      "isValidWhatsAppNumber": true,
      "errors": []
    }
  ],
  "parameters": [
    {"name": "name", "value": "John"}
  ]
}
```

#### Send Template Messages (v2 - Bulk)

```bash
maton api -X POST '/wati/api/v2/sendTemplateMessages' -H 'Content-Type: application/json' --input - <<'JSON'
{
  "template_name": "order_update",
  "broadcast_name": "order_update",
  "receivers": [
    {
      "whatsappNumber": "14155551234",
      "customParams": [
        {"name": "name", "value": "John"}
      ]
    },
    {
      "whatsappNumber": "14155555678",
      "customParams": [
        {"name": "name", "value": "Jane"}
      ]
    }
  ]
}
JSON
```

**Response:**
```json
{
  "result": true,
  "error": null,
  "templateName": "order_update",
  "receivers": [
    {
      "localMessageId": "c486f386-d86d-431d-aa3b-fb1b6c494e58",
      "waId": "14155551234",
      "isValidWhatsAppNumber": true,
      "errors": []
    },
    {
      "localMessageId": "d597f497-e97e-542e-bb4c-718gb6d5a069",
      "waId": "14155555678",
      "isValidWhatsAppNumber": true,
      "errors": []
    }
  ]
}
```

### Interactive Messages API

> **These calls message a real recipient.** Sending an interactive buttons or list message is a
> write action that delivers content to an external WhatsApp contact. Confirm the recipient, the
> message body and the button or list options with the user before sending.

#### Send Interactive Buttons Message

```bash
maton api -X POST '/wati/api/v1/sendInteractiveButtonsMessage?whatsappNumber={whatsappNumber}' -H 'Content-Type: application/json' --input - <<'JSON'
{
  "header": {
    "type": "text",
    "text": "Order Status"
  },
  "body": "Your order #12345 is ready. What would you like to do?",
  "footer": "Reply within 24 hours",
  "buttons": [
    {
      "text": "Track Order"
    },
    {
      "text": "Contact Support"
    }
  ]
}
JSON
```

**Note:** `{whatsappNumber}` stands for a real value; fill it in before sending the request.

#### Send Interactive List Message

```bash
maton api -X POST '/wati/api/v1/sendInteractiveListMessage?whatsappNumber={whatsappNumber}' -H 'Content-Type: application/json' --input - <<'JSON'
{
  "header": "Choose an option",
  "body": "Please select from the menu below",
  "footer": "Powered by WATI",
  "buttonText": "View Options",
  "sections": [
    {
      "title": "Products",
      "rows": [
        {
          "title": "Product A",
          "description": "Best seller item"
        },
        {
          "title": "Product B",
          "description": "New arrival"
        }
      ]
    }
  ]
}
JSON
```

**Note:** `{whatsappNumber}` stands for a real value; fill it in before sending the request.

### Operators API

> **Reassignment changes who owns a live conversation.** Assigning an operator re-routes the chat
> and exposes its history to the new owner, which can disrupt an in-flight support thread. Confirm
> the contact number, the operator identity and the intended routing change with the user first.

#### Assign Operator

```bash
maton api -X POST '/wati/api/v1/assignOperator?email=agent@example.com&whatsappNumber={whatsappNumber}'
```

**Note:** `{whatsappNumber}` stands for a real value; fill it in before sending the request.

### Media API

#### Get Media

```bash
maton api '/wati/api/v1/getMedia?fileName={fileName}'
```

**Note:** `{fileName}` stands for a real value; fill it in before sending the request.

### Pagination

Uses page-based pagination:

```bash
maton api '/wati/api/v1/getContacts?pageSize=50&pageNumber=1'
```

**Query parameters:**
- `pageSize` - Results per page
- `pageNumber` - Page number (1-indexed)

### Notes

- WhatsApp numbers should include country code without + or spaces (e.g., `14155551234`)
- Session messages require an active 24-hour conversation window
- Template messages require pre-approved WhatsApp templates
- Interactive messages have character limits enforced by WhatsApp

### Resources

- [WATI API Documentation](https://docs.wati.io/reference/introduction)
- [WATI Help Center](https://docs.wati.io/)
- [Maton CLI Manual](https://cli.maton.ai/manual)
