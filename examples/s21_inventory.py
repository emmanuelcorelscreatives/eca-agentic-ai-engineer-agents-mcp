"""Stage 21 deterministic business tools. This module performs no model/network calls."""
import json
import re
from pathlib import Path
CATALOG = Path(__file__).resolve().parents[1] / 'data/s21_catalog.json'

def load_catalog():
    return json.loads(CATALOG.read_text())

def lookup_stock(sku: str) -> dict:
    """Look up a synthetic Academy product by exact SKU; never manufacture stock."""
    if not isinstance(sku, str) or not re.fullmatch(r'ECA-[A-Z]+-\d{2}', sku):
        return {'ok': False, 'error': 'invalid_sku'}
    for product in load_catalog()['products']:
        if product['sku'] == sku:
            return {'ok': True, 'product': product}
    return {'ok': False, 'error': 'unknown_sku', 'sku': sku}

def estimate_delivery(postcode: str, sku: str) -> dict:
    """Estimate business days for synthetic AB/CD postcodes, only for in-stock products."""
    product = lookup_stock(sku)
    if not product['ok']:
        return product
    if not isinstance(postcode, str) or not re.fullmatch(r'[A-Z]{2}\d{2}', postcode):
        return {'ok': False, 'error': 'invalid_postcode'}
    zones = load_catalog()['delivery_zones']
    if postcode[:2] not in zones:
        return {'ok': False, 'error': 'unsupported_zone'}
    if not product['product']['stock']:
        return {'ok': False, 'error': 'out_of_stock'}
    return {'ok': True, 'business_days': zones[postcode[:2]], 'sku': sku}

def summarize_events(events):
    """Read real ADK Event objects; intermediate text is not a final response."""
    result = {'event_ids': [], 'calls': [], 'responses': [], 'final_text': []}
    for event in events:
        result['event_ids'].append(event.id)
        for part in getattr(getattr(event, 'content', None), 'parts', None) or []:
            if getattr(part, 'function_call', None):
                call = part.function_call
                result['calls'].append({'id': call.id, 'name': call.name, 'args': call.args})
            if getattr(part, 'function_response', None):
                response = part.function_response
                result['responses'].append({'id': response.id, 'name': response.name, 'response': response.response})
            if event.is_final_response() and getattr(part, 'text', None):
                result['final_text'].append(part.text)
    return result
