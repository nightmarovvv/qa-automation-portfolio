from d42 import schema

# What the backend sends on 4xx / 5xx — used both for asserting the contract
# and for fabricating realistic error payloads in mocks.
ErrorResponseSchema = schema.dict({
    "message": schema.str.len(1, 500),
})
