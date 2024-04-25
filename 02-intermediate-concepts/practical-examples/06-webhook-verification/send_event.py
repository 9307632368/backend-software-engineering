"""Run the API first; this sends a signed demo webhook to localhost."""
import hashlib,hmac,json,os
import httpx

secret=os.getenv('WEBHOOK_SECRET','local-test-secret')
body=json.dumps({'type':'order.created','resource_id':'order-17'},separators=(',',':')).encode()
headers={
    'x-event-id':'event-demo-17',
    'x-signature':'sha256='+hmac.new(secret.encode(),body,hashlib.sha256).hexdigest(),
    'content-type':'application/json',
}
if __name__=='__main__':
    result=httpx.post('http://127.0.0.1:8000/webhooks/events',content=body,headers=headers,timeout=5)
    print(result.status_code,result.text)
