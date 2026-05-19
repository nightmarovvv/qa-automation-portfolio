# Shared base schemas. Each constraint cites where the bound came from
# (HTML attr, regex from validator, API behavior). Don't use bare
# schema.str / schema.int — they accept "" and 0 which flakes the suite.

from d42 import schema

# 26-char Crockford ULID
ValidIDSchema = schema.str.regex(r"^[0-9A-HJKMNP-TV-Z]{26}$")

# Task title: trim, 3..120 chars (see onSubmit in app/app.js).
# Lower bound is in the pattern because d42 disallows .regex() + .len().
ValidTaskTitleSchema = schema.str.regex(r"^[A-Za-z0-9][A-Za-z0-9 _-]{2,118}[A-Za-z0-9]$")

# maxlength=2000 from the HTML attribute
ValidTaskDescriptionSchema = schema.str.len(0, 2000)

# Match the <select> options. Keep in sync with dicts.TaskStatus.
ValidTaskStatusSchema = schema.str.regex(r"^(todo|in_progress|done)$")

# Tag slugs the picker offers (see TAGS in app/app.js).
ValidTagSchema = schema.str.regex(r"^(frontend|backend|infra|bug|research)$")

# ISO 8601 timestamp
ValidTimestampSchema = schema.str.regex(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,6})?Z$"
)
