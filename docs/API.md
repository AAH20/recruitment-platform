# API Reference

## Base URL

```
https://api.recruitment-platform.example.com/v1
```

## Authentication

All API requests require authentication via JWT Bearer token.

```http
Authorization: Bearer <your-jwt-token>
```

### Obtaining a Token

```http
POST /v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400,
  "token_type": "Bearer"
}
```

---

## Endpoints

### Authentication

#### POST /auth/login

Authenticate a user and return JWT tokens.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | User email address |
| `password` | string | Yes | User password |

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400,
  "token_type": "Bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "recruiter"
  }
}
```

---

#### POST /auth/refresh

Refresh an expired access token.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `refresh_token` | string | Yes | Valid refresh token |

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400,
  "token_type": "Bearer"
}
```

---

#### POST /auth/logout

Invalidate the current access token.

**Response:** `204 No Content`

---

### Jobs

#### GET /jobs

Retrieve a paginated list of job postings.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `limit` | integer | 20 | Items per page (max 100) |
| `status` | string | — | Filter by status: `draft`, `published`, `closed`, `archived` |
| `department` | string | — | Filter by department |
| `location` | string | — | Filter by location |
| `search` | string | — | Full-text search query |
| `sort` | string | `-created_at` | Sort field and direction |

**Response:** `200 OK`

```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Senior Software Engineer",
      "description": "We are looking for...",
      "department": "Engineering",
      "location": "Remote",
      "employment_type": "full_time",
      "salary_min": 120000,
      "salary_max": 180000,
      "salary_currency": "USD",
      "status": "published",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "published_at": "2024-01-15T12:00:00Z",
      "closing_date": "2024-03-15T00:00:00Z",
      "hiring_manager_id": "uuid",
      "recruiter_id": "uuid",
      "tags": ["typescript", "react", "nodejs"],
      "applications_count": 42
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 156,
    "total_pages": 8
  }
}
```

---

#### POST /jobs

Create a new job posting.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Job title |
| `description` | string | Yes | Job description (supports Markdown) |
| `department` | string | Yes | Department name |
| `location` | string | Yes | Job location |
| `employment_type` | string | Yes | `full_time`, `part_time`, `contract`, `internship` |
| `salary_min` | number | No | Minimum salary |
| `salary_max` | number | No | Maximum salary |
| `salary_currency` | string | No | ISO 4217 currency code (default: `USD`) |
| `closing_date` | string | No | Application closing date (ISO 8601) |
| `tags` | string[] | No | Skill tags |
| `custom_fields` | object | No | Organization-specific fields |

**Response:** `201 Created`

```json
{
  "id": "uuid",
  "title": "Senior Software Engineer",
  "description": "We are looking for...",
  "department": "Engineering",
  "location": "Remote",
  "employment_type": "full_time",
  "salary_min": 120000,
  "salary_max": 180000,
  "salary_currency": "USD",
  "status": "draft",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "hiring_manager_id": "uuid",
  "recruiter_id": "uuid",
  "tags": ["typescript", "react", "nodejs"]
}
```

---

#### GET /jobs/:id

Retrieve a specific job posting by ID.

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "title": "Senior Software Engineer",
  "description": "We are looking for...",
  "department": "Engineering",
  "location": "Remote",
  "employment_type": "full_time",
  "salary_min": 120000,
  "salary_max": 180000,
  "salary_currency": "USD",
  "status": "published",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "published_at": "2024-01-15T12:00:00Z",
  "closing_date": "2024-03-15T00:00:00Z",
  "hiring_manager": {
    "id": "uuid",
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com"
  },
  "recruiter": {
    "id": "uuid",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com"
  },
  "tags": ["typescript", "react", "nodejs"],
  "applications_count": 42,
  "pipeline_stages": [
    {"id": "uuid", "name": "Applied", "order": 1, "count": 42},
    {"id": "uuid", "name": "Screening", "order": 2, "count": 18},
    {"id": "uuid", "name": "Interview", "order": 3, "count": 8},
    {"id": "uuid", "name": "Offer", "order": 4, "count": 2}
  ]
}
```

---

#### PUT /jobs/:id

Update an existing job posting.

**Request Body:** Same as POST /jobs (all fields optional)

**Response:** `200 OK` — Updated job object

---

#### DELETE /jobs/:id

Delete a job posting (soft delete).

**Response:** `204 No Content`

---

#### POST /jobs/:id/publish

Publish a draft job posting.

**Response:** `200 OK` — Updated job with `status: "published"`

---

#### POST /jobs/:id/close

Close an open job posting.

**Response:** `200 OK` — Updated job with `status: "closed"`

---

### Candidates

#### GET /candidates

Retrieve a paginated list of candidates.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `limit` | integer | 20 | Items per page |
| `status` | string | — | Filter by status |
| `job_id` | string | — | Filter by applied job |
| `search` | string | — | Full-text search |
| `tags` | string | — | Filter by tags (comma-separated) |

**Response:** `200 OK`

```json
{
  "data": [
    {
      "id": "uuid",
      "first_name": "Alice",
      "last_name": "Johnson",
      "email": "alice@example.com",
      "phone": "+1-555-0123",
      "location": "San Francisco, CA",
      "headline": "Full Stack Developer",
      "status": "active",
      "source": "linkedin",
      "rating": 4,
      "tags": ["react", "nodejs", "typescript"],
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-14T15:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 342,
    "total_pages": 18
  }
}
```

---

#### POST /candidates

Create a new candidate profile.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `first_name` | string | Yes | First name |
| `last_name` | string | Yes | Last name |
| `email` | string | Yes | Email address |
| `phone` | string | No | Phone number |
| `location` | string | No | Location |
| `headline` | string | No | Professional headline |
| `resume_url` | string | No | URL to resume file |
| `linkedin_url` | string | No | LinkedIn profile URL |
| `source` | string | No | Sourcing channel |
| `tags` | string[] | No | Skill tags |

**Response:** `201 Created`

---

#### GET /candidates/:id

Retrieve a specific candidate by ID.

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "first_name": "Alice",
  "last_name": "Johnson",
  "email": "alice@example.com",
  "phone": "+1-555-0123",
  "location": "San Francisco, CA",
  "headline": "Full Stack Developer",
  "summary": "Experienced developer with 6+ years...",
  "status": "active",
  "source": "linkedin",
  "rating": 4,
  "tags": ["react", "nodejs", "typescript"],
  "experience": [
    {
      "company": "Tech Corp",
      "title": "Senior Developer",
      "start_date": "2021-03",
      "end_date": null,
      "description": "Led development of..."
    }
  ],
  "education": [
    {
      "institution": "University of California",
      "degree": "B.S. Computer Science",
      "graduation_year": 2018
    }
  ],
  "applications": [
    {
      "id": "uuid",
      "job_id": "uuid",
      "job_title": "Senior Software Engineer",
      "status": "interview",
      "stage": "Technical Interview",
      "applied_at": "2024-01-12T09:00:00Z"
    }
  ],
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-14T15:30:00Z"
}
```

---

#### PUT /candidates/:id

Update a candidate profile.

**Request Body:** Same as POST /candidates (all fields optional)

**Response:** `200 OK` — Updated candidate object

---

#### DELETE /candidates/:id

Delete a candidate profile.

**Response:** `204 No Content`

---

#### POST /candidates/:id/apply

Submit a candidate application for a job.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `job_id` | string | UUID | Job ID to apply for |
| `cover_letter` | string | No | Cover letter text |
| `resume_url` | string | No | Override resume URL |
| `answers` | object | No | Answers to application questions |

**Response:** `201 Created`

```json
{
  "id": "uuid",
  "candidate_id": "uuid",
  "job_id": "uuid",
  "status": "applied",
  "stage": "Applied",
  "applied_at": "2024-01-15T10:30:00Z",
  "cover_letter": "I am excited to apply..."
}
```

---

#### GET /candidates/:id/applications

Retrieve all applications for a candidate.

**Response:** `200 OK`

```json
{
  "data": [
    {
      "id": "uuid",
      "job_id": "uuid",
      "job_title": "Senior Software Engineer",
      "department": "Engineering",
      "status": "interview",
      "stage": "Technical Interview",
      "applied_at": "2024-01-12T09:00:00Z",
      "updated_at": "2024-01-14T15:30:00Z"
    }
  ]
}
```

---

### Interviews

#### GET /interviews

Retrieve a paginated list of interviews.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `limit` | integer | 20 | Items per page |
| `status` | string | — | `scheduled`, `completed`, `cancelled`, `no_show` |
| `job_id` | string | — | Filter by job |
| `candidate_id` | string | — | Filter by candidate |
| `interviewer_id` | string | — | Filter by interviewer |
| `from` | string | — | Start date (ISO 8601) |
| `to` | string | — | End date (ISO 8601) |

**Response:** `200 OK`

```json
{
  "data": [
    {
      "id": "uuid",
      "job_id": "uuid",
      "job_title": "Senior Software Engineer",
      "candidate_id": "uuid",
      "candidate_name": "Alice Johnson",
      "interviewer_id": "uuid",
      "interviewer_name": "Jane Smith",
      "type": "technical",
      "status": "scheduled",
      "scheduled_at": "2024-01-20T14:00:00Z",
      "duration_minutes": 60,
      "location": "Google Meet",
      "meeting_url": "https://meet.google.com/abc-defg-hij",
      "notes": "Focus on system design and React patterns",
      "feedback": null,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 89,
    "total_pages": 5
  }
}
```

---

#### POST /interviews

Schedule a new interview.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `job_id` | string | UUID | Job ID |
| `candidate_id` | string | UUID | Candidate ID |
| `interviewer_id` | string | UUID | Interviewer user ID |
| `type` | string | Yes | `phone`, `video`, `onsite`, `technical`, `behavioral` |
| `scheduled_at` | string | Yes | Start time (ISO 8601) |
| `duration_minutes` | integer | Yes | Duration in minutes |
| `location` | string | No | Location or meeting link |
| `notes` | string | No | Interview notes |

**Response:** `201 Created`

---

#### GET /interviews/:id

Retrieve a specific interview by ID.

**Response:** `200 OK`

---

#### PUT /interviews/:id

Update an existing interview.

**Request Body:** Same as POST /interviews (all fields optional)

**Response:** `200 OK` — Updated interview object

---

#### DELETE /interviews/:id

Cancel/delete an interview.

**Response:** `204 No Content`

---

#### POST /interviews/:id/feedback

Submit interview feedback.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rating` | integer | Yes | Rating 1-5 |
| `strengths` | string | No | Candidate strengths |
| `weaknesses` | string | No | Areas for improvement |
| `notes` | string | No | Additional notes |
| `recommendation` | string | Yes | `strong_hire`, `hire`, `lean_hire`, `lean_no_hire`, `no_hire` |

**Response:** `200 OK`

---

### Applications

#### GET /applications

Retrieve a paginated list of applications.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `limit` | integer | 20 | Items per page |
| `job_id` | string | — | Filter by job |
| `candidate_id` | string | — | Filter by candidate |
| `status` | string | — | Filter by status |
| `stage` | string | — | Filter by pipeline stage |

**Response:** `200 OK`

---

#### GET /applications/:id

Retrieve a specific application by ID.

**Response:** `200 OK`

---

#### PUT /applications/:id

Update an application (e.g., move to a different stage).

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | No | Application status |
| `stage` | string | No | Pipeline stage |
| `rating` | integer | No | Candidate rating 1-5 |
| `notes` | string | No | Recruiter notes |

**Response:** `200 OK` — Updated application object

---

#### POST /applications/:id/notes

Add a note to an application.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | string | Yes | Note content |
| `type` | string | No | `general`, `interview`, `reference` |

**Response:** `201 Created`

---

### Notifications

#### GET /notifications

Retrieve notifications for the authenticated user.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `limit` | integer | 20 | Items per page |
| `unread` | boolean | — | Filter by read status |

**Response:** `200 OK`

---

#### PUT /notifications/:id/read

Mark a notification as read.

**Response:** `200 OK`

---

#### PUT /notifications/read-all

Mark all notifications as read.

**Response:** `200 OK`

---

### Analytics

#### GET /analytics/dashboard

Retrieve dashboard metrics for the authenticated user's organization.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `from` | string | — | Start date (ISO 8601) |
| `to` | string | — | End date (ISO 8601) |
| `department` | string | — | Filter by department |

**Response:** `200 OK`

```json
{
  "period": {
    "from": "2024-01-01",
    "to": "2024-01-31"
  },
  "summary": {
    "total_jobs": 45,
    "active_jobs": 28,
    "total_applications": 1250,
    "new_applications": 342,
    "interviews_scheduled": 89,
    "offers_extended": 12,
    "hires_made": 8,
    "time_to_hire_avg_days": 28.5,
    "cost_per_hire_avg": 3200
  },
  "pipeline": {
    "applied": 1250,
    "screening": 342,
    "interview": 89,
    "offer": 12,
    "hired": 8,
    "rejected": 899
  },
  "sources": [
    {"name": "LinkedIn", "count": 456, "percentage": 36.5},
    {"name": "Indeed", "count": 312, "percentage": 25.0},
    {"name": "Referral", "count": 234, "percentage": 18.7},
    {"name": "Direct", "count": 248, "percentage": 19.8}
  ],
  "departments": [
    {"name": "Engineering", "open_jobs": 12, "applications": 456},
    {"name": "Product", "open_jobs": 8, "applications": 234},
    {"name": "Design", "open_jobs": 5, "applications": 123}
  ]
}
```

---

#### GET /analytics/jobs/:id

Retrieve analytics for a specific job posting.

**Response:** `200 OK`

```json
{
  "job_id": "uuid",
  "job_title": "Senior Software Engineer",
  "views": 1234,
  "applications": 42,
  "conversion_rate": 3.4,
  "pipeline": {
    "applied": 42,
    "screening": 18,
    "interview": 8,
    "offer": 2,
    "hired": 1
  },
  "time_in_stage": {
    "applied_to_screening_avg_days": 3.2,
    "screening_to_interview_avg_days": 5.1,
    "interview_to_offer_avg_days": 7.8,
    "offer_to_hire_avg_days": 4.5
  },
  "sources": [
    {"name": "LinkedIn", "count": 18},
    {"name": "Indeed", "count": 12},
    {"name": "Referral", "count": 8},
    {"name": "Direct", "count": 4}
  ]
}
```

---

### Webhooks

#### GET /webhooks

List all configured webhooks.

**Response:** `200 OK`

---

#### POST /webhooks

Register a new webhook endpoint.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | Webhook endpoint URL |
| `events` | string[] | Yes | Events to subscribe to |
| `secret` | string | No | Signing secret |

**Response:** `201 Created`

---

#### DELETE /webhooks/:id

Remove a webhook.

**Response:** `204 No Content`

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Email is required"
      }
    ]
  }
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | OK — Request succeeded |
| `201` | Created — Resource created |
| `204` | No Content — Request succeeded, no body |
| `400` | Bad Request — Invalid request |
| `401` | Unauthorized — Authentication required |
| `403` | Forbidden — Insufficient permissions |
| `404` | Not Found — Resource not found |
| `409` | Conflict — Resource conflict |
| `422` | Unprocessable Entity — Validation error |
| `429` | Too Many Requests — Rate limit exceeded |
| `500` | Internal Server Error |

### Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing credentials |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |

---

## Rate Limiting

API requests are rate-limited per authenticated user:

| Tier | Requests/minute | Burst |
|------|-----------------|-------|
| Standard | 60 | 100 |
| Premium | 300 | 500 |
| Enterprise | 1000 | 2000 |

Rate limit headers are included in all responses:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1705315800
```

---

## Pagination

List endpoints return paginated results with the following structure:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 156,
    "total_pages": 8
  }
}
```

---

## SDKs & Client Libraries

- **JavaScript/TypeScript**: `@recruitment-platform/sdk`
- **Python**: `recruitment-platform`
- **Go**: `github.com/recruitment-platform/go-sdk`

---

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for API version history.
