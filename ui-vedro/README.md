# ui-vedro

End-to-end suite for the TaskFlow SPA built on the stack I use at work:
vedro + Playwright + d42 + allure.

```bash
make install
make test          # boots the SPA, runs the suite, kills the server
make test-headed   # same but with a visible browser
```

5 scenarios, 7 runs (one parametrized x3), ~5 sec total.

## stack

- **vedro** — async, BDD-style scenario runner
- **Playwright** (Chromium, headless)
- **d42** — typed schemas + fake generator
- **allure** — reporting
- fixture SPA in `../app/` (plain HTML/CSS/JS, no build step)

Python 3.11+. `python -m http.server` is the whole infra.

## layout

```
ui-vedro/
├── interfaces/web/
│   ├── web_elements/             BaseElement, BaseButton, BaseInput, BaseText
│   └── pages/
│       ├── page.py               BasePage + Header / Toast
│       └── board/
│           ├── board_page.py
│           └── components/       TaskList, TaskDrawer, TagsPicker
├── contexts/                     vedro contexts (state-guaranteed)
├── mocks/                        Playwright route wrappers with .history
├── schemas/                      d42 base + entity contracts
├── scenarios/board/              5 scenarios, 7 runs
├── helpers/                      pure functions
├── dicts/                        allure labels, translations, enums
└── Makefile
```

## what to open first

1. `scenarios/board/search_input_debounces_keystrokes.py` — types 5 chars
   in 200ms and asserts the backend was hit exactly once. Proves the
   300ms debounce is real.
2. `mocks/mocked_route.py` — async context manager over `page.route()`.
   Records every matching request as a typed `RecordedRequest`, raises
   on `__aexit__` if the observed count doesn't match expectations.
3. `schemas/__init__.py` — shared base schemas. Every constraint cites
   its source (HTML attr, regex from validator, API contract). No bare
   `schema.str` or `schema.int`.
4. `interfaces/web/pages/board/components/task_list.py` — `_ListXItem`
   pattern. Cards addressed by stable ULID, not by index.

## design choices

**Page objects.** Inheritance for page-level only (one URL, one
`BasePage`). Everything inside the page is a `BaseElement` composed
downward. Container's `data-test` contributes a scope, children resolve
relative to it.

**Locators: `data-test` only.** CSS/XPath forbidden. `data-test` is a
contract owned by the dev team alongside the component. Restyles don't
break tests.

**Contexts return only when the page is interactive.** `opened_board_page`
waits for the toolbar counter, not for `goto` to resolve.
`opened_create_task_drawer` waits for the title input to mount, not for
the drawer container's `hidden` flag.

**Mocks are mock-server style.** Each domain mock takes a ready-made
`response_body` (built via `fake(Schema % {...})`) and a `wait_for_requests`
count. `history` exposes typed `RecordedRequest`s with decoded JSON, parsed
query, lowercased headers. Strict count check on exit catches "mock returned
200 but UI never asked".

**Schemas are shared contracts.** Tests narrow them via `Schema % {...}`,
they don't redefine the shape. Every bound has a comment pointing at the
source (HTML maxlength, regex, API behavior).

**Allure labels are typed.** `@allure_labels(Feature.Board, Story.CreateTask,
Priority.Critical, AllureID("B-101"))`. Order enforced by the decorator,
misspelled labels caught at import.

**Parametrized scenarios get unique AllureIDs** via `allure.dynamic.id()`
in the first step. Each parameter row keeps an addressable history.

## ci

`../.github/workflows/ci.yml` runs the suite on every push and PR.
Allure results uploaded as build artifacts; on `main` they get
published to GitHub Pages.

## running

```bash
make install              # installs deps + Chromium
make test                 # full hermetic run
make test-headed          # watch the browser
make serve                # just the SPA on http://127.0.0.1:5173
make serve-report         # last allure report
```
