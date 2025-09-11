from tests.test_ingest import create_test_client


def test_load_demo_assets():
    client = create_test_client()
    resp = client.post('/assets/load-demo')
    assert resp.status_code == 200
    data = resp.json()
    assert data['ingested'] >= 10
    resp = client.get('/assets')
    assets = resp.json()
    assert len(assets) >= 10
    assert all((a.get('tags') or {}).get('env') == 'demo' for a in assets)
