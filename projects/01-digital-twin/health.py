"""Local deployment probes; readiness and authenticated visitor health are distinct."""
import argparse
import json
import urllib.request
import urllib.error

def readiness(base_url='http://127.0.0.1:7860'):
    try:
        with urllib.request.urlopen(base_url.rstrip('/')+'/',timeout=3) as response:
            if response.status!=200:raise ValueError('unexpected readiness status')
        return {'status':'listening','visitor_health':'not_checked'}
    except urllib.error.HTTPError as error:
        if error.code==401:return {'status':'listening_with_authentication','visitor_health':'not_checked'}
        raise

def check(base_url='http://127.0.0.1:7860'):
    request=urllib.request.Request(base_url.rstrip('/')+'/config',headers={'Accept':'application/json'})
    with urllib.request.urlopen(request,timeout=5) as response:payload=json.load(response)
    if not isinstance(payload,dict) or not payload.get('components'):raise ValueError('Gradio configuration is not healthy')
    return {'status':'ok','component_count':len(payload['components']),'visitor_health':'configuration_only'}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:7860');parser.add_argument('--readiness',action='store_true');args=parser.parse_args()
    print(json.dumps(readiness(args.url) if args.readiness else check(args.url)))
