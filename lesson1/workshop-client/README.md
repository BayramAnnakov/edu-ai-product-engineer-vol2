# Optional instructor-hosted classroom client

This client is not needed for the standalone bakeoff skill or offline examples. It reconnects to the Lead Scout simulation only when the instructor supplies a reachable host/code. No public host is bundled.

```bash
python3 learner.py --host http://INSTRUCTOR:8766 init
python3 learner.py --host http://INSTRUCTOR:8766 baseline
python3 learner.py --host http://INSTRUCTOR:8766 free-wins
# Edit the generated prediction.json and one condition in policy.json.
python3 learner.py --host http://INSTRUCTOR:8766 run --effort fixed
python3 learner.py --host http://INSTRUCTOR:8766 run --effort adaptive
python3 learner.py --host http://INSTRUCTOR:8766 url
```

Finish dev rejection, review, owner decision and export in the notebook UI. For continuing candidates only, preflight/freeze and S1 once are available through the client. Set W1_ROOM_CODE locally if provided. Keep the cookie jar and notebook URL private; do not commit them.
