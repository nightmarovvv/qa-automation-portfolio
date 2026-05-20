<div align="center">

# qa-automation-portfolio

The same SPA. Three test architectures. One Allure dashboard.

[![ci](https://github.com/nightmarovvv/qa-automation-portfolio/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/nightmarovvv/qa-automation-portfolio/actions/workflows/ci.yml)
&nbsp;
[![allure](https://img.shields.io/badge/allure-live-171717?style=flat-square&labelColor=171717)](https://nightmarovvv.github.io/qa-automation-portfolio/report/)
&nbsp;
[![license](https://img.shields.io/badge/license-MIT-171717?style=flat-square&labelColor=171717)](LICENSE)

<br/>

[**Landing**](https://nightmarovvv.github.io/qa-automation-portfolio/) · [**Live Allure**](https://nightmarovvv.github.io/qa-automation-portfolio/report/) · [Hiring lead](#for-the-hiring-lead) · [Fellow QA](#for-the-fellow-qa) · [Tradeoffs](#tradeoffs)

<br/>

<img src="docs/img/demo-create-task.gif" width="900" alt="A test driving the SPA — open drawer, fill form, save, card lands, toast" />

</div>

<br/>

The interesting part of this repo isn't the SPA. It's that the three
suites around it differ where it matters and agree where it should.
A `pytest` + Playwright + POM suite for the 80% of teams. A `vedro` +
`d42` + Webbricks-style suite for the 20% that grow into a thousand
tests. A REST API suite hitting a real FastAPI service with real JWT.

## for the hiring lead

If you're deciding whether to schedule the next interview, three
artifacts answer most questions:

1. The [**live Allure report**](https://nightmarovvv.github.io/qa-automation-portfolio/report/) — 36 cases, 100% pass, rebuilt on every push to `main`.
2. [**Same test, two stacks**](#same-test-two-stacks) — the identical debounce assertion written against the same SPA in pytest and in vedro. Read them side by side; that's the senior conversation.
3. [**Tradeoffs**](#tradeoffs) — when each stack earns its weight, where it overspends.

Email and Telegram at the bottom.

## for the fellow QA

Five files, ~250 lines total:

1. [`ui-vedro/mocks/mocked_route.py`](ui-vedro/mocks/mocked_route.py) — typed `MockedRoute` with `.history` and a strict count check on `__aexit__`.
2. [`ui-vedro/schemas/__init__.py`](ui-vedro/schemas/__init__.py) — every constraint cites its source.
3. [`api/conftest.py`](api/conftest.py) — fixture chain with scope decisions annotated.
4. [`api/custom_requester/custom_requester.py`](api/custom_requester/custom_requester.py) — base class turning every request into an Allure step with body attached.
5. [`TESTING.md`](TESTING.md) — the 10 rules everything follows. The [`docs/adr/`](docs/adr/) series argues each one.

## numbers

|                  | api                                | ui-pytest                  | ui-vedro                              |
|------------------|------------------------------------|----------------------------|---------------------------------------|
| tests / scenarios | **25**                            | **11**                     | **7 (one ×3)**                        |
| runtime           | ~3s                                | ~12s                       | ~5s                                   |
| stack             | pytest + requests + ApiManager     | pytest + Playwright + POM  | vedro + Playwright + d42              |
| isolation         | wipe store per test                | mocks via `page.route()`   | typed `MockedRoute` w/ strict counts  |

**36 in the Allure dashboard. 7 more vedro scenarios in CI logs. 43
total, ~17s wall time, 0 flakes since the suite went green.**

<a href="https://nightmarovvv.github.io/qa-automation-portfolio/report/">
  <img src="docs/img/allure-overview.png" width="900" alt="Allure overview — 36 tests, 100% pass" />
</a>

<sub>Why 36 not 43: vedro's allure-reporter ships per-scenario JSON differently from pytest's plugin; the merge step needs a small adapter. Tracked. Until then the 7 scenarios live in the CI log, not the dashboard.</sub>

## same test, two stacks

The strongest piece of evidence in the repo: the same assertion — *the
SPA's 300 ms debounce coalesces 5 keystrokes into one backend call* —
written in both styles.

<table>
<tr>
<th width="50%">ui-pytest <sub>(classic POM, pytest)</sub></th>
<th width="50%">ui-vedro <sub>(BDD steps, typed mock-server)</sub></th>
</tr>
<tr>
<td valign="top">

```python
class TestSearch:

    @pytest.mark.smoke
    def test_debounce(self, board):
        matching = fake_task(title="Alpha launch retrospective")
        mock = mock_tasks_list(
            board.page, {"data": [matching], "total": 1}
        )

        board.open()
        board.wait_until_ready()
        mock.requests.clear()

        board.search("alpha", delay_ms=30)
        board.page.wait_for_timeout(600)

        assert len(mock.requests) == 1
        assert mock.requests[0].query == {"q": "alpha"}
```

</td>
<td valign="top">

```python
@allure_labels(
    Feature.Search, Story.Search,
    Priority.Critical, AllureID("B-301"),
)
class Scenario(vedro.Scenario):
    subject = "Search input debounces keystrokes..."

    async def given_matching_task(self):
        self.matching_id = fake(ValidIDSchema)
        self.search_response = {"data": [fake(
            TaskSchema % {"id": self.matching_id,
                          "title": "Alpha launch retrospective"})],
            "total": 1}

    async def when_user_types(self):
        async with mocked_tasks_list(
            self.page, self.search_response,
            wait_for_requests=None,
        ) as self.mock:
            await self.board.header.search_input.type(
                "alpha", delay_ms=40)
            await self.board.task_list.get_list_task_by_id(
                self.matching_id).wait_for()

    async def then_exactly_one_call(self):
        assert len(self.mock.history) == 1
```

</td>
</tr>
</table>

Same product. Same assertion. Different texture. Pick what your team
will actually maintain.

## tradeoffs

|                    | ui-pytest                                  | ui-vedro                                              |
|--------------------|--------------------------------------------|-------------------------------------------------------|
| Best fit           | <300 tests, 1–3 QA                          | 1000+ tests, 5+ QA                                     |
| Onboarding         | hours                                       | days, with payback at scale                            |
| Locators           | `data-test` first, CSS if no other handle    | `data-test` only — CSS/xpath forbidden                |
| Mocks              | per-test `page.route()` helpers              | typed `MockedRoute` + `.history` + strict count       |
| Gives up           | scales painfully past ~300 tests             | every test takes longer to write; new hires need a week |

→ [ADR-001](docs/adr/0001-locators-data-test-only.md) · [ADR-002](docs/adr/0002-mock-count-on-exit.md) · [ADR-003](docs/adr/0003-schemas-cite-source.md) · [ADR-004](docs/adr/0004-typed-allure-labels.md) · [ADR-005](docs/adr/0005-fixture-scopes-picked.md)

---

<details>
<summary><b>What a mock-discipline failure looks like</b></summary>

The strict count check itself, ~12 lines from `ui-vedro/mocks/mocked_route.py`:

```python
async def __aexit__(self, exc_type, exc, tb) -> None:
    await self._page.unroute("**/*", self._handle)
    if exc_type is not None or self._wait_for_requests is None:
        return
    actual = len(self._history)
    if actual != self._wait_for_requests:
        raise AssertionError(
            f"Mock expected {self._wait_for_requests} {self._method} call(s), "
            f"got {actual}. Recorded URLs: {[r.url for r in self._history]}"
        )
```

If the debounce broke on a feature branch:

```
AssertionError: Mock expected 1 GET call(s), got 3.
Recorded URLs: ['…/api/tasks?q=a', '…/api/tasks?q=alp', '…/api/tasks?q=alpha']
```

</details>

<details>
<summary><b>Architecture + fixture chain</b></summary>

```mermaid
flowchart LR
    subgraph SUT
        SPA["app/<br/>TaskFlow SPA"]
        BE["backend/<br/>FastAPI + JWT"]
    end
    subgraph "test suites"
        UIP["ui-pytest/"]
        UIV["ui-vedro/"]
        API["api/"]
    end
    subgraph "ci / reporting"
        CI["GitHub Actions matrix"]
        AL["Allure on Pages"]
    end
    UIP --> SPA
    UIV --> SPA
    API --> BE
    UIP --> CI
    UIV --> CI
    API --> CI
    CI --> AL
```

```mermaid
flowchart LR
    A["http_session<br/><i>session</i>"]
    B["auth_token<br/><i>session</i>"]
    C["auth_session<br/><i>session</i>"]
    D["api_manager<br/><i>class</i>"]
    E["clean_tasks<br/><i>function</i>"]
    A --> B --> C --> D --> E
```

`auth_token` is session-scope because POST /login is ~200 ms; 100 tests
at function-scope would burn 20 seconds doing nothing. `clean_tasks`
is per-function because state isolation between tests is non-negotiable.
→ [ADR-005](docs/adr/0005-fixture-scopes-picked.md).

</details>

<details>
<summary><b>Deliberately not included</b></summary>

**No retry-on-failure decorator.** A flaky test is a test asserting on
the wrong thing. The fix lives in the assertion, not in the runner.

**No BDD Gherkin layer.** vedro's scenario class is already a readable
DSL — adding Cucumber would be two DSLs solving one problem.

**No `time.sleep`** — anywhere. Contexts wait for the thing the next
step needs, not for a clock.

</details>

<details>
<summary><b>Running locally</b></summary>

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt \
            -r api/requirements.txt \
            -r ui-pytest/requirements.txt
pip install -e ui-vedro
playwright install chromium

( cd backend && uvicorn main:app --port 8000 ) &

cd api        && pytest -v
cd ui-pytest  && pytest -v
cd ui-vedro   && make test
```

</details>

---

<div align="center"><sub>

[alexshabunin.com](https://alexshabunin.com) · [@shanaleks](https://t.me/shanaleks) · shanaleks0007@gmail.com · MIT

</sub></div>
