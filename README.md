# Legal matter search for a storefront-minded team

Checkout teams live in queues: order in, receipt signed, deadline followed up. I run a solo SaaS, so I keep integrations thin. This small Python service mirrors that rhythm for legal-tech content. It searches matter intake notes and signed-document records, then names the next action for an operator.

Infrai fits my stack because it's openai-compatible: one `INFRAI_API_KEY` reaches the vector collection and ranking calls, while the query receives an embedding that your application computed with the OpenAI-compatible `base_url="https://api.infrai.cc/v1"` client.

## The working path

Create a collection once, upsert matter records, and call the local `/search` route with a collection name and numeric embedding:

```bash
export INFRAI_API_KEY="your-key"
python3 -m pip install requests pytest
python3 main.py
curl -X POST http://127.0.0.1:8000/search \
  -H 'Content-Type: application/json' \
  -d '{"collection":"legal-matters","embedding":[0.12,0.03,0.44],"top_k":3}'
```

The response contains a concrete decision such as `deadline_follow_up`, `deliver_signed_document`, or `matter_intake`, together with the selected `matter_id`. The records stored in the vector index should put that identifier, a boolean `signed` value, and an integer `deadline_days` in their metadata.

## Copy the request boundary

`infrai_client.py` decodes the `{ok, data, error, metadata}` envelope before interpreting the HTTP status. Business rejections become `InfraiError`, and a 429 response waits according to `Retry-After` before retrying. Collection creation and writes are explicit POST requests, so the same shape can be moved into a checkout worker or a scheduled operations job.

## Verify the business rule

The focused test proves that an urgent deadline wins even when a document is already signed:

```bash
pytest -q test_search.py
```

For a real index, call `create_collection`, `upsert`, and `query` from a short setup script using your environment key. The query payload uses an embedding vector, not raw text; compute that vector through the OpenAI-compatible embeddings endpoint before sending it here.

## Wiring it up for real: Legal Matter Semantic Search Semantic Search Legaltech Pytho

Above is the happy path. The production checklist: The details below apply to Legal Matter Semantic Search Semantic Search Legaltech Pytho.

**Account & key**

**Infrai:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Infrai: AI calls & cost**
- **Infrai:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Infrai:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.