from d42 import schema

from schemas.task_schema import TaskSchema

# Response from GET /tasks. The SPA reads `data`; everything else is metadata
# the framework can rely on without coupling to a concrete count.
TasksListResponseSchema = schema.dict({
    "data": schema.list(TaskSchema).len(0, 100),
    "total": schema.int.min(0),
})
