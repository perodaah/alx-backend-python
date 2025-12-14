# Postman Testing Guide

## 1. Auth: Obtain JWT Tokens

POST /api/token/
Body (JSON):
{
"username": "alice",
"password": "password123"
}
Expected: 200 { "access": "...", "refresh": "..." }

Save access token as variable: access_token

## 2. Auth: Refresh Token

POST /api/token/refresh/
Body:
{ "refresh": "{{refresh_token}}" }
Expected: 200 { "access": "..." }

## 3. Create Conversation

POST /api/conversations/
Headers: Authorization: Bearer {{access_token}}
Body:
{ "title": "Chat with Bob", "participants": [2] } # assuming current user id = 1, Bob id = 2
Expected: 201 { "id": X, ... }

Store conversation_id = response.id

## 4. Send Message (Nested)

POST /api/conversations/{{conversation_id}}/messages/
Headers: Authorization: Bearer {{access_token}}
Body:
{ "message_body": "Hello Bob!" }
Expected: 201 { "id": Y, "content": "...", "conversation": X }

## 5. List Conversations (Only Participant Ones)

GET /api/conversations/
Headers: Authorization: Bearer {{access_token}}
Expected: 200 list

## 6. List Messages With Pagination

GET /api/conversations/{{conversation_id}}/messages/?page=1
Expected: 200 { "count": ..., "results": [ ... up to 20 ... ] }

## 7. Filter Messages (Time Range / User)

GET /api/messages/?conversation_id={{conversation_id}}&created_after=2024-01-01T00:00:00Z&created_before=2025-12-31T23:59:59Z
Headers: Authorization: Bearer {{access_token}}

GET /api/messages/?user=2
Filters messages where sender or recipient is user id 2.

## 8. Unauthorized Access Test

GET /api/conversations/
(No Authorization header)
Expected: 401 or 403.

## 9. Template For Recording Results

Timestamp: 2025-11-18T12:00:00Z
Request: POST /api/conversations/
Payload: { "title": "Chat with Bob", "participants": [2] }
Status: 201
Response: { "id": 10, "title": "Chat with Bob", ... }
Notes: Success

Repeat template for each endpoint.

## 10. Negative Tests

- Use wrong token -> 401
- Access conversation not participant -> 403
- Send message to conversation not participant -> 403

## 11. Exporting

In Postman: Save all requests in a Collection "Messaging API".
Export (Collection v2.1) and attach or log summary here.
