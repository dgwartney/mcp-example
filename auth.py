# 1. Create a custom validation middleware
class ApiKeyMiddleware(Middleware):
    async def on_request(self, context: MiddlewareContext, call_next):
        # 2. Extract headers from the current HTTP request
        headers = get_http_headers()
        api_key = headers.get("X-API-Key")
        
        # 3. Verify the key (use environment variables in production)
        if api_key != "your-secret-api-key":
            # 4. Block access if verification fails
            raise ToolError("Unauthorized: Invalid or missing API Key")
        
        # Continue to the tool if valid
        return await call_next(context)