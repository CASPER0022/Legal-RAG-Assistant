import hashlib, json, os, redis

r = redis.Redis(host=os.getenv("REDIS_HOST","localhost"), port=6379, decode_responses=True)
TTL = 7200  # seconds = 2 hours

def _key(prefix, payload):
    s = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return f"{prefix}:{hashlib.sha256(s.encode()).hexdigest()}"

def get_or_set(prefix, payload, compute_fn):
    k = _key(prefix, payload)
    v = r.get(k)
    if v: return json.loads(v)
    out = compute_fn()
    r.setex(k, TTL, json.dumps(out, ensure_ascii=False))
    return out
