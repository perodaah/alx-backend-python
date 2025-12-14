# Messaging App (Django + DRF)

Simple REST API for user-to-user conversations and messages.

## Features

- Custom user model [`User`](chats/models.py) with UUID primary key, email uniqueness, roles.
- Conversation model [`Conversation`](chats/models.py) with ManyToMany participants.
- Message model [`Message`](chats/models.py) linked to conversations and senders.
- Nested and flat endpoints via routers ([`chats/urls.py`](chats/urls.py)).
- Validation for participant count and non-empty message bodies in [`ConversationSerializer`](chats/serializers.py).
- Last message and message count summary fields.
- Auth: Session + Basic + JWT (see [`REST_FRAMEWORK` and `SIMPLE_JWT` settings](messaging_app/settings.py)).
- Query filtering, search, ordering in viewsets ([`ConversationViewSet`](chats/views.py), [`MessageViewSet`](chats/views.py)).
- Middleware: request logging, time-window access restriction, per-IP message rate limiting, role-based access restriction (see [`RequestLoggingMiddleware`, `RestrictAccessByTimeMiddleware`, `OffensiveLanguageMiddleware`, `RolepermissionMiddleware`](chats/middleware.py)).

## Middleware

Defined in [chats/middleware.py](chats/middleware.py) and enabled in [messaging_app/settings.py](messaging_app/settings.py):

- [`RequestLoggingMiddleware`](chats/middleware.py): Appends each request (timestamp, user, path) to requests.log.
- [`RestrictAccessByTimeMiddleware`](chats/middleware.py): Allows requests only between 18:00–21:00 server local time.
- [`OffensiveLanguageMiddleware`](chats/middleware.py): (Implemented as rate limiter) Max 5 POST message requests per IP per rolling 60s window.
- [`RolepermissionMiddleware`](chats/middleware.py): Blocks access unless user role is in {'admin','moderator'} (using `User.role` or Django flags/groups).

Order matters (see MIDDLEWARE list in [messaging_app/settings.py](messaging_app/settings.py)); custom middlewares run after core auth so `request.user` is available.

## Tech Stack

- Django 3.1
- Django REST Framework
- django-filter
- djangorestframework-simplejwt (JWT)
- SQLite (default; configurable in [`settings.py`](messaging_app/settings.py))

## Security Notes

- Development `SECRET_KEY` in [`settings.py`](messaging_app/settings.py); replace for production.
- JWT access & refresh tokens provided (see [`TokenObtainPairView`, `TokenRefreshView`](messaging_app/urls.py)).
- Switch `USERNAME_FIELD` in [`User`](chats/models.py) to `email` if email-based login desired.
- Review middleware restrictions (time window, role) for production suitability; adjust or remove if not desired.
- Rate limiting is in-memory; replace with Redis or more robust solution for scaling.

## Data Models

- [`User`](chats/models.py): UUID id, email, optional phone, role, mirrored `password_hash`.
- [`Conversation`](chats/models.py): UUID id, participants M2M, created_at.
- [`Message`](chats/models.py): UUID id, FK sender, FK conversation, body, timestamp, ordering by `-sent_at`.

## Serializers

- [`UserSerializer`](chats/serializers.py): write-only password; sets Django password + mirrors hash.
- [`MessageSerializer`](chats/serializers.py): includes sender detail via [`UserSerializer`](chats/serializers.py).
- [`ConversationSerializer`](chats/serializers.py): nested messages (optional), participants, computed `message_count`, `last_message`.

Validation rules:

- At least 2 participants.
- Each nested message must have non-blank `message_body`.

## Views / Endpoints

Base API prefix: `/api/` (see [`messaging_app/urls.py`](messaging_app/urls.py)).

Conversations:

- `GET /api/conversations/` (list user’s conversations)
- `POST /api/conversations/`
- `GET /api/conversations/{uuid}/`
- `PATCH /api/conversations/{uuid}/`
- `DELETE /api/conversations/{uuid}/`
- `POST /api/conversations/{uuid}/messages/` (custom action to send a message)

Messages (flat):

- `GET /api/messages/?conversation=<uuid>&sender=<uuid>`
- `POST /api/messages/`
- `GET /api/messages/{uuid}/`
- `PATCH /api/messages/{uuid}/`
- `DELETE /api/messages/{uuid}/`

Search / filter:

- Conversations: search on `messages__message_body`, filter `participants`, order by `created_at`.
- Messages: search `message_body`, filter `conversation`, `sender`, order by `sent_at`.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # if present
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Log in at `/api-auth/login/` for browsable API.

## Example Usage

Create a conversation with participants and initial messages:

```bash
curl -u user:pass -X POST http://localhost:8000/api/conversations/ \
  -H "Content-Type: application/json" \
  -d '{
        "participants": ["<user_uuid_1>", "<user_uuid_2>"],
        "messages": [
          {"message_body": "Hello there"},
          {"message_body": "Follow up"}
        ]
      }'
```

Send a message to an existing conversation:

```bash
curl -u user:pass -X POST http://localhost:8000/api/conversations/<conversation_uuid>/messages/ \
  -H "Content-Type: application/json" \
  -d '{"message_body": "New message"}'
```

Flat message creation:

```bash
curl -u user:pass -X POST http://localhost:8000/api/messages/ \
  -H "Content-Type: application/json" \
  -d '{"conversation": "<conversation_uuid>", "message_body": "Ping"}'
```

## Security Notes

- Development `SECRET_KEY` in [`settings.py`](messaging_app/settings.py); replace for production.
- Switch `USERNAME_FIELD` in [`User`](chats/models.py) to `email` if email-based login desired.
- Add token/JWT auth if required (not included).

## Testing

Placeholder test file [`tests.py`](chats/tests.py). Add API tests using `APITestCase` and `APIClient`.

## Extending

- Add pagination tuning in [`REST_FRAMEWORK`](messaging_app/settings.py).
- Register models in admin (`[`admin.py`](chats/admin.py)` currently empty).
- Add websockets (Channels) for real-time messaging if needed.

## License

Internal / unspecified.

## Maintenance

Run migrations on model changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

Rebuild environment caches on user model alterations.

## References

- DRF docs: [https://www.django-rest-framework.org/](https://www.django-rest-framework.org/)
- Django docs: [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
