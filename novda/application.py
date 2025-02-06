import asyncio

async def app(scope, receive, send):
    if scope['type'] == 'http':
        request_body = await receive()
        body = request_body.get('body')
        # Check if the request method is POST
        if scope['method'] == 'POST':
            # Read the body of the POST request
            request_body = await receive()
            body = request_body.get('body')
            print("Received POST data:", body.decode())  # Decode to string if it's in bytes

            # Send a response
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [
                    [b'content-type', b'text/html'],
                ]
            })
            await send({
                'type': 'http.response.body',
                'body': b'<h1>Received POST data!</h1>',
            })
        else:
            # If it's not a POST request, return a default response
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [
                    [b'content-type', b'text/html'],
                ]
            })
            await send({
                'type': 'http.response.body',
                'body': b'<h1>Method Not Allowed</h1>',
            })

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
print(randint(1,2))