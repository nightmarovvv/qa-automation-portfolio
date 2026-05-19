# qa-automation-portfolio

One application. Two complete UI test architectures. A REST API suite
on top. Same Allure dashboard.

The point of this repo isn't the app — it's how the tests are written.
The right test architecture depends on team size, suite size, and what
the team already knows. I'm equally at home in both stacks on the UI
side, and I'd rather show that than argue it.

```
.
├── app/             TaskFlow SPA — fixture under test (HTML + CSS + 1 JS file)
├── backend/         Minimal FastAPI service, used by the API suite
├── ui-pytest/       Track A — pytest + Playwright + classic Page Object Model
├── ui-vedro/        Track B — vedro + d42 + Webbricks-style page objects
├── api/             pytest + requests + ApiManager facade (shared shape)
└── .github/workflows/ci.yml
```

## start where your stack lives

| If your team uses… | Open |
|--------------------|------|
| pytest + Playwright + POM | [ui-pytest/](ui-pytest/) |
| vedro + d42 + Playwright  | [ui-vedro/](ui-vedro/) |
| REST API testing          | [api/](api/) |
| FastAPI fixture backend   | [backend/](backend/) |

The TaskFlow SPA in `app/` is the same in every case. The drawer, the
debounce, the validation, the toast — same product. What changes is the
test side.

## architecture choices, when each pays off

|                              | ui-pytest (pytest + POM)               | ui-vedro (vedro + d42)                            |
|------------------------------|----------------------------------------|---------------------------------------------------|
| Best fit                     | <300 tests, 1–3 QA, one product surface | 1000+ tests, 5+ QA, contract-heavy domain         |
| Style                        | classic POM, function-scope fixtures   | BDD-style steps, state-guaranteed contexts        |
| Locators                     | `data-test` (or CSS/xpath where it fits) | `data-test` strictly — no CSS/xpath               |
| Mocks                        | per-test `page.route()` helpers        | typed `MockedRoute` w/ `history` + strict counts  |
| API contracts in UI tests    | dict literals + `fake_*` helpers       | `d42` schemas (`fake(Schema % {...})`)            |
| Allure labels                | `@allure.feature/.story` directly      | typed catalog enforced by decorator               |
| Onboarding cost              | low                                    | higher, pays back at scale                        |
| Iteration speed              | fast                                   | slower per test, more guarantees per test         |
| Reading group                | familiar to most pytest users          | familiar to teams already on the vedro stack      |

Neither one is "better." `ui-pytest` is what I'd reach for on a smaller
team or a new project. `ui-vedro` is what earns its weight once the
suite outgrows fixtures and the team has contract-shaped pain that
schemas solve.

## test counts and runtime

| Suite       | Tests | Runtime           |
|-------------|------:|-------------------|
| ui-pytest   |    11 | ~12s (chromium)   |
| ui-vedro    |     7 | ~5s (chromium)    |
| api         |    22 | ~3s (no browser)  |

CI publishes a combined Allure report on every push to `main`.

→ **[Live Allure report](https://nightmarovvv.github.io/qa-automation-portfolio/)** *(published from `.github/workflows/ci.yml`)*

## running everything locally

```bash
# 1. install all the things
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt \
            -r api/requirements.txt \
            -r ui-pytest/requirements.txt
pip install -e ui-vedro
playwright install chromium

# 2. each suite has its own entry point — see its README
( cd backend && uvicorn main:app --port 8000 ) &     # API needs the backend
( cd api && pytest -v )
( cd ui-pytest && pytest -v )
( cd ui-vedro && make test )
```

The `app/` SPA is plain static files. UI suites boot a `python -m
http.server` against it; the FastAPI in `backend/` is only there for the
API suite.

## what's worth opening first

- `ui-pytest/tests/test_search.py` and `ui-vedro/scenarios/board/search_input_debounces_keystrokes.py`
  — same product, same assertion, two different ways to write it. Read
  them side by side.
- `api/custom_requester/custom_requester.py` — the base class every API
  client extends. Every request becomes an allure step with request +
  response attached.
- `api/conftest.py` — the fixture chain (`http_session` → `auth_token`
  → `auth_session` → `api_manager`). Picking the scopes is half the
  engineering.
- `ui-vedro/mocks/mocked_route.py` — async mock-server with typed
  `history`. The closest a Playwright-driven test will get to running
  against mountebank/jj.

## license

MIT.
