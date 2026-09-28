# Testing Strategy

Automated tests live in `tests/test_app.py` (pytest + Flask test client, 15 tests, all passing).
Run them with:

```bash
pytest tests/ -v
```

## Test Case Table

| Test ID | Scenario | Input | Expected Result | Actual Result | Pass/Fail |
|---|---|---|---|---|---|
| TC-01 | New user registration | Valid name/email/password | 201, user created | 201, user created | Pass |
| TC-02 | Existing email registration | Duplicate email | 409, error message | 409 returned | Pass |
| TC-03 | Valid login | Correct email/password | 200 + access_token | 200 + token | Pass |
| TC-04 | Invalid login | Wrong password | 401, error message | 401 returned | Pass |
| TC-05 | Unauthorized dashboard access | No token on `/profile` | 401 | 401 returned | Pass |
| TC-06 | Profile creation/update | Valid profile fields | 200, profile updated | 200, updated | Pass |
| TC-07 | Diet plan generation | Authenticated user | 201, full plan object | 201, plan returned | Pass |
| TC-08 | Vegetarian preference | `dietary_preference=vegetarian` | Meals from vegetarian dataset | Correct dataset used | Pass |
| TC-09 | Vegan preference | `dietary_preference=vegan` | Meals from vegan dataset | Correct dataset used | Pass |
| TC-10 | Different goal | `goal=fitness` | `nutrition_summary.goal == fitness` | Matched | Pass |
| TC-11 | AI API failure / not configured | No `AI_API_KEY` set | Falls back to rule-based, `source=rule_based` | Fallback triggered | Pass |
| TC-12 | Rule-based fallback | Same as TC-11 | Plan still generated successfully | Plan generated | Pass |
| TC-13 | Save diet plan | Generate plan | Row created in `diet_plans` | Row created | Pass |
| TC-14 | Retrieve plan | `GET /plans/{id}` | Correct plan returned | Correct plan returned | Pass |
| TC-15 | Upload file | Valid `.png` file | 201, file metadata returned | 201, metadata returned | Pass |
| TC-16 | Retrieve file list | `GET /files` | List includes uploaded file | File present in list | Pass |
| TC-17 | Invalid file type | `.exe` file | 400, rejected | 400 returned | Pass |
| TC-18 | User A cannot retrieve User B's data | User B requests User A's `plan_id` | 404 (not leaked) | 404 returned | Pass |
| TC-19 | Logout | `POST /logout` then reuse token | Token revoked, subsequent request 401 | 401 returned | Pass |
| TC-20 | Cloud/database failure handling | DB unreachable (simulated) | 500 handled gracefully via `errorhandler(500)`, no stack trace leaked | Not tested | Not tested |

> TC-20 is exercised manually (temporarily point `DATABASE_URL` at an unreachable host and
> confirm the API returns a clean 500 JSON error instead of crashing) since simulating a live
> DB outage inside an automated in-memory test is impractical.

## Automated Test Coverage (`tests/test_app.py`)

- Registration: new user, duplicate email
- Login: valid, invalid
- Authorization: protected route without token
- Profile: update
- Diet plan generation: vegetarian, vegan, different goal, AI-fallback
- Plan persistence: save + retrieve
- File upload: valid upload, invalid extension rejected
- Security: cross-user data isolation
- Logout: token revocation enforced
