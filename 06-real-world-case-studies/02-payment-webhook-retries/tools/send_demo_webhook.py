"""Send a signed fake webhook to a locally running service, never a real processor."""
import hashlib
import hmac
import json
import os
import time
import httpx


def main():
    secret=os.getenv("WEBHOOK_SECRET","local-demo-only-webhook-secret")
    endpoint=os.getenv("WEBHOOK_URL","http://127.0.0.1:8000/webhooks/payment")
    event={"event_id":"evt_demo_001","payment_id":"pay_demo_001",
           "type":"payment.succeeded","amount_cents":1299}
    body=json.dumps(event,separators=(",",":")).encode()
    timestamp=int(time.time())
    signature=hmac.new(secret.encode(),str(timestamp).encode()+b"."+body,hashlib.sha256).hexdigest()
    result=httpx.post(endpoint,content=body,headers={
        "Content-Type":"application/json",
        "X-Webhook-Timestamp":str(timestamp),
        "X-Webhook-Signature":signature},timeout=5)
    print(result.status_code,result.text)


if __name__=="__main__":main()
