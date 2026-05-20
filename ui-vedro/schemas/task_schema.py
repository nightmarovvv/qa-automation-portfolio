from d42 import schema

from schemas import (
    ValidIDSchema,
    ValidTagSchema,
    ValidTaskDescriptionSchema,
    ValidTaskStatusSchema,
    ValidTaskTitleSchema,
    ValidTimestampSchema,
)

# A single task, both as returned by GET /tasks and as POST /tasks responds.
TaskSchema = schema.dict({
    "id": ValidIDSchema,
    "title": ValidTaskTitleSchema,
    "description": ValidTaskDescriptionSchema,
    "status": ValidTaskStatusSchema,
    "tags": schema.list(ValidTagSchema).len(0, 5),
    "created_at": ValidTimestampSchema,
    "updated_at": ValidTimestampSchema,
})

# Body shape sent by the SPA when creating a task. The id is server-assigned,
# so it's absent here. Same for timestamps.
CreateTaskRequestSchema = schema.dict({
    "title": ValidTaskTitleSchema,
    "description": ValidTaskDescriptionSchema,
    "status": ValidTaskStatusSchema,
    "tags": schema.list(ValidTagSchema).len(0, 5),
})

# Editing reuses the same body. If the API later splits the contract
# (partial updates, optional fields), this is where it diverges.
UpdateTaskRequestSchema = CreateTaskRequestSchema
